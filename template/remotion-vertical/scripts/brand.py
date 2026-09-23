"""Sets the look of the video: a style, the brand's colors, fonts and logo.

Everything it does lands in src/brand.json, which the video reads. Nothing
else needs editing to rebrand.

    python scripts/brand.py                            # what the video looks like now
    python scripts/brand.py --list                     # the styles to start from
    python scripts/brand.py --compare                  # this video in every style -> preview/styles.jpg
    python scripts/brand.py --style clean

    python scripts/brand.py --import tokens.json       # a design system: JSON tokens, CSS, SCSS, Tailwind
    python scripts/brand.py --logo ~/Downloads/logo.svg --logo-placement corner
    python scripts/brand.py --accent "#0B5FFF" --accent2 "#FF7A00" --bg "#FFFFFF" --text "#0F1B2D"
    python scripts/brand.py --font "Montserrat" --body-font "Inter"   # any Google font
    python scripts/brand.py --font ~/fonts/BrandSans-Bold.woff2       # or the brand's own file
    python scripts/brand.py --captions pill --motion bouncy --transition depth

Never type a color in from a screenshot or a video frame: compression shifts
it. Take it from the brand manual, a design system or a clean logo export.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRAND = os.path.join(ROOT, "src", "brand.json")
FONTS_TS = os.path.join(ROOT, "src", "fonts.generated.ts")
PUBLIC_BRAND = os.path.join(ROOT, "public", "brand")

STYLES_JSON = os.path.join(ROOT, "src", "styles.json")
with open(STYLES_JSON, encoding="utf-8") as _handle:
    STYLES = json.load(_handle)
# Every style's fonts stay importable, so --compare can show them all.
STYLE_FONTS = list(dict.fromkeys(
    f for s in STYLES.values() for f in (s["font"]["heading"], s["font"]["body"])))

HEX = re.compile(r"#(?:[0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})\b")
FONT_EXT = (".woff2", ".woff", ".ttf", ".otf")
IMAGE_EXT = (".svg", ".png", ".webp", ".jpg", ".jpeg")


def say(message: str = "") -> None:
    print(f"  {message}")


# --------------------------------------------------------------------------- #
# brand.json

def load() -> dict:
    with open(BRAND, encoding="utf-8") as handle:
        return json.load(handle)


def save(brand: dict) -> None:
    with open(BRAND, "w", encoding="utf-8") as handle:
        json.dump(brand, handle, indent=2, ensure_ascii=False)
        handle.write("\n")


def normalize(color: str) -> str:
    color = color.strip()
    if not color.startswith("#"):
        color = "#" + color
    if not HEX.fullmatch(color):
        sys.exit(f"\n  Not a hex color: {color}  (expected something like #0B5FFF)\n")
    if len(color) == 4:
        color = "#" + "".join(c * 2 for c in color[1:])
    return color[:7].upper()


# --------------------------------------------------------------------------- #
# color maths, mirrored from src/theme.ts so the report matches the render

def luminance(color: str) -> float:
    r, g, b = (int(color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in (r, g, b)]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((luminance(a), luminance(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def effective_colors(brand: dict) -> dict:
    style = STYLES.get(brand.get("style", "bold"), STYLES["bold"])
    base = {k: style["color"][k] for k in ("bg", "text", "accent", "accent2")}
    own = {k: v for k, v in (brand.get("colors") or {}).items() if v}
    if own.get("accent") and not own.get("accent2"):
        own["accent2"] = own["accent"]  # as theme.ts does
    base.update(own)
    return base


def check(brand: dict) -> list[str]:
    """Problems a viewer would actually see."""
    c = effective_colors(brand)
    problems = []
    ratio = contrast(c["text"], c["bg"])
    if ratio < 4.5:
        problems.append(f"text on background is {ratio:.1f}:1 — under 4.5:1, hard to read on a phone")
    for key in ("accent", "accent2"):
        r = contrast(c[key], c["bg"])
        if r < 1.8:
            problems.append(f"{key} {c[key]} almost disappears on the background ({r:.1f}:1)")
    logo = brand.get("logo")
    if logo and not os.path.exists(os.path.join(ROOT, "public", logo)):
        problems.append(f"logo file public/{logo} does not exist")
    return problems


# --------------------------------------------------------------------------- #
# fonts

def google_font_index() -> dict[str, str]:
    """{"Playfair Display": "PlayfairDisplay", ...} from the installed package."""
    folder = ROOT
    while True:
        index = os.path.join(folder, "node_modules", "@remotion", "google-fonts",
                             "dist", "esm", "index.mjs")
        if os.path.exists(index):
            break
        parent = os.path.dirname(folder)
        if parent == folder:
            return {}
        folder = parent
    with open(index, encoding="utf-8") as handle:
        text = handle.read()
    pairs = re.findall(r"fontFamily:\s*'([^']+)',\s*importName:\s*'([^']+)'", text)
    return dict(pairs)


def resolve_font(value: str) -> str:
    """A Google family name, or a font file copied into public/brand/fonts."""
    path = os.path.expanduser(value)
    if value.lower().endswith(FONT_EXT):
        if not os.path.exists(path):
            sys.exit(f"\n  No font file at {path}\n")
        dest = os.path.join(PUBLIC_BRAND, "fonts")
        os.makedirs(dest, exist_ok=True)
        shutil.copy2(path, os.path.join(dest, os.path.basename(path)))
        return f"file:brand/fonts/{os.path.basename(path)}"

    index = google_font_index()
    if not index:
        say("Can't find @remotion/google-fonts to check the name — install first.")
        return value
    if value in index:
        return value
    match = {k.lower(): k for k in index}.get(value.lower())
    if match:
        return match
    close = [k for k in index if value.lower().replace(" ", "") in k.lower().replace(" ", "")]
    hint = f" Close: {', '.join(close[:6])}." if close else ""
    sys.exit(f"\n  '{value}' is not a Google font.{hint}\n"
             "  For the brand's own font, pass the .woff2/.ttf/.otf file instead.\n")


def write_font_registry(brand: dict) -> None:
    index = google_font_index()
    wanted = list(STYLE_FONTS)
    for key in ("heading", "body"):
        name = (brand.get("fonts") or {}).get(key)
        if name and not name.startswith("file:") and name not in wanted and name in index:
            wanted.append(name)
    lines = [
        "// Written by scripts/brand.py — do not edit by hand.",
        "// The Google fonts this project can load: the five the styles use, plus any",
        "// the brand asked for. Importing one costs nothing; only the fonts theme.ts",
        "// actually loads are downloaded.",
    ]
    for i, name in enumerate(wanted):
        module = index.get(name, name.replace(" ", ""))
        lines.append(f'import * as F{i} from "@remotion/google-fonts/{module}";')
    lines += ["", "export const GOOGLE_FONTS: Record<string, unknown> = {"]
    lines += [f'  "{name}": F{i},' for i, name in enumerate(wanted)]
    lines += ["};", ""]
    with open(FONTS_TS, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


# --------------------------------------------------------------------------- #
# design system import

ROLES = [
    # (brand.json key, name patterns in priority order)
    ("accent", [r"\bprimary\b", r"brand", r"\baccent\b", r"\bmain\b", r"primary"]),
    ("bg", [r"^background$", r"\bbackground\b", r"\bbg\b", r"canvas", r"\bpaper\b", r"surface"]),
    ("text", [r"^text$", r"\btext\b", r"foreground", r"\bfg\b", r"\bink\b", r"on-?background", r"body"]),
    ("accent2", [r"secondary", r"highlight", r"accent", r"tertiary"]),
]
# Shade suffixes a scale uses; the base shade is the one to pick.
SHADE = re.compile(r"(?:^|[-_. /])(50|[1-9]00|950|light(?:er|est)?|dark(?:er|est)?|subtle|muted|hover|active|disabled)$")


def walk_json(node, path: list[str], colors: list, fonts: list) -> None:
    if isinstance(node, dict):
        value = node.get("$value", node.get("value"))
        if isinstance(value, str) and not isinstance(value, dict):
            walk_json(value, path, colors, fonts)
            return
        for key, child in node.items():
            if not key.startswith("$"):
                walk_json(child, path + [key], colors, fonts)
    elif isinstance(node, list):
        for i, child in enumerate(node):
            walk_json(child, path + [str(i)], colors, fonts)
    elif isinstance(node, str):
        name = "-".join(path).lower()
        if HEX.fullmatch(node.strip()):
            colors.append((name, node.strip()))
        elif "font" in name and ("family" in name or name.endswith("font")):
            fonts.append((name, node))


def scan_text(text: str, colors: list, fonts: list) -> None:
    for name, value in re.findall(
            r"""(?:--|\$|@)?([\w.-]+)["']?\s*[:=]\s*["']?(#[0-9a-fA-F]{3,8})\b""", text):
        colors.append((name.lower(), value))
    for name, value in re.findall(
            r"""(?:--|\$|@)?([\w.-]*font[\w.-]*)["']?\s*[:=]\s*([^;\n}]+)""", text, re.I):
        fonts.append((name.lower(), value))


def first_family(value: str) -> str:
    if isinstance(value, list):
        value = value[0] if value else ""
    return str(value).split(",")[0].strip().strip("'\"[]")


def import_design_system(path: str, brand: dict) -> None:
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        sys.exit(f"\n  No file at {path}\n")
    with open(path, encoding="utf-8", errors="replace") as handle:
        text = handle.read()

    colors: list[tuple[str, str]] = []
    fonts: list[tuple[str, str]] = []
    try:
        walk_json(json.loads(text), [], colors, fonts)
    except ValueError:
        scan_text(text, colors, fonts)
    if not colors and not fonts:
        sys.exit(f"\n  Found no colors or fonts in {path}.\n")

    say(f"Found {len(colors)} colors and {len(fonts)} font settings in {os.path.basename(path)}.")
    chosen: dict[str, str] = {}
    taken: set[str] = set()
    for key, patterns in ROLES:
        for pattern in patterns:
            # The two accents must differ; text may well share a color with one.
            hits = [(n, v) for n, v in colors if re.search(pattern, n)
                    and not (key.startswith("accent") and normalize(v) in taken)]
            base = [h for h in hits if not SHADE.search(h[0])]
            pick = (base or [h for h in hits if re.search(r"(500|600)$", h[0])] or hits)
            if pick:
                chosen[key] = normalize(pick[0][1])
                if key.startswith("accent"):
                    taken.add(chosen[key])
                say(f"  {key:<8} {chosen[key]}   from '{pick[0][0]}'")
                break

    brand.setdefault("colors", {}).update(chosen)
    missing = [k for k, _ in ROLES if k not in chosen]
    if missing:
        say(f"  Not identified: {', '.join(missing)} — the style's own stays.")

    families = [(n, first_family(v)) for n, v in fonts if first_family(v)]
    index = google_font_index()
    for key, pattern in (("heading", r"head|display|title"), ("body", r"body|base|sans|text")):
        hit = next((f for n, f in families if re.search(pattern, n)), None)
        hit = hit or (families[0][1] if families else None)
        if not hit:
            continue
        if hit in index:
            brand.setdefault("fonts", {})[key] = hit
            say(f"  {key + ' font':<13} {hit}")
        else:
            say(f"  {key + ' font':<13} {hit} is not on Google Fonts — pass the font file "
                f"with --font / --body-font to use it.")

    say("")
    say("Every color found, so a wrong guess is easy to fix with --accent/--bg/...:")
    for name, value in colors[:40]:
        say(f"    {normalize(value)}  {name}")
    if len(colors) > 40:
        say(f"    ... and {len(colors) - 40} more")


# --------------------------------------------------------------------------- #
# logo

def logo_colors(path: str) -> list[str]:
    """The dominant non-background colors of a raster logo, as suggestions."""
    try:
        from PIL import Image
    except ImportError:
        return []
    img = Image.open(path).convert("RGBA")
    img.thumbnail((200, 200))
    # Pixels are grouped into coarse buckets to find the dominant colors, then
    # each bucket reports the average of its real pixels, not its corner.
    buckets: dict[tuple, list[int]] = {}
    data = img.tobytes()
    for i in range(0, len(data), 4):
        r, g, b, a = data[i:i + 4]
        if a < 200:
            continue
        spread = max(r, g, b) - min(r, g, b)
        if spread < 24 and (max(r, g, b) > 235 or max(r, g, b) < 20):
            continue  # white or black: background or type, rarely the brand color
        acc = buckets.setdefault((r // 24, g // 24, b // 24), [0, 0, 0, 0])
        acc[0] += r
        acc[1] += g
        acc[2] += b
        acc[3] += 1
    ranked = sorted(buckets.values(), key=lambda acc: -acc[3])
    return ["#%02X%02X%02X" % tuple(round(c / acc[3]) for c in acc[:3]) for acc in ranked[:4]]


def set_logo(path: str, brand: dict) -> None:
    path = os.path.expanduser(path)
    if not os.path.exists(path):
        sys.exit(f"\n  No file at {path}\n")
    ext = os.path.splitext(path)[1].lower()
    if ext not in IMAGE_EXT:
        sys.exit(f"\n  A logo should be {', '.join(IMAGE_EXT)} — got {ext}.\n")
    os.makedirs(PUBLIC_BRAND, exist_ok=True)
    dest = os.path.join(PUBLIC_BRAND, "logo" + ext)
    shutil.copy2(path, dest)
    brand["logo"] = f"brand/logo{ext}"
    say(f"Logo copied to public/brand/logo{ext}")
    if ext in (".jpg", ".jpeg"):
        say("  A JPG has no transparency: it will show as a rectangle. SVG or PNG is better.")
    if ext != ".svg":
        suggested = logo_colors(dest)
        if suggested:
            say(f"  Colors in the logo: {', '.join(suggested)}")
            say("  Use them only if the brand manual agrees — e.g.  --accent " + suggested[0])


# --------------------------------------------------------------------------- #
# compare

def compare(browser: str | None) -> None:
    npx = shutil.which("npx")
    if not npx:
        sys.exit("\n  npx not found — Node is not installed or not on the PATH.\n")
    try:
        with open(os.path.join(ROOT, "src", "timings.json"), encoding="utf-8") as handle:
            scenes = json.load(handle).get("scenes", [])
        frame = max(int(scenes[0]["frames"] * 0.6), 20) if scenes else 60
    except (OSError, ValueError, KeyError, IndexError):
        frame = 60

    out_dir = os.path.join(ROOT, "preview", "styles")
    os.makedirs(out_dir, exist_ok=True)
    bundle = os.path.join(ROOT, "preview", "bundle")
    say("Bundling once...")
    subprocess.run([npx, "remotion", "bundle", os.path.join("src", "index.ts"),
                    "--out-dir", bundle, "--log=error"], cwd=ROOT, check=True)

    extra = [f"--browser-executable={browser}"] if browser else []
    shots = [("yours", None)] + [(name, name) for name in STYLES]
    files = []
    for label, style in shots:
        out = os.path.join(out_dir, f"{label}.png")
        props = ["--props", json.dumps({"style": style})] if style else []
        say(f"  {label}")
        result = subprocess.run(
            [npx, "remotion", "still", bundle, "Short", out, f"--frame={frame}",
             "--scale=0.4", "--log=error", *props, *extra],
            cwd=ROOT, capture_output=True, text=True)
        if result.returncode != 0 or not os.path.exists(out):
            say(f"    failed: {(result.stderr or result.stdout).strip()[-300:]}")
            continue
        files.append((label, out))

    if not files:
        sys.exit("\n  No preview could be rendered.\n")
    sheet = os.path.join(ROOT, "preview", "styles.jpg")
    try:
        from PIL import Image, ImageDraw, ImageFont
        try:
            label_font = ImageFont.load_default(size=26)
        except TypeError:  # Pillow < 10.1
            label_font = ImageFont.load_default()
        images = [Image.open(f).convert("RGB") for _, f in files]
        w, h = images[0].size
        pad, band = 16, 44
        canvas = Image.new("RGB", (len(images) * (w + pad) + pad, h + band + pad), "#FFFFFF")
        draw = ImageDraw.Draw(canvas)
        for i, ((label, _), img) in enumerate(zip(files, images)):
            x = pad + i * (w + pad)
            canvas.paste(img, (x, band))
            draw.text((x, 8), label.upper(), fill="#111111", font=label_font)
        canvas.save(sheet, quality=88)
    except ImportError:
        sheet = out_dir
    say("")
    say(f"Side by side: {sheet}")
    say("'yours' is brand.json as it is now; the others are each style untouched.")
    say("Pick one with --style, then override colors, fonts and logo on top.")


# --------------------------------------------------------------------------- #

def report(brand: dict) -> None:
    style = brand.get("style", "bold")
    c = effective_colors(brand)
    fonts = brand.get("fonts") or {}
    say(f"Style        {style}  — {STYLES.get(style, STYLES['bold'])['looksLike']}")
    for key in ("bg", "text", "accent", "accent2"):
        own = (brand.get("colors") or {}).get(key)
        derived = key == "accent2" and (brand.get("colors") or {}).get("accent")
        say(f"{key:<12} {c[key]}  {'(brand)' if own or derived else '(style)'}")
    own_font = STYLES.get(style, STYLES["bold"])["font"]
    say(f"Heading font {fonts.get('heading') or own_font['heading'] + ' (style)'}")
    say(f"Body font    {fonts.get('body') or own_font['body'] + ' (style)'}")
    say(f"Logo         {brand.get('logo') or '—'}"
        + (f"  [{brand.get('logoPlacement', 'corner')}]" if brand.get("logo") else ""))
    for key in ("captions", "motion", "transition", "background", "radius"):
        if brand.get(key) is not None:
            say(f"{key.capitalize():<12} {brand[key]}")
    problems = check(brand)
    if problems:
        say("")
        for problem in problems:
            say(f"! {problem}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--list", action="store_true", help="show the styles")
    parser.add_argument("--style", choices=list(STYLES))
    parser.add_argument("--import", dest="import_path", metavar="FILE",
                        help="design tokens (JSON), CSS/SCSS variables or a Tailwind config")
    parser.add_argument("--logo", metavar="FILE")
    parser.add_argument("--logo-placement", choices=["corner", "end", "both", "none"])
    for key in ("bg", "text", "accent", "accent2"):
        parser.add_argument(f"--{key}", metavar="HEX")
    parser.add_argument("--caption-color", metavar="HEX", help="the highlighted caption word")
    parser.add_argument("--font", metavar="NAME_OR_FILE", help="headings (and body, unless --body-font)")
    parser.add_argument("--body-font", metavar="NAME_OR_FILE")
    parser.add_argument("--uppercase", choices=["yes", "no"], help="uppercase headlines")
    parser.add_argument("--captions", choices=["stroke", "box", "pill"])
    parser.add_argument("--motion", choices=["snappy", "calm", "bouncy"])
    parser.add_argument("--transition", choices=["cut", "depth"])
    parser.add_argument("--background", choices=["gradient", "solid"])
    parser.add_argument("--radius", type=int, help="corner roundness in px, 0 = square")
    parser.add_argument("--reset", action="store_true", help="drop every override, keep the style")
    parser.add_argument("--compare", action="store_true",
                        help="render this video in every style, side by side")
    parser.add_argument("--browser-executable", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.list:
        print()
        for name, style in STYLES.items():
            say(f"{name:<10} {style['looksLike']}  [{style['font']['heading']}]")
        print()
        return

    brand = load()
    changed = False
    print()

    if args.reset:
        brand = {k: v for k, v in brand.items() if k in ("_help", "style")}
        brand.update({"colors": {}, "fonts": {}, "logo": None, "logoPlacement": "corner"})
        changed = True
    if args.style:
        brand["style"] = args.style
        changed = True
    if args.import_path:
        import_design_system(args.import_path, brand)
        changed = True
    if args.logo:
        set_logo(args.logo, brand)
        changed = True
    if args.logo_placement:
        brand["logoPlacement"] = args.logo_placement
        changed = True
    for key in ("bg", "text", "accent", "accent2"):
        value = getattr(args, key)
        if value:
            brand.setdefault("colors", {})[key] = normalize(value)
            changed = True
    if args.caption_color:
        brand.setdefault("colors", {})["captionActive"] = normalize(args.caption_color)
        changed = True
    if args.font:
        family = resolve_font(args.font)
        brand.setdefault("fonts", {})["heading"] = family
        if not args.body_font:
            brand["fonts"]["body"] = family
        changed = True
    if args.body_font:
        brand.setdefault("fonts", {})["body"] = resolve_font(args.body_font)
        changed = True
    if args.uppercase:
        brand.setdefault("fonts", {})["uppercaseHeadings"] = args.uppercase == "yes"
        changed = True
    for key in ("captions", "motion", "transition", "background", "radius"):
        value = getattr(args, key)
        if value is not None:
            brand[key] = value
            changed = True

    if changed:
        save(brand)
        write_font_registry(brand)
        say("Saved src/brand.json. The studio updates by itself.")
        print()

    report(brand)
    print()

    if args.compare:
        compare(args.browser_executable)
        print()


if __name__ == "__main__":
    main()
