"""Checks the machine has what the kit needs, and installs what it can.

    python scripts/doctor.py             # report only
    python scripts/doctor.py --install   # install the Python pieces too

Node and FFmpeg are not installed for you: they are system packages, and
silently installing those on someone's machine is not a decision a script
should make. The report tells you the exact command for your platform.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
import urllib.error
import urllib.request

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

VOICESTUDIO_URL = os.environ.get("VOICESTUDIO_URL", "http://localhost:3900")

INSTALL_HINTS = {
    "node": {
        "Windows": "winget install OpenJS.NodeJS.LTS",
        "Darwin": "brew install node",
        "Linux": "see https://nodejs.org (or your package manager)",
    },
    "ffmpeg": {
        "Windows": "winget install Gyan.FFmpeg",
        "Darwin": "brew install ffmpeg",
        "Linux": "sudo apt install ffmpeg",
    },
}

PIP_PACKAGES = {
    "edge_tts": ("edge-tts", "free fallback voice engine"),
    "faster_whisper": ("faster-whisper", "word-level captions"),
    "yt_dlp": ("yt-dlp", "downloading source and reference footage"),
}


def has_command(name: str) -> str | None:
    return shutil.which(name)


def has_module(name: str) -> bool:
    try:
        __import__(name)
        return True
    except ImportError:
        return False


def voicestudio_up() -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(
            f"{VOICESTUDIO_URL}/v1/audio/voices", timeout=4,
        ) as response:
            data = json.load(response)
        count = len(data.get("data", data)) if isinstance(data, (dict, list)) else 0
        return True, f"{count} voices"
    except urllib.error.URLError:
        return False, "not running"
    except Exception as err:  # reachable but answering something unexpected
        return True, f"reachable ({err})"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--install", action="store_true",
                        help="pip install the missing Python packages")
    args = parser.parse_args()

    system = platform.system()
    problems: list[str] = []

    print("\n  Required\n  " + "-" * 44)
    for command in ("node", "npm", "ffmpeg", "ffprobe"):
        path = has_command(command)
        print(f"  {command:<16} {'ok' if path else 'MISSING'}")
        if not path:
            key = "node" if command in ("node", "npm") else "ffmpeg"
            hint = INSTALL_HINTS[key].get(system, INSTALL_HINTS[key]["Linux"])
            problems.append(f"{command} — install with:  {hint}")

    print("\n  Python packages\n  " + "-" * 44)
    for module, (package, why) in PIP_PACKAGES.items():
        present = has_module(module)
        print(f"  {package:<16} {'ok' if present else '-':<8} {why}")
        if not present and args.install:
            print(f"    installing {package}...")
            subprocess.run([sys.executable, "-m", "pip", "install", "-q", package])

    print("\n  Voice engines\n  " + "-" * 44)
    up, detail = voicestudio_up()
    print(f"  VoiceStudio      {'ok' if up else '-':<8} {detail} · {VOICESTUDIO_URL}")
    if not up:
        print("    Best quality and free. Install the desktop app from")
        print("    https://github.com/debpalash/VoiceStudio and leave it open,")
        print('    or set "engine": "edge" in script.json to work without it.')
    print(f"  edge-tts         {'ok' if has_module('edge_tts') else '-':<8} free fallback")
    for name, key in (("OpenAI", "OPENAI_API_KEY"), ("ElevenLabs", "ELEVENLABS_API_KEY")):
        print(f"  {name:<16} {'key set' if os.environ.get(key) else '-':<8} optional")

    if problems:
        print("\n  Fix these first\n  " + "-" * 44)
        for problem in problems:
            print(f"  · {problem}")
        print()
        sys.exit(1)

    print("\n  Ready.\n")


if __name__ == "__main__":
    main()
