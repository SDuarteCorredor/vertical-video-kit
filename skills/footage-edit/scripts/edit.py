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
     "stabilize": true}
  ]
}

The Spanish keys from the original workspace (salida, tomas, archivo, inicio,
duracion, rotar, cruce, zoom_vel, estabilizar...) are accepted too.

Why each step is the way it is:
- Rotation happens BEFORE stabilizing: vidstab removes shake, not a fixed tilt.
- A stabilized clip looks locked-off and flat. The slow push-in gives it life
  back, and also pushes clutter at the edges (mugs, bottles on a desk) out of
  frame — aim x/y away from whatever should not be seen.
- The push-in is scale(eval=frame) + a fixed-size crop, because crop cannot
  animate its own width and height over time, only its position.
- vidstab gets relative paths: a Windows path with "C:" breaks the filter
  parser, so every step runs with the work folder as its cwd.
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
    "brillo": "brightness",
}

COLOR = {"contrast": 1.08, "saturation": 1.18, "brightness": 0.02, "gamma": 1.03}


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
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", str(path)], capture_output=True, text=True).stdout
    return float(out.strip() or 0)


def has_vidstab() -> bool:
    out = subprocess.run(["ffmpeg", "-hide_banner", "-filters"],
                         capture_output=True, text=True).stdout
    return "vidstabdetect" in out


def process(i: int, clip: dict, base: Path, work: Path, cfg: dict, stabilize_ok: bool) -> Path:
    n = f"{i:02d}"
    W, H = cfg.get("width", 1080), cfg.get("height", 1920)
    c = {**COLOR, **cfg.get("color", {})}
    raw = f"clip{n}_raw.mp4"

    pre = [f"rotate={clip['rotate']}*PI/180:c=black"] if clip.get("rotate") else []
    vf = ["-vf", ",".join(pre)] if pre else []
    run(["ffmpeg", "-y", "-ss", str(clip.get("start", 0)), "-i", str(base / clip["file"]),
         "-t", str(clip["duration"]), "-an", *vf,
         "-c:v", "libx264", "-crf", "16", "-preset", "veryfast", "-pix_fmt", "yuv420p", raw],
        cwd=work)

    chain = []
    if clip.get("stabilize", True) and stabilize_ok:
        run(["ffmpeg", "-y", "-i", raw, "-vf",
             f"vidstabdetect=shakiness=6:accuracy=15:result=clip{n}.trf", "-f", "null", "-"],
            cwd=work)
        chain.append(f"vidstabtransform=input=clip{n}.trf:zoom=0:optzoom=1:smoothing=15:crop=black")

    z0, zv = clip.get("zoom", 1.06), clip.get("zoom_speed", 0.025)
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
    run(["ffmpeg", "-y", "-i", raw, "-vf", ",".join(chain), "-an",
         "-c:v", "libx264", "-crf", "16", "-preset", "slow", done], cwd=work)
    return work / done


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
    if music:
        args += ["-i", str(music)]
        fade_at = max(expected - 1.5, 0)
        graph.append(f"[{len(clips)}:a]atrim=0:{expected:.3f},"
                     f"afade=t=out:st={fade_at:.3f}:d=1.5[aout]")
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
