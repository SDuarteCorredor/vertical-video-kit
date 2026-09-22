"""Generates the voice-over and measures how long each scene lasts.

Order matters: audio first, animation second. A scene is as long as its
narration actually takes, never as long as someone guessed. Change a line,
run this again, and every animation re-syncs itself.

    python scripts/voice.py                      # generate + measure
    python scripts/voice.py --only-measure       # re-measure existing files
    python scripts/voice.py --list-voices        # what your engine offers
    python scripts/voice.py --sample "Try this." # one file, to compare voices

Reads:  script.json
Writes: audio/<id>.mp3 · public/audio/<id>.mp3 · src/timings.json

Engines (set "engine" in script.json):
  voicestudio  local VoiceStudio app, best quality, free, no key  [default]
  edge         edge-tts, free, no install beyond pip, lower quality
  openai       needs OPENAI_API_KEY
  elevenlabs   needs ELEVENLABS_API_KEY
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request

from text_prep import guess_language, naturalize, split_pauses

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS = 30
VOICESTUDIO_URL = os.environ.get("VOICESTUDIO_URL", "http://localhost:3900")


# --------------------------------------------------------------------------- #
# helpers
# --------------------------------------------------------------------------- #

def die(message: str) -> None:
    sys.exit(f"\n  {message}\n")


def has_edge_tts() -> bool:
    try:
        import edge_tts  # noqa: F401
        return True
    except ImportError:
        return False


def rate_to_speed(rate: str | float | None) -> float:
    """'-3%' -> 0.97. Engines that take a multiplier instead of a percentage."""
    if rate is None:
        return 1.0
    if isinstance(rate, (int, float)):
        return float(rate)
    match = re.match(r"^\s*([+-]?\d+(?:\.\d+)?)\s*%\s*$", str(rate))
    return 1.0 + float(match.group(1)) / 100 if match else 1.0


def duration_of(path: str) -> float:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "csv=p=0", path],
        capture_output=True, text=True,
    ).stdout.strip()
    try:
        return float(out)
    except ValueError:
        return 0.0


def post_json(url: str, payload: dict, headers: dict) -> bytes:
    request = urllib.request.Request(
        url, data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", **headers},
    )
    with urllib.request.urlopen(request, timeout=300) as response:
        return response.read()


# --------------------------------------------------------------------------- #
# engines — each one takes plain text and returns mp3 bytes
# --------------------------------------------------------------------------- #

def synth_voicestudio(text: str, cfg: dict) -> bytes:
    try:
        return post_json(
            f"{VOICESTUDIO_URL}/v1/audio/speech",
            {
                "model": cfg.get("model", "tts-1"),
                "voice": cfg["voice"],
                "input": text,
                "response_format": "mp3",
                "speed": rate_to_speed(cfg.get("rate")),
            },
            {},
        )
    except urllib.error.URLError as err:
        die(f"VoiceStudio is not answering at {VOICESTUDIO_URL} ({err}).\n"
            f"  Open the VoiceStudio app and leave it running, or set\n"
            f'  "engine": "edge" in script.json to use the free fallback.')
        raise


def synth_edge(text: str, cfg: dict) -> bytes:
    try:
        import edge_tts
    except ImportError:
        die("edge-tts is missing. Install it with:  pip install edge-tts")
        raise

    import asyncio

    async def run() -> bytes:
        chunks = bytearray()
        communicate = edge_tts.Communicate(
            text, cfg["voice"], rate=str(cfg.get("rate", "+0%")),
        )
        async for item in communicate.stream():
            if item["type"] == "audio":
                chunks.extend(item["data"])
        return bytes(chunks)

    try:
        audio = asyncio.run(run())
    except Exception as err:
        # edge-tts talks to a Microsoft endpoint over a websocket, so it is the
        # one free engine that needs the internet — and the one that breaks on
        # a locked-down office network. The raw traceback is forty lines of
        # aiohttp and tells nobody what to do about it.
        detail = str(err) or type(err).__name__
        hint = ""
        if "CERTIFICATE" in detail.upper() or "SSL" in detail.upper():
            hint = ("\n  A certificate error usually means a corporate proxy is "
                    "inspecting\n  traffic. On a network like that, use the "
                    "'voicestudio' engine instead —\n  it runs on your own "
                    "machine and never leaves it.")
        elif "404" in detail or "invalid" in detail.lower():
            hint = (f"\n  Check that '{cfg['voice']}' is a real voice:  "
                    f"python scripts/voice.py --list-voices")
        die(f"edge-tts could not reach the voice service.\n"
            f"  {detail}\n{hint}")
        raise

    if not audio:
        die(f"edge-tts returned no audio for '{cfg['voice']}'.\n"
            f"  Usually the voice name is wrong. See:  "
            f"python scripts/voice.py --list-voices")
    return audio


def synth_openai(text: str, cfg: dict) -> bytes:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        die("OPENAI_API_KEY is not set.")
    return post_json(
        "https://api.openai.com/v1/audio/speech",
        {
            "model": cfg.get("model", "gpt-4o-mini-tts"),
            "voice": cfg["voice"],
            "input": text,
            "response_format": "mp3",
            "speed": rate_to_speed(cfg.get("rate")),
        },
        {"Authorization": f"Bearer {key}"},
    )


def synth_elevenlabs(text: str, cfg: dict) -> bytes:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        die("ELEVENLABS_API_KEY is not set.")
    return post_json(
        f"https://api.elevenlabs.io/v1/text-to-speech/{cfg['voice']}"
        f"?output_format=mp3_44100_128",
        {"text": text, "model_id": cfg.get("model", "eleven_multilingual_v2")},
        {"xi-api-key": key},
    )


ENGINES = {
    "voicestudio": synth_voicestudio,
    "edge": synth_edge,
    "openai": synth_openai,
    "elevenlabs": synth_elevenlabs,
}

# Where edge-tts lands when VoiceStudio is the configured engine but the app
# isn't open. VoiceStudio voice names ("af_heart") mean nothing to edge-tts, so
# falling back has to pick a voice too.
EDGE_DEFAULTS = {
    "es": "es-CO-SalomeNeural",
    "en": "en-US-AriaNeural",
    "pt": "pt-BR-FranciscaNeural",
    "fr": "fr-FR-DeniseNeural",
    "de": "de-DE-KatjaNeural",
    "it": "it-IT-ElsaNeural",
}

EDGE_VOICE_PATTERN = re.compile(r"^[a-z]{2}-[A-Z]{2}-\w+$")


def voicestudio_reachable() -> bool:
    try:
        urllib.request.urlopen(f"{VOICESTUDIO_URL}/v1/audio/voices", timeout=4).close()
        return True
    except Exception:
        return False


def fall_back_to_edge(cfg: dict, lang: str) -> None:
    """Swap a dead VoiceStudio for edge-tts rather than stopping the run.

    Someone who cloned the repo an hour ago has not installed a desktop app,
    and dying here is the difference between a video and an error message.
    Loud about it, because the two engines do not sound the same.
    """
    cfg["engine"] = "edge"
    if not EDGE_VOICE_PATTERN.match(cfg.get("voice") or ""):
        cfg["voice"] = EDGE_DEFAULTS.get(lang, EDGE_DEFAULTS["en"])
    cfg["model"] = None
    print(f"""
  VoiceStudio is not answering at {VOICESTUDIO_URL}, so this is using
  edge-tts with {cfg['voice']} instead. It works, it just sounds more
  synthetic.

  To keep it: set "engine": "edge" in script.json.
  For the better voice: open the VoiceStudio app and run this again.
