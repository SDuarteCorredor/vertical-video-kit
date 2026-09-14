"""Takes apart a short that works, so you can borrow the structure.

Copying someone's video gets you a worse copy. Copying the *shape* — how fast
it cuts, how long the hook runs, how many words per minute, where the payoff
lands — gets you something of your own that holds attention the same way.

    python scripts/analyze.py reference.mp4
    python scripts/analyze.py reference.mp4 --json out.json

Needs the file locally. To fetch one you have the right to study:
    python ../clip-cutter/scripts/download.py <url>
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

SCENE_LINE = re.compile(r"pts_time:([0-9.]+)")


def probe(path: str) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-print_format", "json",
         "-show_format", "-show_streams", path],
        capture_output=True, text=True,
    ).stdout
    return json.loads(out or "{}")


def scene_cuts(path: str, threshold: float = 0.30) -> list[float]:
    """Timestamps where the picture changes enough to count as a cut."""
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", path,
         "-vf", f"select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
        capture_output=True, text=True,
    )
    return [float(m.group(1)) for m in SCENE_LINE.finditer(result.stderr or "")]


def transcribe(path: str, model_name: str, lang: str | None) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        return []
    model = WhisperModel(model_name, device="auto", compute_type="int8")
    segments, _ = model.transcribe(path, language=lang, vad_filter=True)
    return [{"start": float(s.start), "end": float(s.end), "text": s.text.strip()}
            for s in segments if s.text and s.text.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video")
    parser.add_argument("--model", default="base")
    parser.add_argument("--lang")
    parser.add_argument("--json", dest="json_out")
    args = parser.parse_args()

    if not shutil.which("ffprobe"):
        sys.exit("\n  FFmpeg is missing.\n")
    if not os.path.exists(args.video):
        sys.exit(f"\n  No file at {args.video}\n")

    data = probe(args.video)
    fmt = data.get("format", {})
    video = next((s for s in data.get("streams", [])
                  if s.get("codec_type") == "video"), {})
    duration = float(fmt.get("duration", 0) or 0)
    width, height = int(video.get("width", 0)), int(video.get("height", 0))

    cuts = scene_cuts(args.video)
    shot = duration / (len(cuts) + 1) if duration else 0.0

    print(f"\n  {os.path.basename(args.video)}")
    print(f"  {width}x{height} · {duration:.1f}s\n")
    print(f"  cuts            {len(cuts)}")
    print(f"  avg shot        {shot:.1f}s"
          + ("   (fast — the frame rarely sits still)" if shot < 2.5 else ""))

    segments = transcribe(args.video, args.model, args.lang)
    hook = ""
    words_per_minute = 0.0

    if segments:
        words = sum(len(s["text"].split()) for s in segments)
        words_per_minute = words / duration * 60 if duration else 0.0
        hook = " ".join(s["text"] for s in segments if s["start"] < 3.0)
        print(f"  speech rate     {words_per_minute:.0f} words/min"
              + ("   (fast — typical of short-form)" if words_per_minute > 165 else ""))
        print(f"\n  first 3 seconds\n  {'-' * 44}\n  {hook or '(no speech)'}\n")
        print(f"  transcript\n  {'-' * 44}")
        for segment in segments:
            print(f"  {segment['start']:6.1f}  {segment['text']}")
    else:
        print("\n  No transcript — install faster-whisper for the spoken "
              "breakdown:\n    pip install faster-whisper")

    print(f"""
  What to take from it
  {'-' * 44}
  · Does the hook name a problem, promise an outcome, or open a loop?
  · What is on screen during the first second — a face, text, or motion?
  · Where does the payoff land, and how much of the clip is left after it?
  · Would this still work with the sound off?
""")

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as handle:
            json.dump({
                "file": os.path.basename(args.video),
                "duration": round(duration, 2),
                "resolution": f"{width}x{height}",
                "cuts": len(cuts),
                "averageShotSeconds": round(shot, 2),
                "wordsPerMinute": round(words_per_minute, 1),
                "hook": hook,
                "transcript": segments,
            }, handle, indent=2, ensure_ascii=False)
        print(f"  {args.json_out}\n")


if __name__ == "__main__":
    main()
