"""Makes an upload-ready file from the master render.

Every platform re-encodes whatever you give it. That is why you render the
master at high quality and then hand over a file that is already in the shape
the encoder expects — H.264 High, yuv420p, AAC, moov atom at the front. A file
that needs remuxing before it can even start playing is the one that comes back
looking soft.

    python scripts/publish.py                       # output/video.mp4 -> upload/
    python scripts/publish.py output/other.mp4
    python scripts/publish.py --loudness -14        # louder, for music-led edits
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", nargs="?", default=os.path.join("output", "video.mp4"))
    parser.add_argument("--out", default=os.path.join("upload", "video.mp4"))
    parser.add_argument("--crf", type=int, default=20,
                        help="18-22 is the useful range; lower is bigger and sharper")
    parser.add_argument("--loudness", type=float, default=-16.0,
                        help="integrated LUFS target for the voice-over")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("\n  FFmpeg is missing.\n")

    source = args.source if os.path.isabs(args.source) else os.path.join(ROOT, args.source)
    if not os.path.exists(source):
        sys.exit(f"\n  No file at {source} — render first with:  npm run render\n")

    out = args.out if os.path.isabs(args.out) else os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out), exist_ok=True)

    subprocess.run([
        "ffmpeg", "-v", "error", "-stats", "-y", "-i", source,
        "-c:v", "libx264", "-profile:v", "high", "-level", "4.1",
        "-pix_fmt", "yuv420p", "-crf", str(args.crf), "-preset", "slow",
        # Speech sits well below music at the same peak level, so normalize to
        # a spoken-word target instead of trusting whatever the engine gave us.
        "-af", f"loudnorm=I={args.loudness}:TP=-1.5:LRA=11",
        "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
        "-movflags", "+faststart", out,
    ], check=True)

    size = os.path.getsize(out) / (1024 * 1024)
    print(f"\n  {out}   {size:.1f} MB\n")


if __name__ == "__main__":
    main()