""")


# --------------------------------------------------------------------------- #
# synthesis with real pauses
# --------------------------------------------------------------------------- #

def render_line(text: str, dest: str, cfg: dict) -> None:
    """Synthesize one narration line, honouring any [pause:N] markers."""
    engine = ENGINES[cfg["engine"]]
    segments = split_pauses(text)

    if len(segments) == 1 and segments[0][1] == 0:
        with open(dest, "wb") as handle:
            handle.write(engine(segments[0][0], cfg))
        return

    with tempfile.TemporaryDirectory() as tmp:
        pieces: list[str] = []
        for index, (chunk, pause) in enumerate(segments):
            part = os.path.join(tmp, f"{index:03d}.mp3")
            with open(part, "wb") as handle:
                handle.write(engine(chunk, cfg))
            pieces.append(part)

            if pause > 0:
                gap = os.path.join(tmp, f"{index:03d}-gap.mp3")
                subprocess.run(
                    ["ffmpeg", "-v", "error", "-y", "-f", "lavfi",
                     "-i", "anullsrc=r=44100:cl=mono", "-t", str(pause),
                     "-c:a", "libmp3lame", gap],
                    check=True,
                )
                pieces.append(gap)

        listing = os.path.join(tmp, "list.txt")
        with open(listing, "w", encoding="utf-8") as handle:
            for piece in pieces:
                handle.write(f"file '{piece.replace(os.sep, '/')}'\n")

        # Re-encoded, not stream-copied: the engine and the silence generator
        # rarely agree on sample rate, and a copy would desync the audio.
        subprocess.run(
            ["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0",
             "-i", listing, "-c:a", "libmp3lame", "-q:a", "2", dest],
            check=True,
        )


def list_voices(engine: str) -> None:
    if engine == "voicestudio":
        try:
            with urllib.request.urlopen(
                f"{VOICESTUDIO_URL}/v1/audio/voices", timeout=30,
            ) as response:
                data = json.load(response)
        except urllib.error.URLError as err:
            die(f"VoiceStudio is not answering at {VOICESTUDIO_URL} ({err}). "
                f"Open the app first.")
            return
        print(json.dumps(data, indent=2, ensure_ascii=False))
    elif engine == "edge":
        subprocess.run([sys.executable, "-m", "edge_tts", "--list-voices"])
    else:
        print(f"  Voice lists for '{engine}' live in that provider's docs.")


# --------------------------------------------------------------------------- #

def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--only-measure", action="store_true",
                        help="don't regenerate, just re-read the existing mp3 "
                             "durations (use after swapping in a human recording)")
    parser.add_argument("--list-voices", action="store_true")
    parser.add_argument("--sample", metavar="TEXT",
                        help="synthesize one line to sample.mp3 and stop")
    parser.add_argument("--engine", help="override the engine in script.json")
    parser.add_argument("--voice", help="override the voice in script.json")
    parser.add_argument("--raw", action="store_true",
                        help="skip the text normalization (debugging)")
    args = parser.parse_args()

    if not shutil.which("ffprobe") or not shutil.which("ffmpeg"):
        die("FFmpeg is missing. Install it and reopen the terminal.")

    script_path = os.path.join(ROOT, "script.json")
    if not os.path.exists(script_path):
        die(f"No script.json at {script_path}")

    with open(script_path, encoding="utf-8") as handle:
        script = json.load(handle)

    cfg = {
        "engine": args.engine or script.get("engine", "voicestudio"),
        "voice": args.voice or script.get("voice", ""),
        "model": script.get("model"),
        "rate": script.get("rate", "+0%"),
    }
    if cfg["engine"] not in ENGINES:
        die(f"Unknown engine '{cfg['engine']}'. "
            f"Pick one of: {', '.join(ENGINES)}")

    if args.list_voices:
        list_voices(cfg["engine"])
        return

    lang = guess_language(cfg["voice"], script.get("lang"))

    # An explicit --engine is a decision; the default in script.json is not.
    if cfg["engine"] == "voicestudio" and not args.engine and not args.only_measure:
        if not voicestudio_reachable() and has_edge_tts():
            fall_back_to_edge(cfg, lang)
            lang = guess_language(cfg["voice"], script.get("lang"))

    prepare = (lambda t: t) if args.raw else (lambda t: naturalize(t, lang))

    if args.sample:
        dest = os.path.join(ROOT, "sample.mp3")
        render_line(prepare(args.sample), dest, cfg)
        print(f"\n  {dest}  ({cfg['engine']} / {cfg['voice']})\n")
        return

    if not cfg["voice"]:
        die('script.json has no "voice". Run --list-voices to see your options.')

    audio_dir = os.path.join(ROOT, "audio")
    public_dir = os.path.join(ROOT, "public", "audio")
    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(public_dir, exist_ok=True)

    tail = float(script.get("tailSeconds", 0.35))
    print(f"\n  {cfg['engine']} · {cfg['voice']} · {cfg['rate']} · lang={lang}\n"
          if not args.only_measure else "\n  Measuring existing audio.\n")

    timings, total = [], 0.0
    for scene in script["scenes"]:
        dest = os.path.join(audio_dir, scene["id"] + ".mp3")

        if args.only_measure:
            if not os.path.exists(dest):
                die(f"Missing {dest} — nothing to measure.")
        else:
            render_line(prepare(scene["text"]), dest, cfg)

        shutil.copy(dest, os.path.join(public_dir, scene["id"] + ".mp3"))

        seconds = duration_of(dest)
        frames = int(round((seconds + tail) * FPS))
        timings.append({"id": scene["id"], "audio": round(seconds, 3),
                        "frames": frames})
        total += seconds + tail
        print(f"  {scene['id']:<18} {seconds:6.2f}s  ->  {frames:4d} frames")

    with open(os.path.join(ROOT, "src", "timings.json"), "w",
              encoding="utf-8") as handle:
        json.dump(
            {"fps": FPS, "scenes": timings,
             "totalFrames": sum(t["frames"] for t in timings)},
            handle, indent=2, ensure_ascii=False,
        )

    minutes, seconds = divmod(total, 60)
    print(f"\n  TOTAL {int(minutes)}:{seconds:04.1f}")
    if total > 90:
        print("  Over 90s — long for a short. Consider cutting a scene.")
    print("\n  Next:  python scripts/captions.py\n")


if __name__ == "__main__":
    main()
