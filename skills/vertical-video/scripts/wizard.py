"""Makes a video by asking questions, for people who don't want a terminal.

Everything the wizard does can be done by hand — it just does it in order and
without leaving you to guess. You answer five things and it produces a finished
1080x1920 MP4.

    python skills/vertical-video/scripts/wizard.py
    python skills/vertical-video/scripts/wizard.py --name my-video --lang es

No AI agent is involved. If you want help writing the narration, paste a prompt
from docs/PROMPTS.md into any free chat assistant and bring the lines back here.
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

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

# Curated instead of complete: `python scripts/voice.py --list-voices` prints
# the full edge-tts catalogue, which is hundreds of rows and helps nobody
# choose. Accent matters more than most people expect — a video for Colombia
# narrated in Spanish from Spain sounds imported.
VOICES = [
    ("es-CO", "Colombia",     "es-CO-GonzaloNeural", "es-CO-SalomeNeural"),
    ("es-MX", "México",       "es-MX-JorgeNeural",   "es-MX-DaliaNeural"),
    ("es-AR", "Argentina",    "es-AR-TomasNeural",   "es-AR-ElenaNeural"),
    ("es-ES", "España",       "es-ES-AlvaroNeural",  "es-ES-ElviraNeural"),
    ("es-US", "US Spanish",   "es-US-AlonsoNeural",  "es-US-PalomaNeural"),
    ("en-US", "US English",   "en-US-AndrewNeural",  "en-US-AriaNeural"),
    ("en-GB", "UK English",   "en-GB-RyanNeural",    "en-GB-SoniaNeural"),
]


def ask(question: str, default: str = "") -> str:
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"  {question}{suffix}: ").strip()
    except (EOFError, KeyboardInterrupt):
        sys.exit("\n\n  Cancelled.\n")
    return answer or default


def yes(question: str, default: bool = True) -> bool:
    hint = "Y/n" if default else "y/N"
    answer = ask(f"{question} [{hint}]").lower()
    if not answer:
        return default
    return answer.startswith(("y", "s"))  # y/yes, s/sí


def rule(title: str) -> None:
    print(f"\n  {title}\n  " + "-" * 56)


def check_environment() -> None:
    rule("Checking the machine")
    missing = [c for c in ("node", "npm", "ffmpeg", "ffprobe") if not shutil.which(c)]
    if missing:
        print(f"  Missing: {', '.join(missing)}")
        print("\n  Run the setup script first:")
        print("    macOS / Linux   bash setup.sh")
        print("    Windows         powershell -ExecutionPolicy Bypass -File setup.ps1\n")
        sys.exit(1)
    try:
        __import__("edge_tts")
    except ImportError:
        print("  edge-tts is missing — it is the free voice engine.")
        if yes("  Install it now?"):
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", "edge-tts"],
                           check=False)
        else:
            sys.exit("\n  Nothing to generate the voice with. Stopping.\n")
    print("  Everything the kit needs is here.")


def pick_voice() -> tuple[str, str]:
    rule("Who narrates it")
    for index, (_, place, male, female) in enumerate(VOICES, 1):
        print(f"  {index}. {place:<14} {male.split('-')[-1][:-6]} / "
              f"{female.split('-')[-1][:-6]}")
    choice = ask("Pick a number", "1")
    try:
        code, _, male, female = VOICES[int(choice) - 1]
    except (ValueError, IndexError):
        code, _, male, female = VOICES[0]
    gender = ask("Voice — (m)ale or (f)emale", "f")
    voice = male if gender.lower().startswith("m") else female
    print(f"\n  Using {voice}")
    return code.split("-")[0], voice


def collect_lines() -> list[str]:
    rule("What is said out loud")
    print("""  One sentence per line — this is narration, so write it to be HEARD.
  Whole sentences, no bullet fragments, no acronyms you would not say aloud.

  The first line is your hook. It has about two seconds to make someone
  stop scrolling, so it should open a question in their head, not announce
  what the video is about.

  Press Enter on an empty line when you are done.
  Press Enter immediately to use the example script instead.
