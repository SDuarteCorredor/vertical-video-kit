"""Finds the parts of a long video worth cutting into shorts.

Transcribes the whole thing, then proposes self-contained windows and ranks
them. The ranking is a shortlist, not a verdict: it is good at throwing out
the 90% that is throat-clearing and mediocre at picking the single best one.
Read the transcript of the top few and choose with your own judgement.

    python scripts/find_moments.py talk.mp4
    python scripts/find_moments.py talk.mp4 --min 20 --max 55 --top 8

Writes moments.json next to the video.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Openings that stand on their own. A clip that starts with "and so that's why"
# has already lost the viewer, no matter how good the rest of it is.
STRONG_OPENERS = re.compile(
    r"^\s*(the (secret|problem|reason|trick|mistake)|here'?s|most people|"
    r"nobody|everyone|stop|never|always|if you|why |how |what if|imagine|"
    r"three|two|one thing|el (secreto|problema|error)|la mayoría|nadie|"
    r"todo el mundo|nunca|siempre|si (tú|usted)|por qué|cómo |qué pasa)",
    re.IGNORECASE,
)

WEAK_OPENERS = re.compile(
    r"^\s*(and |so |but |then |also |um|uh|yeah|okay|right|y |pero |entonces |"
    r"también |bueno |o sea)",
    re.IGNORECASE,
)

HAS_NUMBER = re.compile(r"\b\d+([.,]\d+)?\s*(%|percent|por ciento|x|k|million|mil)?\b",
                        re.IGNORECASE)


def transcribe(path: str, model_name: str, lang: str | None) -> list[dict]:
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        sys.exit("\n  faster-whisper is missing.  pip install faster-whisper\n")

    model = WhisperModel(model_name, device="auto", compute_type="int8")
    segments, _ = model.transcribe(path, language=lang, vad_filter=True)
    return [{"start": float(s.start), "end": float(s.end), "text": s.text.strip()}
            for s in segments if s.text and s.text.strip()]


def score(text: str, seconds: float, gap_before: float) -> float:
    value = 0.0
    if STRONG_OPENERS.search(text):
        value += 3.0
    if WEAK_OPENERS.search(text):
        value -= 2.5
    if HAS_NUMBER.search(text):
        value += 1.0
    if "?" in text[: len(text) // 3 or 1]:
        value += 1.5
    # A real pause before it usually means a new thought started there.
    value += min(gap_before, 1.5)
    # Density: a window full of words beats one full of silence.
    value += min(len(text.split()) / max(seconds, 1) / 3.0, 1.5)
    if text.rstrip().endswith((".", "!", "?")):
        value += 1.0
    return round(value, 2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("video")
    parser.add_argument("--model", default="base")
    parser.add_argument("--lang")
    parser.add_argument("--min", type=float, default=18.0, dest="min_s")
    parser.add_argument("--max", type=float, default=58.0, dest="max_s")
    parser.add_argument("--top", type=int, default=6)
    args = parser.parse_args()

    if not os.path.exists(args.video):
        sys.exit(f"\n  No file at {args.video}\n")

    print(f"\n  Transcribing with faster-whisper ({args.model})...")
    segments = transcribe(args.video, args.model, args.lang)
    if not segments:
        sys.exit("\n  Nothing transcribed — is there speech in this file?\n")
    print(f"  {len(segments)} segments\n")

    moments = []
    for index, first in enumerate(segments):
        text_parts: list[str] = []
        for last in segments[index:]:
            text_parts.append(last["text"])
            span = last["end"] - first["start"]
            if span < args.min_s:
                continue
            if span > args.max_s:
                break
            gap = first["start"] - segments[index - 1]["end"] if index else 2.0
            text = " ".join(text_parts)
            moments.append({
                "start": round(first["start"], 2),
                "end": round(last["end"], 2),
                "seconds": round(span, 1),
                "score": score(text, span, max(gap, 0.0)),
                "text": text,
            })

    moments.sort(key=lambda m: m["score"], reverse=True)

    # Keep the shortlist from being six versions of the same 40 seconds.
    chosen: list[dict] = []
    for moment in moments:
        if all(moment["start"] >= c["end"] or moment["end"] <= c["start"]
               for c in chosen):
            chosen.append(moment)
        if len(chosen) >= args.top:
            break

    out_path = os.path.splitext(args.video)[0] + "-moments.json"
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump({"source": os.path.basename(args.video), "moments": chosen},
                  handle, indent=2, ensure_ascii=False)

    for rank, moment in enumerate(chosen, 1):
        preview = moment["text"][:110].replace("\n", " ")
        print(f"  {rank}. {moment['start']:7.1f}s  {moment['seconds']:4.0f}s  "
              f"score {moment['score']:>5}")
        print(f"     {preview}...\n")

    print(f"  {out_path}")
    print(f"  Cut one:  python scripts/cut.py {args.video} "
          f"--start {chosen[0]['start']} --end {chosen[0]['end']}\n")


if __name__ == "__main__":
    main()
