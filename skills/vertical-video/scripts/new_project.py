"""Creates a new vertical video project from the template.

    python scripts/new_project.py my-video
    python scripts/new_project.py my-video --engine edge --voice es-CO-SalomeNeural
    python scripts/new_project.py my-video --no-install

Copies the Remotion template and writes your engine and voice choice into
script.json. Inside the kit, every project shares one Remotion install at the
kit root (see deps.py); anywhere else, the project gets its own.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_URL = "https://github.com/SDuarteCorredor/vertical-video-kit"
TEMPLATE_SUBPATH = os.path.join("template", "remotion-vertical")


def find_template(explicit: str | None) -> str:
    """Look where the template could reasonably be, then fetch it as a last resort."""
    candidates = [explicit] if explicit else []
    candidates += [
        os.environ.get("VVK_TEMPLATE"),
        # repo layout: skills/vertical-video/scripts/ -> up three
        os.path.join(HERE, "..", "..", "..", TEMPLATE_SUBPATH),
        # skill installed on its own, kit cloned next to it
        os.path.join(HERE, "..", TEMPLATE_SUBPATH),
        os.path.join(os.getcwd(), TEMPLATE_SUBPATH),
    ]
    for candidate in candidates:
        if candidate and os.path.isdir(candidate):
            return os.path.abspath(candidate)

    if not shutil.which("git"):
        sys.exit("\n  Can't find the template and git is not installed.\n"
                 "  Clone the kit and pass --template <path>.\n")

    print("  Template not found locally — fetching the kit...")
    tmp = tempfile.mkdtemp(prefix="vvk-")
    subprocess.run(["git", "clone", "--depth", "1", REPO_URL, tmp],
                   check=True, capture_output=True)
    fetched = os.path.join(tmp, TEMPLATE_SUBPATH)
    if not os.path.isdir(fetched):
        sys.exit(f"\n  The fetched kit has no {TEMPLATE_SUBPATH}.\n")
    return fetched


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("name", help="folder to create")
    parser.add_argument("--engine", default=None,
                        choices=["voicestudio", "edge", "openai", "elevenlabs"])
    parser.add_argument("--voice", default=None)
    parser.add_argument("--lang", default=None, help="e.g. en, es")
    parser.add_argument("--style", default=None,
                        choices=["bold", "clean", "editorial", "playful", "corporate"],
                        help="the look to start from; scripts/brand.py changes it later")
    parser.add_argument("--template", default=None)
    parser.add_argument("--no-install", action="store_true")
    args = parser.parse_args()

    target = os.path.abspath(args.name)
    if os.path.exists(target):
        sys.exit(f"\n  {target} already exists. Pick another name.\n")

    template = find_template(args.template)
    shutil.copytree(
        template, target,
        ignore=shutil.ignore_patterns("node_modules", "audio", "output",
                                      "upload", "preview", "__pycache__"),
    )

    if args.engine or args.voice or args.lang:
        script_path = os.path.join(target, "script.json")
        with open(script_path, encoding="utf-8") as handle:
            script = json.load(handle)
        if args.engine:
            script["engine"] = args.engine
        if args.voice:
            script["voice"] = args.voice
        if args.lang:
            script["lang"] = args.lang
        with open(script_path, "w", encoding="utf-8") as handle:
            json.dump(script, handle, indent=2, ensure_ascii=False)

    if args.style:
        brand_path = os.path.join(target, "src", "brand.json")
        with open(brand_path, encoding="utf-8") as handle:
            brand = json.load(handle)
        brand["style"] = args.style
        with open(brand_path, "w", encoding="utf-8") as handle:
            json.dump(brand, handle, indent=2, ensure_ascii=False)
            handle.write("\n")

    print(f"\n  Created {target}")

    if not args.no_install:
        from deps import ensure_dependencies
        where = ensure_dependencies(target, say=lambda m: print(f"  {m}"))
        if where and os.path.abspath(where) != target:
            print(f"  Using the shared Remotion in {where}")

    print(f"""
  Next:

    cd {args.name}
    python scripts/brand.py --help   (the look: style, logo, colors, fonts)
    (write src/content.ts and script.json first — text before design)
    python scripts/voice.py
    python scripts/captions.py
    npm run dev
""")


if __name__ == "__main__":
    main()
