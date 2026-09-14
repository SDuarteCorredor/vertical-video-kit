"""Turns written text into text a speech engine reads well.

Most "robotic TTS" is not the engine's fault. It is text written to be read
with the eyes being fed to something that reads with a mouth: acronyms it
spells as words, symbols it skips, sentences with no punctuation to breathe
between. Fixing the text is cheaper and more effective than switching engines.

Everything here is conservative. It never rewrites your wording — it only
changes how the same words get pronounced.

Used by voice.py; also runnable on its own to preview the result:

    python scripts/text_prep.py "Our ROI grew 40% in Q1."
"""
from __future__ import annotations

import re
import sys

# Uppercase words that are read as words, not spelled out letter by letter.
# Add your own domain's here — a wrong guess is very audible.
SAID_AS_WORDS = {
    "NASA", "NATO", "UNESCO", "UNICEF", "OK", "AI", "API", "URL", "SEO",
    "RAM", "PDF", "GIF", "JPEG", "PNG", "HTML", "CSS", "SQL", "USA", "UK",
    "IVA", "ONU", "OTAN", "PYME",
}

SYMBOLS = {
    "en": [("%", " percent"), ("&", " and "), ("+", " plus "), ("@", " at "),
           ("#", " number "), ("=", " equals "), ("€", " euros"), ("$", " dollars")],
    "es": [("%", " por ciento"), ("&", " y "), ("+", " más "), ("@", " arroba "),
           ("#", " número "), ("=", " igual a "), ("€", " euros"), ("$", " pesos")],
}

PAUSE = re.compile(r"\[pause:\s*([0-9]*\.?[0-9]+)\s*\]", re.IGNORECASE)


def guess_language(voice: str, declared: str | None = None) -> str:
    """Language code used for symbol expansion. Declared value always wins."""
    if declared:
        return declared[:2].lower()
    match = re.match(r"([a-z]{2})[-_]", voice or "")
    return match.group(1).lower() if match else "en"


def _spell_acronym(match: re.Match[str]) -> str:
    word = match.group(0)
    if word in SAID_AS_WORDS:
        return word
    # "E P S" is read letter by letter; "EPS" is read as a nonsense word.
    return " ".join(word)


def naturalize(text: str, lang: str = "en", spell_acronyms: bool = True) -> str:
    """Rewrite `text` for the ear. Returns text with [pause:N] markers intact."""
    out = text.strip()

    # Em dashes and ellipses are read as nothing at all. Commas are read as a
    # breath, which is what they were standing in for anyway.
    out = out.replace("…", ", ").replace("—", ", ").replace("–", ", ")
    out = re.sub(r"\.{3,}", ", ", out)

    for symbol, spoken in SYMBOLS.get(lang, SYMBOLS["en"]):
        out = out.replace(symbol, spoken)

    # "example.com" -> "example dot com", otherwise it comes out as one word.
    out = re.sub(r"\b([\w-]+)\.(com|net|org|io|co|dev|app|ai)\b",
                 r"\1 dot \2", out, flags=re.IGNORECASE)

    if spell_acronyms:
        out = re.sub(r"\b[A-ZÁÉÍÓÚÑ]{2,5}\b", _spell_acronym, out)

    out = re.sub(r"[ \t]+", " ", out)
    out = re.sub(r"\s+([,.;:!?])", r"\1", out)
    out = out.strip()

    # A line with no final punctuation gets read with a rising, unfinished
    # intonation, and the next scene then starts on top of it.
    if out and out[-1] not in ".!?:,":
        out += "."
    return out


def split_pauses(text: str) -> list[tuple[str, float]]:
    """Split on [pause:N] markers into (chunk, silence_after_seconds) pairs.

    Engines that ignore SSML still get real pauses this way: each chunk is
    synthesized separately and the silence is inserted between them.
    """
    parts: list[tuple[str, float]] = []
    cursor = 0
    for match in PAUSE.finditer(text):
        chunk = text[cursor:match.start()].strip()
        if chunk:
            parts.append((chunk, float(match.group(1))))
        cursor = match.end()
    tail = text[cursor:].strip()
    if tail:
        parts.append((tail, 0.0))
    return parts or [(text.strip(), 0.0)]


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    source = " ".join(sys.argv[1:]) or "Our ROI grew 40% in Q1. Visit example.com"
    print(naturalize(source, guess_language("", None)))
