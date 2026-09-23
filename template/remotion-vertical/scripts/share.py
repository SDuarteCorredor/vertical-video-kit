"""Makes a light copy for email or WhatsApp, aiming at a target size.

The master is too heavy to attach. This brings the size down without wrecking
the on-screen text, which is the first thing to go when a video is compressed
too hard.

    python scripts/share.py                           # output/video.mp4 -> output/video_light.mp4
    python scripts/share.py output/other.mp4 --mb 15
    python scripts/share.py --mb 10 --allow-720       # drop to 720p if 1080p cannot get there
"""
from __future__ import annotations

import argparse
import math
import os
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Past this, captions and small text start to smear.
MAX_CRF = 28


def size_mb(path: str) -> float:
    return os.path.getsize(path) / (1024 * 1024)


def encode(source: str, out: str, crf: int, to_720: bool = False) -> None:
    # 720 on the short side: 720x1280 for vertical, 1280x720 for horizontal.
    vf = ["-vf", "scale='if(lt(iw,ih),720,-2)':'if(lt(iw,ih),-2,720)'"] if to_720 else []
    subprocess.run(
        ["ffmpeg", "-v", "error", "-y", "-i", source, *vf,
         "-c:v", "libx264", "-crf", str(crf), "-preset", "slow", "-pix_fmt", "yuv420p",
         "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", out],
        check=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", nargs="?", default=os.path.join("output", "video.mp4"))
    parser.add_argument("--mb", type=float, default=25.0, help="target size in MB")
    parser.add_argument("--allow-720", action="store_true",
                        help="if 1080p cannot reach the target, drop to 720p")
    parser.add_argument("--out")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("\n  FFmpeg is missing.\n")
    source = args.source if os.path.isabs(args.source) else os.path.join(ROOT, args.source)
    if not os.path.exists(source):
        sys.exit(f"\n  No file at {source} — render first with:  npm run render\n")

    base, ext = os.path.splitext(source)
    out = args.out or f"{base}_light{ext}"

    print(f"\n  Original: {size_mb(source):.1f} MB   Target: {args.mb:.0f} MB\n")
    if size_mb(source) <= args.mb:
        shutil.copyfile(source, out)
        print(f"  Already under the target, copied as is: {out}\n")
        return

    # Higher CRF compresses more and softens the text a little more, so stop
    # at the first one that fits. Every +6 CRF roughly halves the size, which
    # lets each attempt jump close to the answer instead of stepping by one.
    for to_720 in ([False, True] if args.allow_720 else [False]):
        crf = 22 if to_720 else 20
        while True:
            encode(source, out, crf, to_720)
            mb = size_mb(out)
            res = "720p" if to_720 else "full size"
            print(f"  CRF {crf} {res:<9} ->  {mb:.1f} MB")
            if mb <= args.mb:
                print(f"\n  Done: {out}\n")
                return
            if crf >= MAX_CRF:
                break
            guess = crf + math.ceil(6 * math.log2(mb / args.mb))
            crf = min(max(guess, crf + 2), MAX_CRF)

    print(f"\n  Lightest without ruining the text: {size_mb(out):.1f} MB  ({out})")
    if not args.allow_720:
        print("  --allow-720 goes further, at the cost of resolution.")
    print("  For long videos a Drive or Dropbox link beats any attachment.\n")


if __name__ == "__main__":
    main()
