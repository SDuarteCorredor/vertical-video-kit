"""Cuts a range out of a horizontal video and reframes it to 9:16.

    python scripts/cut.py talk.mp4 --start 412 --end 458
    python scripts/cut.py talk.mp4 --start 412 --end 458 --mode crop --focus left
    python scripts/cut.py talk.mp4 --start 412 --end 458 --captions

Modes:
  blur   fit the whole frame, fill the rest with a blurred copy  [default]
  crop   fill the frame, cut off the sides — nothing is letterboxed but
         whatever sits at the edge is gone
  fit    fit the whole frame on flat black bars
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

W, H = 1080, 1920

FOCUS_X = {
    "center": "(in_w-out_w)/2",
    "left": "0",
    "right": "in_w-out_w",
}

# Sits above the platform UI, heavy, with a thick outline so it survives
# landing on a bright background.
SUBTITLE_STYLE = (
    "FontName=Arial,FontSize=54,Bold=1,PrimaryColour=&H00FFFFFF,"
    "OutlineColour=&H00000000,BorderStyle=1,Outline=4,Shadow=0,"
    "Alignment=2,MarginV=400"
)


def filter_path(path: str) -> str:
    """FFmpeg filter arguments need Windows paths spelled a specific way."""
    escaped = os.path.abspath(path).replace("\\", "/").replace(":", "\\:")
    return f"'{escaped}'"


def vertical_filter(mode: str, focus: str) -> str:
    """Filter graph reading [0:v], left open so captions can be appended."""
    if mode == "crop":
        return (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=increase,"
                f"crop={W}:{H}:{FOCUS_X[focus]}:(in_h-out_h)/2")
    if mode == "fit":
        return (f"[0:v]scale={W}:{H}:force_original_aspect_ratio=decrease,"
                f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:black")
    return (
        f"[0:v]split=2[bg][fg];"
        f"[bg]scale={W}:{H}:force_original_aspect_ratio=increase,"
        f"crop={W}:{H},boxblur=32:4[bgb];"
        f"[fg]scale={W}:{H}:force_original_aspect_ratio=decrease[fgs];"
        f"[bgb][fgs]overlay=(W-w)/2:(H-h)/2"
    )


def seconds_to_srt(value: float) -> str:
    hours, rest = divmod(max(value, 0.0), 3600)
    minutes, seconds = divmod(rest, 60)
    whole = int(seconds)
    millis = int(round((seconds - whole) * 1000))
    return f"{int(hours):02d}:{int(minutes):02d}:{whole:02d},{millis:03d}"


def write_srt(clip: str, srt_path: str, model_name: str, lang: str | None) -> None:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("\n  faster-whisper is missing.  pip install faster-whisper\n")

    model = WhisperModel(model_name, device="auto", compute_type="int8")
    segments, _ = model.transcribe(clip, language=lang, word_timestamps=True,
                                   vad_filter=True)

    lines: list[str] = []
    index = 1
    for segment in segments:
        words = list(segment.words or [])
        if not words:
            continue
        # Three words per cue: long cues make people read instead of watch.
        for start in range(0, len(words), 3):
            group = words[start:start + 3]
            text = " ".join(w.word.strip() for w in group).strip()
            if not text:
                continue
            lines.append(
                f"{index}\n"
                f"{seconds_to_srt(float(group[0].start))} --> "
                f"{seconds_to_srt(float(group[-1].end))}\n"
                f"{text}\n"
            )
            index += 1

    with open(srt_path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(lines))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video")
    parser.add_argument("--start", type=float, required=True)
    parser.add_argument("--end", type=float, required=True)
    parser.add_argument("--out")
    parser.add_argument("--mode", default="blur", choices=["blur", "crop", "fit"])
    parser.add_argument("--focus", default="center", choices=list(FOCUS_X))
    parser.add_argument("--captions", action="store_true",
                        help="transcribe the clip and burn captions into it")
    parser.add_argument("--model", default="base")
    parser.add_argument("--lang")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("\n  FFmpeg is missing.\n")
    if not os.path.exists(args.video):
        sys.exit(f"\n  No file at {args.video}\n")
    span = args.end - args.start
    if span <= 0:
        sys.exit("\n  --end must come after --start.\n")

    out = args.out or (f"{os.path.splitext(args.video)[0]}"
                       f"-clip-{int(args.start)}.mp4")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)

    chain = vertical_filter(args.mode, args.focus)

    with tempfile.TemporaryDirectory() as tmp:
        if args.captions:
            # Cut first, transcribe the cut: timestamps then start at zero and
            # line up with the clip instead of the source timeline.
            rough = os.path.join(tmp, "rough.mp4")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(args.start),
                            "-i", args.video, "-t", str(span),
                            "-c:v", "libx264", "-crf", "20", "-preset", "veryfast",
                            "-c:a", "aac", rough], check=True)
            srt = os.path.join(tmp, "captions.srt")
            print("  Transcribing the clip...")
            write_srt(rough, srt, args.model, args.lang)
            chain += f",subtitles={filter_path(srt)}:force_style='{SUBTITLE_STYLE}'"
            source_args = ["-i", rough]
            trim_args: list[str] = []
        else:
            source_args = ["-ss", str(args.start), "-i", args.video]
            trim_args = ["-t", str(span)]

        command = ["ffmpeg", "-v", "error", "-stats", "-y", *source_args, *trim_args,
                   "-filter_complex", chain + "[v]",
                   # -filter_complex turns off ffmpeg's automatic stream
                   # selection, so the audio has to be mapped by hand or the
                   # clip comes out silent. The ? tolerates a source with none.
                   "-map", "[v]", "-map", "0:a?",
                   "-c:v", "libx264", "-profile:v", "high", "-pix_fmt", "yuv420p",
                   "-crf", "20", "-preset", "slow",
                   "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                   "-movflags", "+faststart", out]
        subprocess.run(command, check=True)

    print(f"\n  {out}   {os.path.getsize(out) / (1024 * 1024):.1f} MB  "
          f"({span:.1f}s, {args.mode})\n")


if __name__ == "__main__":
    main()
