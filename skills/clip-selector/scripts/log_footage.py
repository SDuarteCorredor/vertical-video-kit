"""Log raw footage so clips can be chosen from what is in it, not from guesses.

    python scripts/log_footage.py raw/
    python scripts/log_footage.py interview.mov --lang es
    python scripts/log_footage.py raw/ --no-transcript --every 3

For every video file it writes, into <folder>/_log/ (or --out):

    footage-log.md       one section per file: technical facts, a timecoded
                         transcript, picture changes and long silences
    footage-log.json     the same, for scripts
    strips/<file>.jpg    a filmstrip: one labelled frame every --every seconds
                         and at every picture change, timecode burned on each

This is the logging pass an assistant editor does before anyone cuts: what
is said, where, how it looks, where the camera changes and where nobody
talks. The selection itself is a judgement call made by reading this log,
looking at the strips and listening to candidates — see SKILL.md.

Phone footage is usually variable frame rate; the log says so per file,
because Premiere drifts audio against picture on long VFR clips.
"""
from __future__ import annotations

import argparse
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

VIDEO = {".mp4", ".mov", ".m4v", ".mkv", ".avi", ".webm", ".mxf", ".mts"}


def need(tool: str) -> None:
    if not shutil.which(tool):
        sys.exit(f"\n  {tool} is not on the PATH. Install FFmpeg (see docs/NO-AGENT.md).\n")


def fraction(text: str | None) -> float:
    if not text or text in ("0/0", "N/A"):
        return 0.0
    if "/" in text:
        num, den = text.split("/", 1)
        return float(num) / float(den) if float(den) else 0.0
    return float(text)


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True, text=True).stdout
    data = json.loads(out or "{}")
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), None)
    rate = fraction(video.get("r_frame_rate"))
    avg = fraction(video.get("avg_frame_rate"))
    rotation = 0
    for side in video.get("side_data_list", []) or []:
        if "rotation" in side:
            rotation = int(side["rotation"])
    rotation = rotation or int((video.get("tags") or {}).get("rotate", 0) or 0)
    width, height = video.get("width"), video.get("height")
    if rotation in (90, -90, 270, -270) and width and height:
        width, height = height, width
    return {
        "duration": round(float(data.get("format", {}).get("duration", 0) or 0), 3),
        "width": width,
        "height": height,
        "fps": round(avg or rate, 3),
        # A phone records variable frame rate: the nominal and the average rate
        # disagree. Premiere then lets audio drift on long clips.
        "vfr": bool(rate and avg and abs(rate - avg) > 0.05),
        "codec": video.get("codec_name"),
        "audio": bool(audio),
        "audio_channels": (audio or {}).get("channels"),
    }


def scene_changes(path: Path, threshold: float) -> list[float]:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-an",
         "-vf", f"scale=320:-2,select='gt(scene,{threshold})',showinfo", "-f", "null", "-"],
        capture_output=True, text=True)
    return [round(float(t), 2) for t in re.findall(r"pts_time:([0-9.]+)", result.stderr)]


def silences(path: Path, noise_db: int, min_s: float) -> list[tuple[float, float]]:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-i", str(path), "-vn",
         "-af", f"silencedetect=noise={noise_db}dB:d={min_s}", "-f", "null", "-"],
        capture_output=True, text=True)
    starts = [float(t) for t in re.findall(r"silence_start: (-?[0-9.]+)", result.stderr)]
    ends = [float(t) for t in re.findall(r"silence_end: ([0-9.]+)", result.stderr)]
    return [(round(max(a, 0), 2), round(b, 2)) for a, b in zip(starts, ends)]


def transcribe(path: Path, model, lang: str | None) -> list[dict]:
    segments, _ = model.transcribe(str(path), language=lang, vad_filter=True,
                                   word_timestamps=True)
    rows = []
    for seg in segments:
        text = (seg.text or "").strip()
        if not text:
            continue
        words = [{"w": w.word.strip(), "s": round(w.start, 2), "e": round(w.end, 2)}
                 for w in (seg.words or []) if w.word.strip()]
        rows.append({"start": round(seg.start, 2), "end": round(seg.end, 2),
                     "text": text, "words": words})
    return rows


def timecode(seconds: float, fps: float) -> str:
    fps_whole = max(1, round(fps or 30))
    frames = int(round(seconds * fps_whole))
    ff = frames % fps_whole
    total = frames // fps_whole
    return f"{total // 3600:02d}:{total % 3600 // 60:02d}:{total % 60:02d}:{ff:02d}"


