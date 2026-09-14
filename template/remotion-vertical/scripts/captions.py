"""Builds word-by-word captions from the narration that actually got rendered.

Transcribing the audio instead of splitting the script is the whole point: the
timings come from the voice, so the highlight lands on the word being said even
when the engine pauses somewhere you did not expect.

    python scripts/captions.py                 # faster-whisper if available
    python scripts/captions.py --model small   # slower, better with accents
    python scripts/captions.py --engine estimate   # no Whisper? rough fallback

Reads:  src/timings.json · audio/*.mp3 · script.json
Writes: src/captions.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def words_faster_whisper(path: str, lang: str | None, model_name: str, cache: dict):
    from faster_whisper import WhisperModel

    if "model" not in cache:
        # int8 keeps this usable on a laptop CPU; the accuracy cost is not
        # audible at caption granularity.
        cache["model"] = WhisperModel(model_name, device="auto", compute_type="int8")
    segments, _ = cache["model"].transcribe(
        path, word_timestamps=True, language=lang, vad_filter=True,
    )
    for segment in segments:
        for word in segment.words or []:
            text = word.word.strip()
            if text:
                yield float(word.start), float(word.end), text


def words_whisper(path: str, lang: str | None, model_name: str, cache: dict):
    import whisper

    if "model" not in cache:
        cache["model"] = whisper.load_model(model_name)
    result = cache["model"].transcribe(path, word_timestamps=True, language=lang)
    for segment in result.get("segments", []):
        for word in segment.get("words", []):
            text = str(word.get("word", "")).strip()
            if text:
                yield float(word["start"]), float(word["end"]), text


def words_estimated(text: str, duration: float):
    """Spread the script's words evenly across the clip.

    Good enough to see the design working; not good enough to publish. Long
    words get the same time as short ones, so the highlight drifts.
    """
    tokens = [t for t in text.split() if t]
    if not tokens or duration <= 0:
        return
    step = duration / len(tokens)
    for index, token in enumerate(tokens):
        yield index * step, (index + 1) * step, token


def merge_orphans(words: list[dict]) -> list[dict]:
    """Glue bare symbols onto the word before them.

    Whisper writes spoken "eighty percent" back as "80" + "%", and a caption
    line whose whole job is showing a lone percent sign looks broken.
    """
    merged: list[dict] = []
    for word in words:
        bare = word["text"].strip()
        if merged and bare and all(not c.isalnum() for c in bare):
            merged[-1]["text"] += bare
            merged[-1]["end"] = word["end"]
            continue
        merged.append(word)
    return merged


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--engine", default="auto",
                        choices=["auto", "faster-whisper", "whisper", "estimate"])
    parser.add_argument("--model", default="base",
                        help="Whisper size: tiny, base, small, medium, large-v3")
    parser.add_argument("--lang", help="force a language code, e.g. es or en")
    args = parser.parse_args()

    timings_path = os.path.join(ROOT, "src", "timings.json")
    if not os.path.exists(timings_path):
        sys.exit("\n  No src/timings.json — run scripts/voice.py first.\n")

    timings = load(timings_path)
    script = load(os.path.join(ROOT, "script.json"))
    fps = timings.get("fps", 30)
    lang = args.lang or script.get("lang")
    text_by_id = {s["id"]: s["text"] for s in script.get("scenes", [])}

    engine = args.engine
    if engine == "auto":
        for candidate, module in (("faster-whisper", "faster_whisper"),
                                  ("whisper", "whisper")):
            try:
                __import__(module)
                engine = candidate
                break
            except ImportError:
                continue
        else:
            engine = "estimate"
            print("\n  Whisper is not installed — falling back to estimated "
                  "timings.\n  For real ones:  pip install faster-whisper\n")

    print(f"\n  Captions with: {engine}"
          + (f" ({args.model})" if engine.endswith("whisper") else "") + "\n")

    cache: dict = {}
    words: list[dict] = []
    offset = 0.0

    for scene in timings.get("scenes", []):
        audio_path = os.path.join(ROOT, "audio", scene["id"] + ".mp3")
        found = 0

        if engine == "estimate" or not os.path.exists(audio_path):
            source = words_estimated(text_by_id.get(scene["id"], ""),
                                     scene.get("audio", 0.0))
        elif engine == "faster-whisper":
            source = words_faster_whisper(audio_path, lang, args.model, cache)
        else:
            source = words_whisper(audio_path, lang, args.model, cache)

        for start, end, text in source:
            words.append({"start": round(offset + start, 3),
                          "end": round(offset + end, 3),
                          "text": text})
            found += 1

        print(f"  {scene['id']:<18} {found:4d} words")
        # The next scene starts where this one's *slot* ends, tail included —
        # that is what Video.tsx uses to place the sequence.
        offset += scene["frames"] / fps

    words = merge_orphans(words)

    out_path = os.path.join(ROOT, "src", "captions.json")
    with open(out_path, "w", encoding="utf-8") as handle:
        json.dump({"fps": fps, "words": words}, handle, indent=2,
                  ensure_ascii=False)

    print(f"\n  {len(words)} words -> src/captions.json")
    print("  Next:  npm run dev   (check a couple of scenes, then render)\n")


if __name__ == "__main__":
    main()