""")
    lines: list[str] = []
    while True:
        try:
            line = input(f"  {len(lines) + 1}. ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not line:
            break
        lines.append(line)
    return lines


def screen_text(line: str, words: int = 7) -> str:
    """A short on-screen version of a spoken line.

    Deliberately crude. Screen text and narration are different texts and the
    good version is written by a person — this is a placeholder that is at
    least the right length, so the layout is real while you rewrite it.
    """
    clean = re.sub(r"\[pause:[\d.]+\]", " ", line)
    clean = re.sub(r"\s+", " ", clean).strip().rstrip(".!?,;:")
    parts = clean.split(" ")
    cut = " ".join(parts[:words]) + ("…" if len(parts) > words else "")
    # This lands inside a double-quoted TypeScript string literal.
    return cut.replace("\\", "\\\\").replace('"', '\\"')


def scene_id(index: int, total: int) -> tuple[str, str]:
    if index == 0:
        return f"{index + 1:02d}-hook", "hook"
    if index == total - 1:
        return f"{index + 1:02d}-cta", "cta"
    return f"{index + 1:02d}-point", "point"


def write_project(target: str, lines: list[str], lang: str, voice: str) -> None:
    """Turn the collected lines into the two files content actually lives in."""
    total = len(lines)
    scenes, content = [], []

    for index, line in enumerate(lines):
        ident, kind = scene_id(index, total)
        scenes.append({"id": ident, "text": line})
        if kind == "hook":
            content.append(f'  {{\n    id: "{ident}",\n    type: "hook",\n'
                           f'    text: "{screen_text(line, 9)}",\n  }},')
        elif kind == "cta":
            content.append(f'  {{\n    id: "{ident}",\n    type: "cta",\n'
                           f'    text: "{screen_text(line)}",\n  }},')
        else:
            content.append(f'  {{\n    id: "{ident}",\n    type: "point",\n'
                           f'    title: "{screen_text(line)}",\n  }},')

    script_path = os.path.join(target, "script.json")
    with open(script_path, encoding="utf-8") as handle:
        script = json.load(handle)
    script.update({"engine": "edge", "voice": voice, "lang": lang,
                   "scenes": scenes})
    script.pop("_comment", None)
    with open(script_path, "w", encoding="utf-8") as handle:
        json.dump(script, handle, indent=2, ensure_ascii=False)
        handle.write("\n")

    content_path = os.path.join(target, "src", "content.ts")
    with open(content_path, encoding="utf-8") as handle:
        source = handle.read()
    # Everything above `export const SCENES` is the type definitions and the
    # comments explaining them — worth keeping, and not ours to rewrite.
    head = source.split("export const SCENES", 1)[0]
    with open(content_path, "w", encoding="utf-8") as handle:
        handle.write(head)
        handle.write("export const SCENES: Scene[] = [\n")
        handle.write("\n".join(content))
        handle.write("\n];\n")


STYLES = [
    ("bold", "dark, heavy type, high contrast — creator / TikTok"),
    ("clean", "light, airy, lots of white space — product, tips"),
    ("editorial", "serif headlines on warm paper — magazine, opinion"),
    ("playful", "saturated color, round shapes — consumer, events"),
    ("corporate", "white and navy, logo on screen — institutional, B2B"),
]


def pick_look() -> list[str]:
    """Asks for the look and returns the arguments for scripts/brand.py."""
    rule("The look")
    for i, (name, looks) in enumerate(STYLES, 1):
        print(f"  {i}. {name:<10} {looks}")
    choice = ask("Which style (number)", "1")
    try:
        style = STYLES[int(choice) - 1][0]
    except (ValueError, IndexError):
        style = "bold"
    brand = ["--style", style]

    print("\n  Your brand, if you have one. Press Enter to skip any of these.")
    logo = ask("Logo file (SVG or transparent PNG)", "").strip().strip('"')
    if logo:
        if os.path.exists(os.path.expanduser(logo)):
            where = ask("Logo: corner / end / both", "end").lower()
            brand += ["--logo", logo, "--logo-placement",
                      where if where in ("corner", "end", "both") else "end"]
        else:
            print(f"  No file at {logo} — skipping the logo.")
    main = ask("Main brand color, as a hex code like #0B5FFF", "").strip()
    if main:
        brand += ["--accent", main]
    font = ask("Brand font (a Google Fonts name)", "").strip()
    if font:
        brand += ["--font", font]
    return brand


def run(command: list[str], cwd: str) -> bool:
    print(f"\n  $ {' '.join(command)}")
    return subprocess.run(command, cwd=cwd, check=False).returncode == 0


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--name", help="skip the folder-name question")
    parser.add_argument("--lang", help="skip the voice question (es, en)")
    parser.add_argument("--render", action="store_true",
                        help="render without asking at the end")
    parser.add_argument("--no-studio", action="store_true",
                        help="don't open the live preview at the end")
    args = parser.parse_args()

    print("""
  vertical-video-kit
  Answer a few questions and you get a finished 1080x1920 video.
""")

    check_environment()

    rule("Where it goes")
    name = args.name or ask("Folder name for this video", "my-video")
    target = os.path.abspath(name)
    if os.path.exists(target):
        sys.exit(f"\n  {target} already exists. Pick another name.\n")

    lang, voice = pick_voice()
    if args.lang:
        lang = args.lang

    lines = collect_lines()
    look = pick_look()

    rule("Building the project")
    created = subprocess.run(
        [sys.executable, os.path.join(HERE, "new_project.py"), target,
         "--engine", "edge", "--voice", voice, "--lang", lang],
        check=False,
    )
    if created.returncode != 0 or not os.path.isdir(target):
        sys.exit("\n  Could not create the project.\n")

    if not run([sys.executable, os.path.join("scripts", "brand.py"), *look], target):
        print("  The look could not be applied — the video keeps the default style.")

    if lines:
        write_project(target, lines, lang, voice)
        print(f"  Wrote {len(lines)} scenes into script.json and src/content.ts")
    else:
        print("  Using the example script that ships with the template.")

    rule("Generating the voice")
    if not run([sys.executable, os.path.join("scripts", "voice.py")], target):
        sys.exit("\n  The voice step failed. Nothing else can run until it works.\n")

    rule("Generating the captions")
    if not run([sys.executable, os.path.join("scripts", "captions.py")], target):
        print("  Captions failed — the video still renders, just without them.")
        print("  Usually this means faster-whisper is missing:")
        print(f"    {sys.executable} -m pip install faster-whisper")

    rule("Done building")
    print(f"""  Your project is in  {target}

  The on-screen text is a rough cut of your narration — good enough to see the
  layout, not good enough to publish. Open src/content.ts and rewrite it: the
  screen carries fragments, the voice carries sentences.
""")

    if not args.no_studio:
        rule("Opening the preview")
        from studio import open_studio
        if not open_studio(target):
            print(f"\n  Start it yourself with:  cd {name} && npm run dev\n")

    npm = shutil.which("npm")
    if npm and (args.render or yes("  Render the video now? (a few minutes)")):
        rule("Rendering")
        if run([npm, "run", "render"], target):
            run([sys.executable, os.path.join("scripts", "publish.py")], target)
            print(f"""
  Finished.

    {os.path.join(target, 'output', 'video.mp4')}   master
    {os.path.join(target, 'upload', 'video.mp4')}   the one you upload
""")


if __name__ == "__main__":
    main()