def filmstrip(path: Path, times: list[float], fps: float, out: Path) -> None:
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("    (no filmstrip: pip install pillow)")
        return
    thumbs = []
    with tempfile.TemporaryDirectory() as tmp:
        for index, t in enumerate(times):
            frame = Path(tmp) / f"{index:04d}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", str(path),
                            "-frames:v", "1", "-vf", "scale=-2:240", "-q:v", "4", str(frame)],
                           capture_output=True)
            if frame.exists():
                thumbs.append((t, Image.open(frame).convert("RGB")))
        if not thumbs:
            return
        try:
            font = ImageFont.truetype("DejaVuSans-Bold.ttf", 18)
        except OSError:
            font = ImageFont.load_default()
        width, height = thumbs[0][1].size
        columns = min(6, len(thumbs))
        rows = math.ceil(len(thumbs) / columns)
        sheet = Image.new("RGB", (columns * width, rows * height), (20, 20, 20))
        for index, (t, image) in enumerate(thumbs):
            image = image.resize((width, height))
            draw = ImageDraw.Draw(image)
            label = timecode(t, fps)
            draw.rectangle([0, 0, 150, 26], fill=(0, 0, 0))
            draw.text((6, 3), label, fill=(255, 220, 0), font=font)
            sheet.paste(image, ((index % columns) * width, (index // columns) * height))
        sheet.save(out, quality=82)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("source", help="a video file or a folder of them")
    parser.add_argument("--out", help="where the log goes (default: <folder>/_log)")
    parser.add_argument("--lang", help="spoken language, e.g. es or en (default: detect)")
    parser.add_argument("--model", default="base", help="Whisper model: tiny, base, small...")
    parser.add_argument("--no-transcript", action="store_true",
                        help="skip speech; for B-roll with no one talking")
    parser.add_argument("--every", type=float, default=5.0,
                        help="seconds between filmstrip frames (default 5)")
    parser.add_argument("--scene", type=float, default=0.3,
                        help="picture-change threshold, 0-1 (default 0.3)")
    args = parser.parse_args()

    need("ffmpeg")
    need("ffprobe")
    source = Path(args.source)
    if source.is_dir():
        files = sorted(p for p in source.iterdir() if p.suffix.lower() in VIDEO)
        base = source
    elif source.exists():
        files = [source]
        base = source.parent
    else:
        sys.exit(f"\n  Not found: {source}\n")
    if not files:
        sys.exit(f"\n  No video files in {source}\n")

    out = Path(args.out) if args.out else base / "_log"
    (out / "strips").mkdir(parents=True, exist_ok=True)

    model = None
    if not args.no_transcript:
        try:
            from faster_whisper import WhisperModel
        except ImportError:
            sys.exit("\n  faster-whisper is missing:  pip install faster-whisper\n"
                     "  (or run with --no-transcript for footage without speech)\n")
        print(f"\n  Loading Whisper ({args.model})...")
        model = WhisperModel(args.model, device="auto", compute_type="int8")

    log = {"source": str(source.resolve()), "files": []}
    md = [f"# Footage log — {source.name}\n",
          "Timecodes are HH:MM:SS:FF from the start of each file.\n"]

    for number, path in enumerate(files, 1):
        print(f"  [{number}/{len(files)}] {path.name}")
        info = probe(path)
        fps = info["fps"] or 30
        cuts = scene_changes(path, args.scene)
        quiet = silences(path, -35, 1.5) if info["audio"] else []
        speech = transcribe(path, model, args.lang) if (model and info["audio"]) else []

        step = max(args.every, info["duration"] / 60 or 1)  # at most ~60 frames a file
        times = sorted(set([round(t, 2) for t in cuts] +
                           [round(i * step, 2) for i in range(int(info["duration"] // step) + 1)]))
        times = [t for t in times if t < max(info["duration"] - 0.1, 0.01)]
        strip = out / "strips" / f"{path.stem}.jpg"
        filmstrip(path, times, fps, strip)

        entry = {"file": path.name, "path": str(path.resolve()), **info,
                 "picture_changes": cuts,
                 "silences": [{"start": a, "end": b} for a, b in quiet],
                 "speech": speech, "strip": str(strip.relative_to(out))}
        log["files"].append(entry)

        flags = []
        if info["vfr"]:
            flags.append("**VFR** (phone footage: convert to constant frame rate "
                         "before a long edit, or audio drifts)")
        if not info["audio"]:
            flags.append("no audio")
        md.append(f"\n## {number}. {path.name}\n")
        md.append(f"{info['duration']:.1f} s · {info['width']}×{info['height']} · "
                  f"{info['fps']} fps · {info['codec']}"
                  + (f" · {'; '.join(flags)}" if flags else "") + "\n")
        md.append(f"Filmstrip: `{entry['strip']}`\n")
        if cuts:
            md.append("Picture changes: " + ", ".join(timecode(c, fps) for c in cuts) + "\n")
        if quiet:
            md.append("Silences over 1.5 s: " + ", ".join(
                f"{timecode(a, fps)}–{timecode(b, fps)}" for a, b in quiet) + "\n")
        if speech:
            md.append("\n| In | Out | Said |\n|---|---|---|")
            for seg in speech:
                text = seg["text"].replace("|", "/")
                md.append(f"| {timecode(seg['start'], fps)} | {timecode(seg['end'], fps)} | {text} |")
            md.append("")
        elif info["audio"] and model:
            md.append("\nNo speech detected.\n")

    (out / "footage-log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False),
                                          encoding="utf-8")
    (out / "footage-log.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    total = sum(f["duration"] for f in log["files"])
    print(f"\n  {len(files)} files, {total / 60:.1f} min logged → {out}/footage-log.md\n")


if __name__ == "__main__":
    main()
