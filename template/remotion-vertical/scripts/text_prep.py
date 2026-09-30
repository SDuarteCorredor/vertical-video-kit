"""Turns written text into text a speech engine reads well.

Most "robotic TTS" is not the engine's fault. It is text written to be read
with the eyes being fed to something that reads with a mouth: acronyms it
spells as words, symbols it skips, sentences with no punctuation to breathe
between. Fixing the text is cheaper and more effective than switching engines.

Everything here is conservative. It never rewrites your wording — it only
changes how the same words get pronounced.

Used by voice.py; also runnable on its own to preview the result:

    python scripts/text_prep.py "Our ROI grew 40% in Q1."
    python scripts/text_prep.py --lang es "Precio: $1.500.000 COP/mes"
"""
from __future__ import annotations

import re
import sys

# Uppercase words that are read as words, not spelled out letter by letter.
# Add your own domain's here — a wrong guess is very audible.
SAID_AS_WORDS = {
    "NASA", "NATO", "UNESCO", "UNICEF", "OK", "AI", "API", "URL", "SEO",
    "RAM", "PDF", "GIF", "JPEG", "PNG", "HTML", "CSS", "SQL", "USA", "UK",
    "IVA", "ONU", "OTAN", "PYME", "PYMES",
    # Colombian institutions and documents said as one word, not spelled.
    "DIAN", "SENA", "SOAT", "NIT", "RUT", "DANE", "ICETEX",
}

# Written abbreviations with internal dots. The acronym rule below would see
# "RR" and "HH" in "RR.HH." and spell them, which is gibberish out loud.
ABBREVIATIONS = {
    "es": {
        "RR.HH.": "recursos humanos", "EE.UU.": "Estados Unidos",
        "Ltda.": "limitada", "Cía.": "compañía",
        "Dr.": "doctor", "Dra.": "doctora", "Sr.": "señor", "Sra.": "señora",
        "N.°": "número", "Nº": "número",
    },
    "en": {
        "e.g.": "for example", "i.e.": "that is", "vs.": "versus",
        "etc.": "et cetera",
    },
}

CURRENCY = {
    "es": {"$": "pesos", "COP": "pesos", "USD": "dólares", "US$": "dólares",
           "€": "euros", "EUR": "euros", "MXN": "pesos mexicanos"},
    "en": {"$": "dollars", "USD": "dollars", "US$": "dollars", "€": "euros",
           "EUR": "euros", "COP": "Colombian pesos", "MXN": "Mexican pesos"},
}

# "/mes" is read as "barra mes" by most engines.
PER = {
    "es": {"mes": "al mes", "año": "al año", "día": "al día", "hora": "por hora",
           "semana": "a la semana", "persona": "por persona", "usuario": "por usuario"},
    "en": {"mo": "a month", "month": "a month", "yr": "a year", "year": "a year",
           "day": "a day", "hr": "an hour", "hour": "an hour", "week": "a week",
           "user": "per user", "person": "per person"},
}

DOT = {"es": "punto", "en": "dot"}
TLDS = ("com", "net", "org", "io", "co", "dev", "app", "ai", "gov", "edu", "info")

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


def _currency(text: str, lang: str) -> str:
    """ "$1.500.000 COP" -> "1.500.000 pesos". The symbol is written first
    but said last, and a code after it is the same money said twice."""
    names = CURRENCY.get(lang, CURRENCY["en"])
    codes = "|".join(re.escape(c) for c in names if c.isalpha())
    number = r"(\d[\d.,]*\d|\d)"

    def spoken(symbol: str | None, code: str | None) -> str:
        return names.get(code or "", "") or names.get(symbol or "", "")

    text = re.sub(
        r"(US\$|\$|€)\s?" + number + r"(?:\s?(" + codes + r")\b)?",
        lambda m: f"{m.group(2)} {spoken(m.group(1), m.group(3))}",
        text,
    )
    return re.sub(
        number + r"\s?(" + codes + r")\b",
        lambda m: f"{m.group(1)} {names[m.group(2)]}",
        text,
    )


def _spell_acronym(match: re.Match[str]) -> str:
    word = match.group(0)
    if word in SAID_AS_WORDS:
        return word
    # "E P S" is read letter by letter; "EPS" is read as a nonsense word.
    return " ".join(word)


def naturalize(text: str, lang: str = "en", spell_acronyms: bool = True) -> str:
    """Rewrite `text` for the ear. Returns text with [pause:N] markers intact."""
    out = text.strip()

    table = lang if lang in SYMBOLS else "en"

    for written, spoken in ABBREVIATIONS.get(table, {}).items():
        out = re.sub(r"(?<![\w.])" + re.escape(written) + r"(?!\w)", spoken, out)

    out = _currency(out, table)

    # "48h" -> "48 horas", "24/7" -> said the way people say it, "/mes" -> "al mes".
    hours = "horas" if table == "es" else "hours"
    out = re.sub(r"\b24/7\b", "veinticuatro siete" if table == "es" else "twenty-four seven", out)
    out = re.sub(r"\b(\d+)\s?h\b", r"\1 " + hours, out)
    for unit, spoken in PER.get(table, {}).items():
        out = re.sub(r"\s?/\s?" + unit + r"\b", " " + spoken, out)
    if table == "es":
        # "Q3" means nothing said aloud in Spanish; "tercer trimestre" does.
        for n, word in (("1", "primer"), ("2", "segundo"), ("3", "tercer"), ("4", "cuarto")):
            out = re.sub(r"\bQ" + n + r"\b", word + " trimestre", out)

    # Em dashes and ellipses are read as nothing at all. Commas are read as a
    # breath, which is what they were standing in for anyway.
    out = out.replace("…", ", ").replace("—", ", ").replace("–", ", ")
    out = re.sub(r"\.{3,}", ", ", out)

    for symbol, spoken in SYMBOLS[table]:
        out = out.replace(symbol, spoken)

    # "asignar.com.co" -> "asignar punto com punto co"; otherwise it comes out
    # as one word. Every label must hold a letter, so "1.500.000" is left alone.
    dot = f" {DOT.get(table, 'dot')} "
    out = re.sub(
        r"\b[a-z0-9-]*[a-z][a-z0-9-]*(?:\.[a-z0-9-]*[a-z][a-z0-9-]*)*\.(?:"
        + "|".join(TLDS) + r")(?:\.[a-z]{2})?\b",
        lambda m: m.group(0).replace(".", dot),
        out, flags=re.IGNORECASE,
    )

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
    import json
    import os

    args = sys.argv[1:]
    lang = None
    if len(args) >= 2 and args[0] == "--lang":
        lang, args = args[1], args[2:]
    if lang is None:
        # Preview in the project's language, the one voice.py will use —
        # otherwise a Spanish project previews "Colombian pesos".
        script = os.path.join(os.path.dirname(os.path.dirname(
            os.path.abspath(__file__))), "script.json")
        try:
            with open(script, encoding="utf-8") as handle:
                data = json.load(handle)
            lang = guess_language(data.get("voice", ""), data.get("lang"))
        except (OSError, ValueError):
            lang = "en"
    source = " ".join(args) or "Our ROI grew 40% in Q1. Visit example.com"
    print(naturalize(source, lang))
