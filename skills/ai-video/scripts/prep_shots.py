"""Cut the shots an AI model will replace out of a finished video, with
everything the generator needs next to each one.

    python scripts/prep_shots.py video.mov --detect
    python scripts/prep_shots.py video.mov --out shots/ \
        --shot walk-in=0-2.9 --shot front-desk=2.9-7.89 --shot selfie=39-52.57

`--detect` only prints where the picture changes, so the cut points come from
the footage instead of from scrubbing by eye. With `--shot`, each shot becomes:

    shots/<n>_<name>.mp4         the clip, re-encoded H.264 (AI tools reject HEVC)
    shots/<n>_<name>_first.jpg   first frame: the start frame for image-to-video
    shots/<n>_<name>_mid.jpg     middle frame: what the shot is about
    shots/narration.mp3          the whole soundtrack, to keep timing in the edit
    shots/manifest.json          names, times and durations, for the edit and for whoever comes next

Shots are cut with a re-encode, not a stream copy: a copy snaps to the
nearest keyframe and the clip comes back up to a second longer than asked,
which then no longer lines up with the narration it has to sit under.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def need(tool: str) -> None:
    if not shutil.which(tool):
        sys.exit(f"\n  {tool} is not on the PATH. Install FFmpeg (see docs/NO-AGENT.md).\n")


def run(args: list[str]) -> None:
    result = subprocess.run(args, capture_output=True, text=True)
    if result.returncode != 0:
        sys.exit(f"\n  ffmpeg failed:\n{result.stderr[-1500:]}\n")


def duration(path: Path) -> float:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return float(out.strip() or 0)


def detect(video: Path, threshold: float) -> None:
    # showinfo prints one line per frame the scene filter lets through.
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(video), "-an",
         "-vf", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
        capture_output=True, text=True)
    cuts = [float(t) for t in re.findall(r"pts_time:([0-9.]+)", result.stderr)]
    total = duration(video)
    print(f"\n  {video.name}: {total:.2f} s, {len(cuts)} picture changes "
          f"(threshold {threshold})\n")
    start = 0.0
    for cut in cuts + [total]:
        print(f"    {start:7.2f} - {cut:7.2f}   ({cut - start:5.2f} s)")
        start = cut
    print("\n  A UI screen recording changes a little on every tap; raise --threshold "
          "if every tap shows up as a cut.\n")


def parse_shot(text: str) -> tuple[str, float, float]:
    match = re.fullmatch(r"([\w-]+)=([0-9.]+)-([0-9.]+)", text.strip())
    if not match:
        sys.exit(f"\n  Bad --shot '{text}'. Use name=start-end in seconds, e.g. intro=0-2.9\n")
    name, start, end = match.group(1), float(match.group(2)), float(match.group(3))
    if end <= start:
        sys.exit(f"\n  Shot '{name}' ends before it starts.\n")
    return name, start, end


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video")
    parser.add_argument("--detect", action="store_true", help="print picture changes and stop")
    parser.add_argument("--threshold", type=float, default=0.25)
    parser.add_argument("--shot", action="append", default=[], metavar="NAME=START-END")
    parser.add_argument("--out", default="shots")
    parser.add_argument("--crf", type=int, default=14, help="lower is better; 14 is near-lossless")
    args = parser.parse_args()

    need("ffmpeg")
    need("ffprobe")
    video = Path(args.video)
    if not video.exists():
        sys.exit(f"\n  Not found: {video}\n")

    if args.detect or not args.shot:
        detect(video, args.threshold)
        if not args.shot:
            return

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    total = duration(video)
    manifest = {"source": str(video.resolve()), "duration": round(total, 3), "shots": []}

    for index, raw in enumerate(args.shot, start=1):
        name, start, end = parse_shot(raw)
        end = min(end, total)
        stem = f"{index:02d}_{name}"
        clip = out / f"{stem}.mp4"
        run(["ffmpeg", "-v", "error", "-y", "-ss", str(start), "-to", str(end), "-i", str(video),
             "-c:v", "libx264", "-crf", str(args.crf), "-preset", "slow", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", str(clip)])
        run(["ffmpeg", "-v", "error", "-y", "-i", str(clip), "-frames:v", "1", "-q:v", "2",
             str(out / f"{stem}_first.jpg")])
        run(["ffmpeg", "-v", "error", "-y", "-ss", str((end - start) / 2), "-i", str(clip),
             "-frames:v", "1", "-q:v", "2", str(out / f"{stem}_mid.jpg")])
        manifest["shots"].append({"name": name, "file": clip.name, "start": start, "end": end,
                                  "length": round(end - start, 3)})
        print(f"  {clip.name:40s} {start:7.2f} - {end:7.2f}  ({end - start:.2f} s)")

    run(["ffmpeg", "-v", "error", "-y", "-i", str(video), "-vn",
         "-c:a", "libmp3lame", "-q:a", "0", str(out / "narration.mp3")])
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False),
                                       encoding="utf-8")
    print(f"\n  {len(manifest['shots'])} shots, narration.mp3 and manifest.json in {out}/\n")


if __name__ == "__main__":
    main()
