"""A labelled contact sheet of a folder of clips, to choose takes from.

    python scripts/contact_sheet.py raw/
    python scripts/contact_sheet.py raw/ --out sheet.jpg --columns 6

Every thumbnail carries a number and the file name, and an index .txt is
written next to the sheet. This exists because of a real mistake: takes were
picked by counting positions on an unlabelled grid, the count was off, and
three clips in the final video were the wrong ones. Never pick a take by its
position on a grid that has no names on it.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    sys.exit("\n  Pillow is missing:  pip install pillow\n")

VIDEO = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm"}


def probe(path: Path) -> tuple[float, int | None, int | None]:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height:format=duration", "-of", "json", str(path)],
        capture_output=True, text=True).stdout
    data = json.loads(out or "{}")
    stream = (data.get("streams") or [{}])[0]
    return (float(data.get("format", {}).get("duration", 0)),
            stream.get("width"), stream.get("height"))


def label_font(size: int):
    for name in ("arialbd.ttf", "Arial Bold.ttf", "DejaVuSans-Bold.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("folder")
    parser.add_argument("--out")
    parser.add_argument("--columns", type=int, default=6)
    parser.add_argument("--width", type=int, default=240, help="thumbnail width in px")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("\n  FFmpeg is missing. See docs/NO-AGENT.md.\n")

    folder = Path(args.folder)
    videos = sorted(p for p in folder.iterdir() if p.suffix.lower() in VIDEO)
    if not videos:
        sys.exit(f"\n  No videos in {folder}\n")
    out = Path(args.out) if args.out else folder / "contact_sheet.jpg"

    font = label_font(18)
    thumbs, index = [], []
    with tempfile.TemporaryDirectory() as tmp:
        for i, video in enumerate(videos, 1):
            length, w, h = probe(video)
            jpg = Path(tmp) / f"{i:03d}.jpg"
            # The middle of a take is more representative than its first frame,
            # which is usually the phone still settling.
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{length / 2:.2f}",
                            "-i", str(video), "-frames:v", "1",
                            "-vf", f"scale={args.width}:-2", str(jpg)])
            if not jpg.exists():
                print(f"  skipped (unreadable): {video.name}")
                continue
            img = Image.open(jpg).convert("RGB")
            draw = ImageDraw.Draw(img)
            draw.rectangle([0, 0, img.width, 26], fill=(0, 0, 0))
            draw.text((6, 3), f"{i:02d}  {video.stem[-14:]}", fill=(255, 255, 255), font=font)
            thumbs.append(img)
            index.append(f"{i:02d}\t{length:6.1f}s\t{w}x{h}\t{video.name}")

    if not thumbs:
        sys.exit("\n  None of the videos could be read.\n")
    cols = min(args.columns, len(thumbs))
    rows = (len(thumbs) + cols - 1) // cols
    cw = max(t.width for t in thumbs)
    ch = max(t.height for t in thumbs)
    sheet = Image.new("RGB", (cols * cw, rows * ch), (255, 255, 255))
    for k, thumb in enumerate(thumbs):
        sheet.paste(thumb, ((k % cols) * cw, (k // cols) * ch))
    sheet.save(out, quality=88)
    out.with_suffix(".txt").write_text("\n".join(index), encoding="utf-8")
    print(f"\n  Sheet: {out}\n  Index: {out.with_suffix('.txt')}\n")
    print("\n".join(index))


if __name__ == "__main__":
    main()
