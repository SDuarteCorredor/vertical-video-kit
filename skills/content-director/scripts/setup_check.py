"""Checks what content-director needs and prints the one command that installs what is missing.

    python setup_check.py
"""
from __future__ import annotations
import importlib.util, platform, shutil, sys

def has_mod(name: str) -> bool:
    return importlib.util.find_spec(name) is not None

def main() -> None:
    rows = [
        ("ffmpeg / ffprobe", bool(shutil.which("ffmpeg") and shutil.which("ffprobe")), "cutting frames, audio, cut detection"),
        ("yt-dlp", has_mod("yt_dlp") or bool(shutil.which("yt-dlp")), "downloading reels and their metadata"),
        ("faster-whisper", has_mod("faster_whisper"), "transcripts with timestamps"),
        ("Pillow", has_mod("PIL"), "frame sheets, palettes"),
    ]
    print("\n  content-director — setup\n  " + "-" * 44)
    for name, ok, why in rows:
        print(f"  {name:18s} {'ok' if ok else 'MISSING':8s} {why}")
    missing_py = [p for (n, ok, _), p in zip(rows, [None, "yt-dlp", "faster-whisper", "pillow"]) if not ok and p]
    if missing_py:
        print(f"\n  Install:  {sys.executable} -m pip install -U {' '.join(missing_py)}")
        print("  (If pip refuses with 'externally managed', create a venv first:"
              f" {sys.executable} -m venv .venv && .venv/bin/pip install {' '.join(missing_py)})")
    if not rows[0][1]:
        sysname = platform.system()
        cmd = {"Darwin": "brew install ffmpeg", "Windows": "winget install Gyan.FFmpeg"}.get(sysname, "sudo apt install ffmpeg")
        print(f"  Install:  {cmd}")
    if sys.version_info >= (3, 14) and not has_mod("faster_whisper"):
        print("  Note: faster-whisper may not install on Python 3.14+ (its 'av' dependency). Use Python 3.12 for the venv.")
    if all(ok for _, ok, _ in rows):
        print("\n  Ready.")

if __name__ == "__main__":
    main()
