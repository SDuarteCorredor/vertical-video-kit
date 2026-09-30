"""Turns phone footage into one vertical video: trim, straighten, stabilize,
slow push-in, color, crossfades. FFmpeg only — no Remotion, no Node.

    python scripts/edit.py edit.json
    python scripts/edit.py edit.json --join-only     # reuse clips already processed

edit.json (paths are relative to the json file):

{
  "output": "output/video.mp4",
  "width": 1080, "height": 1920, "fps": 30,
  "crossfade": 0.5,
  "color": {"contrast": 1.08, "saturation": 1.18, "brightness": 0.02, "gamma": 1.03},
  "music": "music.mp3",            optional; faded out at the end
  "clips": [
    {"file": "raw/take1.mp4", "start": 6.2, "duration": 4.5,
     "rotate": -3,                 degrees; negative turns left. Try -2/-3/-4 on a still
     "zoom": 1.09,                 starting push-in (1.0 = none)
     "zoom_speed": 0.035,          how much it pushes in per second
     "x": 0.5, "y": 0.15,          where it pushes toward: 0 = left/top, 1 = right/bottom
     "stabilize": true},
    {"file": "raw/testimonial.mp4", "start": 12.0, "duration": 18.0,
     "audio": true}                keep what this take says; the rest stay silent
  ]
}

The Spanish keys from the original workspace (salida, tomas, archivo, inicio,
duracion, rotar, cruce, zoom_vel, estabilizar, audio/voz/sonido...) are
accepted too.

Why each step is the way it is:
- Rotation happens BEFORE stabilizing: vidstab removes shake, not a fixed tilt.
- A stabilized clip looks locked-off and flat. The slow push-in gives it life
  back, and also pushes clutter at the edges (mugs, bottles on a desk) out of
  frame — aim x/y away from whatever should not be seen.
- The push-in is scale(eval=frame) + a fixed-size crop, because crop cannot
  animate its own width and height over time, only its position.
- vidstab gets relative paths: a Windows path with "C:" breaks the filter
  parser, so every step runs with the work folder as its cwd.
- Clips are silent unless they ask for "audio": room sound from five takes
  never matches, but a testimonial without its voice is not a testimonial.
  Kept audio is loudness-normalised per clip, so two speakers recorded at
  different distances land at the same level, and crossfades with the
  picture. Music ducks under it rather than fighting it.
- A take that keeps its audio pushes in far more slowly by default. The
  standard 2.5%/s suits a 4-second shot; over an 18-second testimonial it
  ends 45% closer, on someone's nose.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SPANISH = {
    "salida": "output", "ancho": "width", "alto": "height", "cruce": "crossfade",
    "tomas": "clips", "musica": "music", "música": "music",
    "archivo": "file", "inicio": "start", "duracion": "duration", "duración": "duration",
    "rotar": "rotate", "zoom_vel": "zoom_speed", "estabilizar": "stabilize",
    "contraste": "contrast", "saturacion": "saturation", "saturación": "saturation",
    "brillo": "brightness", "voz": "audio", "sonido": "audio",
}

COLOR = {"contrast": 1.08, "saturation": 1.18, "brightness": 0.02, "gamma": 1.03}

# Spoken-word target, the same one publish.py uses for narration.
LOUDNESS = "loudnorm=I=-16:TP=-1.5:LRA=11"
AUDIO_FORMAT = "aformat=sample_rates=48000:channel_layouts=stereo"
RATE = 48000


def fit(seconds: float) -> str:
    """Filters that make audio exactly `seconds` long: pad with silence,
    then cut by sample count. Cutting by time does not work here — loudnorm
    leaves gaps in the timestamps, and a time-based atrim comes up ~0.1s
    short per clip, which shifts every crossfade after it."""
    return f"asetpts=N/SR/TB,apad,atrim=end_sample={round(seconds * RATE)}"


def english(value):
    if isinstance(value, dict):
        return {SPANISH.get(k, k): english(v) for k, v in value.items()}
    if isinstance(value, list):
        return [english(v) for v in value]
    return value


def run(args: list[str], cwd: Path | None = None) -> None:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(result.stderr[-2500:])
        sys.exit(f"\n  Failed: {' '.join(map(str, args[:6]))} ...\n")


def duration(path: Path) -> float:
    """Length of the picture. The container's length is the longer of video
    and audio, and the crossfades have to follow the picture."""
    for query in (["-select_streams", "v:0", "-show_entries", "stream=duration"],
                  ["-show_entries", "format=duration"]):
        out = subprocess.run(["ffprobe", "-v", "error", *query, "-of", "csv=p=0",
                              str(path)], capture_output=True, text=True).stdout
        try:
            return float(out.strip().splitlines()[0])
        except (ValueError, IndexError):
            continue
    return 0.0


def has_audio(path: Path) -> bool:
    out = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "a",
                          "-show_entries", "stream=index", "-of", "csv=p=0", str(path)],
                         capture_output=True, text=True).stdout
    return bool(out.strip())


def has_vidstab() -> bool:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"],
                         capture_output=True, text=True).stdout
    return "vidstabdetect" in out


def process(i: int, clip: dict, base: Path, work: Path, cfg: dict, stabilize_ok: bool) -> Path:
    n = f"{i:02d}"
    W, H = cfg.get("width", 1080), cfg.get("height", 1920)
    c = {**COLOR, **cfg.get("color", {})}
    raw = f"clip{n}_raw.mp4"
    source = base / clip["file"]

    keep = bool(clip.get("audio"))
    if keep and not has_audio(source):
        print(f"    {clip['file']} has no sound to keep — using it silent.")
        keep = False
    # Only video filters run on the clip, so its sound stays in sync through
    # rotate, stabilize and the push-in without any extra work.
    sound = ["-c:a", "aac", "-b:a", "192k"] if keep else ["-an"]

    pre = [f"rotate={clip['rotate']}*PI/180:c=black"] if clip.get("rotate") else []
    vf = ["-vf", ",".join(pre)] if pre else []
    run(["ffmpeg", "-y", "-ss", str(clip.get("start", 0)), "-i", str(source),
         "-t", str(clip["duration"]), *sound, *vf,
         "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", raw],
        cwd=work)

    chain = []
    if clip.get("stabilize", True) and stabilize_ok:
        run(["ffmpeg", "-y", "-i", raw, "-vf",
             f"vidstabdetect=shakiness=6:accuracy=15:result=clip{n}.trf", "-f", "null", "-"],
            cwd=work)
        chain.append(f"vidstabtransform=input=clip{n}.trf:zoom=0:optzoom=1:smoothing=15:crop=black")

    z0 = clip.get("zoom", 1.06)
    zv = clip.get("zoom_speed", 0.008 if keep else 0.025)
    x, y = clip.get("x", 0.5), clip.get("y", 0.2)
    chain += [
        # Cover the frame first, so horizontal or odd-sized footage is cropped
        # instead of squashed.
        f"scale={W}:{H}:force_original_aspect_ratio=increase:flags=lanczos",
        f"crop={W}:{H}",
        f"scale=w='{W}*({z0}+{zv}*t)':h='{H}*({z0}+{zv}*t)':eval=frame:flags=lanczos",
        f"crop=w={W}:h={H}:x='(in_w-{W})*{x}':y='(in_h-{H})*{y}'",
        "unsharp=5:5:0.5",
        f"eq=contrast={c['contrast']}:saturation={c['saturation']}"
        f":brightness={c['brightness']}:gamma={c['gamma']}",
        "setsar=1",
        "format=yuv420p",
    ]
    done = f"clip{n}_done.mp4"
    # The sound ends exactly where the picture does: a clip whose audio
    # outlasts or undershoots its video throws every crossfade after it off.
    sound = (["-af", f"{LOUDNESS},{AUDIO_FORMAT},{fit(duration(work / raw))}",
              "-c:a", "aac", "-b:a", "192k"] if keep else ["-an"])
    run(["ffmpeg", "-y", "-i", raw, "-vf", ",".join(chain), *sound,
         "-c:v", "libx264", "-crf", "16", "-preset", "slow", done], cwd=work)
    return work / done


def speech_track(clips: list[Path], lengths: list[float], crossfade: float,
                 graph: list[str]) -> bool:
    """Add a [speech] label joining every clip's own sound, or return False.

    Silent clips get silence of their exact length, so the audio crossfades
    line up with the picture's one for one. When no clip kept its sound
    there is nothing to add, and the edit behaves exactly as it always has.
    """
    kept = [has_audio(c) for c in clips]
    if not any(kept):
        return False
    for k, (clip_has, length) in enumerate(zip(kept, lengths)):
        source = f"[{k}:a]" if clip_has else f"anullsrc=r={RATE}:cl=stereo,"
        graph.append(f"{source}{AUDIO_FORMAT},{fit(length)}[a{k}]")
    if len(clips) == 1:
        graph.append("[a0]anull[speech]")
    elif crossfade > 0.01:
        prev = "a0"
        for k in range(1, len(clips)):
            label = "speech" if k == len(clips) - 1 else f"ax{k}"
            graph.append(f"[{prev}][a{k}]acrossfade=d={crossfade}:c1=tri:c2=tri[{label}]")
            prev = label
    else:
        joined = "".join(f"[a{k}]" for k in range(len(clips)))
        graph.append(f"{joined}concat=n={len(clips)}:v=0:a=1[speech]")
    return True


def join(clips: list[Path], out: Path, crossfade: float, fps: int, music: Path | None) -> None:
    lengths = [duration(c) for c in clips]
    inputs, graph, prev, offset = [], [], "0:v", 0.0
    for c in clips:
        inputs += ["-i", str(c)]
    for k in range(1, len(clips)):
        offset += lengths[k - 1] - crossfade
        label = "vout" if k == len(clips) - 1 else f"v{k}"
        graph.append(f"[{prev}][{k}:v]xfade=transition=fade:duration={crossfade}"
                     f":offset={offset:.4f}[{label}]")
        prev = label
    expected = sum(lengths) - crossfade * (len(lengths) - 1)

    args = ["ffmpeg", "-y", *inputs]
    maps = ["-map", "[vout]" if len(clips) > 1 else "0:v"]
    speech = speech_track(clips, lengths, crossfade, graph)
    fade_at = max(expected - 1.5, 0)
    if music:
        args += ["-i", str(music)]
        graph.append(f"[{len(clips)}:a]{AUDIO_FORMAT},{fit(expected)},"
                     f"afade=t=out:st={fade_at:.3f}:d=1.5[music]")
        if speech:
            # Music at a bed level, pushed down further whenever someone
            # speaks and back up in the gaps, instead of two tracks at once.
            graph.append("[speech]asplit=2[say][key]")
            graph.append("[music]volume=0.35[bed]")
            graph.append("[bed][key]sidechaincompress=threshold=0.02:ratio=8"
                         ":attack=30:release=500[ducked]")
            graph.append("[say][ducked]amix=inputs=2:duration=first:normalize=0,"
                         f"{fit(expected)}[aout]")
        else:
            graph.append("[music]anull[aout]")
    elif speech:
        graph.append(f"[speech]{fit(expected)}[aout]")
    if music or speech:
        maps += ["-map", "[aout]", "-c:a", "aac", "-b:a", "192k"]
    if graph:
        args += ["-filter_complex", ";".join(graph)]
    out.parent.mkdir(parents=True, exist_ok=True)
    args += [*maps, "-r", str(fps), "-c:v", "libx264", "-crf", "17", "-preset", "slow",
             "-pix_fmt", "yuv420p", "-movflags", "+faststart", str(out)]
    run(args)
    print(f"\n  {out}   {duration(out):.2f}s (expected {expected:.2f}s)\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("config")
    parser.add_argument("--join-only", "--solo-unir", action="store_true",
                        help="reuse clips already processed in work/")
    args = parser.parse_args()

    if not shutil.which("ffmpeg"):
        sys.exit("\n  FFmpeg is missing. See docs/NO-AGENT.md.\n")

    cfg_path = Path(args.config).resolve()
    cfg = english(json.loads(cfg_path.read_text(encoding="utf-8-sig")))
    base = cfg_path.parent
    work = base / "work"
    work.mkdir(exist_ok=True)

    stabilize_ok = has_vidstab()
    if not stabilize_ok and any(c.get("stabilize", True) for c in cfg["clips"]):
        print("  This FFmpeg was built without vidstab: clips will not be stabilized.\n"
              "  The Gyan (Windows), Homebrew and apt builds all include it.\n")

    done = []
    for i, clip in enumerate(cfg["clips"], 1):
        ready = work / f"clip{i:02d}_done.mp4"
        if args.join_only and ready.exists():
            done.append(ready)
            continue
        print(f"  Clip {i}/{len(cfg['clips'])}: {clip['file']}")
        done.append(process(i, clip, base, work, cfg, stabilize_ok))

    music = base / cfg["music"] if cfg.get("music") else None
    join(done, base / cfg.get("output", "output/video.mp4"),
         cfg.get("crossfade", 0.5), cfg.get("fps", 30), music)


if __name__ == "__main__":
    main()
