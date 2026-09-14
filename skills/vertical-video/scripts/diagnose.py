"""Measures an existing video and says what is wrong with it.

Numbers settle arguments that opinions don't. "It looks cheap" is hard to act
on; "398 kbps at 1080p, which is twenty times below normal" tells you exactly
what to fix and proves it was worth redoing.

    python scripts/diagnose.py video.mp4
    python scripts/diagnose.py video.mp4 --frames 4    # also pull stills

Writes frames next to the video as <name>-frame-N.jpg when asked.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import shutil
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def probe(path: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", path],
        capture_output=True, text=True,
    ).stdout
    return json.loads(out or "{}")


def loudness(path: str) -> str | None:
    """Integrated loudness, the number that explains 'the audio feels quiet'."""
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", path,
         "-af", "ebur128=framelog=quiet", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    for line in reversed((result.stderr or "").splitlines()):
        if "I:" in line and "LUFS" in line:
            return line.strip()
    return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video")
    parser.add_argument("--frames", type=int, default=0,
                        help="how many stills to extract for a look")
    args = parser.parse_args()

    if not shutil.which("ffprobe"):
        sys.exit("\n  FFmpeg is missing.\n")
    if not os.path.exists(args.video):
        sys.exit(f"\n  No file at {args.video}\n")

    data = probe(args.video)
    fmt = data.get("format", {})
    streams = data.get("streams", [])
    video = next((s for s in streams if s.get("codec_type") == "video"), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)

    duration = float(fmt.get("duration", 0) or 0)
    size_mb = float(fmt.get("size", 0) or 0) / (1024 * 1024)

    print(f"\n  {os.path.basename(args.video)}")
    print(f"  {duration:.1f}s · {size_mb:.1f} MB\n")

    notes: list[str] = []

    if video:
        width = int(video.get("width", 0))
        height = int(video.get("height", 0))
        rate = video.get("avg_frame_rate", "0/1")
        try:
            num, den = (float(x) for x in rate.split("/"))
            fps = num / den if den else 0.0
        except ValueError:
            fps = 0.0
        kbps = int(video.get("bit_rate", 0) or 0) / 1000
        if not kbps and duration:
            kbps = (float(fmt.get("size", 0) or 0) * 8 / duration) / 1000

        print(f"  video   {width}x{height} · {fps:.0f} fps · {kbps:.0f} kbps · "
              f"{video.get('codec_name')}")

        ratio = width / height if height else 0
        if not math.isclose(ratio, 9 / 16, rel_tol=0.02):
            notes.append(f"Not 9:16 ({width}x{height}). Vertical feeds crop or "
                         f"letterbox anything else.")
        if height and kbps and kbps < (height * 1.5):
            notes.append(f"{kbps:.0f} kbps is low for {height}p — this is what "
                         f"makes text look washed out. Re-encode from the master "
                         f"at CRF 18-20 instead of a fixed bitrate.")
        if fps and fps < 24:
            notes.append(f"{fps:.0f} fps looks stuttery on a phone.")
    else:
        notes.append("No video stream at all.")

    if audio:
        print(f"  audio   {audio.get('codec_name')} · "
              f"{audio.get('sample_rate')} Hz · "
              f"{int(audio.get('bit_rate', 0) or 0) / 1000:.0f} kbps")
        level = loudness(args.video)
        if level:
            print(f"  level   {level}")
    else:
        notes.append("No audio track. On muted-by-default feeds that is survivable "
                     "only if the captions carry the whole message.")

    if duration > 180:
        notes.append(f"{duration:.0f}s is long for short-form; most of the "
                     f"audience leaves well before the end.")

    if args.frames > 0 and duration:
        base = os.path.splitext(args.video)[0]
        for index in range(args.frames):
            at = duration * (index + 0.5) / args.frames
            out = f"{base}-frame-{index + 1}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(at),
                            "-i", args.video, "-frames:v", "1", "-q:v", "2", out],
                           check=False)
            print(f"  still   {out}")

    if notes:
        print("\n  Worth fixing\n  " + "-" * 44)
        for note in notes:
            print(f"  · {note}")
    else:
        print("\n  Nothing obviously wrong.")
    print()


if __name__ == "__main__":
    main()
