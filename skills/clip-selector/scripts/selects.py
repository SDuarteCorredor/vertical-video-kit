"""Turn a clip selection into something Premiere Pro opens: a selects sequence.

    python scripts/selects.py selects.json
    python scripts/selects.py selects.json --media-root "D:/Video/raw"

Reads selects.json (written by the selector, see SKILL.md) and writes, next
to it:

    <name>.xml        Final Cut Pro 7 XML (xmeml). In Premiere: File > Import.
                      A bin with one sequence, "<name> SELECTS": every chosen
                      clip in order, cut at its in/out, with a marker on each
                      carrying the label, the rating and why it was chosen.
                      The whole source file stays linked, so the editor can
                      roll any edit outward — nothing is lost at the cut.
    <name>.csv        the same list for a spreadsheet: file, in, out, timecodes
    <name>.md         the same list for a person to read

The XML points at the media by absolute path. If it is generated on another
machine than the one Premiere runs on, pass --media-root with the folder that
holds the files there; each clip is then looked up by its file name in it.
If Premiere still shows a clip offline, right-click > Link Media and point at
the folder once: it finds the rest.
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import subprocess
import sys
from fractions import Fraction
from pathlib import Path, PurePosixPath, PureWindowsPath
from urllib.parse import quote
from xml.sax.saxutils import escape

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Premiere's label colours for clips, by the rating the selector gave them.
LABEL_BY_RATING = {5: "Forest", 4: "Caribbean", 3: "Mango", 2: "Rose", 1: "Violet"}

ALIASES = {  # the Spanish keys are accepted too, like the rest of the kit
    "clips": ("clips", "tomas"), "file": ("file", "archivo"),
    "in": ("in", "inicio", "entrada"), "out": ("out", "fin", "salida"),
    "label": ("label", "nombre", "etiqueta"), "why": ("why", "porque", "razon", "razón"),
    "rating": ("rating", "nota", "puntaje"), "role": ("role", "rol"),
}


def get(data: dict, key: str, default=None):
    for name in ALIASES.get(key, (key,)):
        if name in data:
            return data[name]
    return default


def seconds(value) -> float:
    """12.4, "12.4", "1:02.5" or "00:01:02:15@30" (timecode at a frame rate)."""
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if "@" in text:
        tc, rate = text.split("@", 1)
        h, m, s, f = (int(x) for x in tc.replace(";", ":").split(":"))
        return h * 3600 + m * 60 + s + f / float(rate)
    parts = [float(p) for p in text.split(":")]
    total = 0.0
    for part in parts:
        total = total * 60 + part
    return total


def probe(path: Path) -> dict:
    if not shutil.which("ffprobe"):
        return {}
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", str(path)],
        capture_output=True, text=True).stdout
    data = json.loads(out or "{}")
    video = next((s for s in data.get("streams", []) if s.get("codec_type") == "video"), {})
    audio = next((s for s in data.get("streams", []) if s.get("codec_type") == "audio"), {})
    rotation = 0
    for side in video.get("side_data_list", []) or []:
        if "rotation" in side:
            rotation = int(side["rotation"])
    width, height = video.get("width"), video.get("height")
    if rotation in (90, -90, 270, -270) and width and height:
        width, height = height, width
    return {
        "duration": float(data.get("format", {}).get("duration", 0) or 0),
        "rate": video.get("avg_frame_rate") or video.get("r_frame_rate"),
        "width": width, "height": height,
        "audio_channels": int(audio.get("channels", 0) or 0),
        "sample_rate": int(audio.get("sample_rate", 48000) or 48000),
    }


def xml_rate(rate_text: str | None, fallback: float) -> tuple[int, bool, float]:
    """(timebase, ntsc, real fps). 29.97 is timebase 30 with NTSC on."""
    try:
        real = float(Fraction(rate_text)) if rate_text and rate_text != "0/0" else fallback
    except (ValueError, ZeroDivisionError):
        real = fallback
    for nominal in (24, 30, 60, 120):
        if abs(real - nominal * 1000 / 1001) < 0.02:
            return nominal, True, nominal * 1000 / 1001
    base = max(1, round(real))
    return base, False, float(base)


def pathurl(path: str) -> str:
    """file://localhost/C:/Video/a%20b.mov or file://localhost/Users/me/a.mov"""
    text = path.replace("\\", "/")
    if len(text) > 1 and text[1] == ":":  # Windows drive
        text = "/" + text
    return "file://localhost" + quote(text, safe="/:")


def timecode(frames: int, base: int) -> str:
    ff = frames % base
    total = frames // base
    return f"{total // 3600:02d}:{total % 3600 // 60:02d}:{total % 60:02d}:{ff:02d}"


def rate_xml(base: int, ntsc: bool) -> str:
    return f"<rate><timebase>{base}</timebase><ntsc>{'TRUE' if ntsc else 'FALSE'}</ntsc></rate>"


def build(spec: dict, spec_dir: Path, media_root: str | None, seq_fps: float | None) -> tuple[str, list[dict]]:
    clips = get(spec, "clips", [])
    if not clips:
        sys.exit("\n  selects.json has no clips.\n")

    rows = []
    for index, clip in enumerate(clips, 1):
        file = get(clip, "file")
        if not file:
            sys.exit(f"\n  Clip {index} has no file.\n")
        local = (spec_dir / file) if not Path(file).is_absolute() else Path(file)
        info = probe(local) if local.exists() else {}
        if not local.exists():
            print(f"  ! {file} is not on this machine; its length and frame rate "
                  "are taken from selects.json")
        start, end = seconds(get(clip, "in")), seconds(get(clip, "out"))
        if end <= start:
            sys.exit(f"\n  Clip {index} ({file}) ends before it starts.\n")
        if info.get("duration") and end > info["duration"] + 0.05:
            sys.exit(f"\n  Clip {index} ({file}) ends at {end:.2f} s but the file is "
                     f"{info['duration']:.2f} s long.\n")
        if media_root:
            name = PureWindowsPath(file).name if "\\" in file else PurePosixPath(file).name
            sep = "\\" if "\\" in media_root else "/"
            target = media_root.rstrip("/\\") + sep + name
        else:
            target = str(local.resolve())
        rows.append({
            "n": index, "file": file, "target": target, "info": info,
            "start": start, "end": end,
            "label": str(get(clip, "label", f"Clip {index}")),
            "why": str(get(clip, "why", "")),
            "rating": int(get(clip, "rating", 0) or 0),
            "role": str(get(clip, "role", "")),
            "fps_hint": float(clip.get("fps", spec.get("fps", 30))),
            "duration_hint": float(clip.get("duration", 0) or 0),
        })

    first = rows[0]
    base, ntsc, real = xml_rate(first["info"].get("rate"), seq_fps or first["fps_hint"])
    if seq_fps:
        base, ntsc, real = xml_rate(str(seq_fps), seq_fps)
    width = int(spec.get("width") or first["info"].get("width") or 1920)
    height = int(spec.get("height") or first["info"].get("height") or 1080)
    name = str(spec.get("name") or spec.get("project") or "Selects")

    files_xml: dict[str, str] = {}
    video_items, audio_items = [], []
    cursor = 0
    gap = int(round(float(spec.get("gap", 0)) * real))  # optional black between clips
    seq_marker_list = []

    for row in rows:
        info = row["info"]
        fbase, fntsc, freal = xml_rate(info.get("rate"), row["fps_hint"])
        # In and out are in the clip's own frames; start and end on the timeline
        # are in the sequence's frames. Same rate in the usual case.
        clip_in = int(round(row["start"] * freal))
        clip_out = int(round(row["end"] * freal))
        length = int(round((row["end"] - row["start"]) * real))
        file_frames = int(round((info.get("duration") or row["duration_hint"]
                                 or row["end"]) * freal))
        row.update(tc_in=timecode(clip_in, fbase), tc_out=timecode(clip_out, fbase),
                   seq_tc=timecode(cursor, base))

        file_id = f"file-{len(files_xml) + 1}"
        key = row["target"]
        if key in files_xml:
            file_id = files_xml[key]
            file_xml = f'<file id="{file_id}"/>'
        else:
            files_xml[key] = file_id
            channels = info.get("audio_channels", 2) if info else 2
            audio_part = (
                f"<audio><samplecharacteristics><depth>16</depth>"
                f"<samplerate>{info.get('sample_rate', 48000) if info else 48000}</samplerate>"
                f"</samplecharacteristics><channelcount>{channels or 2}</channelcount></audio>"
            ) if channels else ""
            fname = escape(PureWindowsPath(key).name if "\\" in key else PurePosixPath(key).name)
            file_xml = (
                f'<file id="{file_id}"><name>{fname}</name>'
                f"<pathurl>{escape(pathurl(key))}</pathurl>{rate_xml(fbase, fntsc)}"
                f"<duration>{file_frames}</duration>"
                f"<timecode>{rate_xml(fbase, fntsc)}<string>00:00:00:00</string>"
                f"<frame>0</frame><displayformat>NDF</displayformat></timecode>"
                f"<media><video><samplecharacteristics>{rate_xml(fbase, fntsc)}"
                f"<width>{info.get('width') or width}</width>"
                f"<height>{info.get('height') or height}</height>"
                f"</samplecharacteristics></video>{audio_part}</media></file>")

        stars = "★" * row["rating"] if row["rating"] else ""
        marker_name = escape(f"{row['n']:02d} {row['label']}"[:120])
        comment = escape(" · ".join(x for x in (stars, row["role"], row["why"]) if x))
        # Marker on the clip, at its first frame: it travels with the clip when
        # the editor moves it around the timeline.
        marker = (f"<marker><name>{marker_name}</name><comment>{comment}</comment>"
                  f"<in>{clip_in}</in><out>-1</out></marker>")
        label = LABEL_BY_RATING.get(row["rating"])
        labels = f"<labels><label2>{label}</label2></labels>" if label else ""
        clip_name = escape(f"{row['n']:02d} {row['label']}"[:120])
        common = (f"<name>{clip_name}</name><enabled>TRUE</enabled>"
                  f"<duration>{file_frames}</duration>{rate_xml(fbase, fntsc)}"
                  f"<start>{cursor}</start><end>{cursor + length}</end>"
                  f"<in>{clip_in}</in><out>{clip_out}</out>")
        vid = f"clip-v{row['n']}"
        aud = [f"clip-a{row['n']}-{ch}" for ch in (1, 2)]
        has_audio = bool(info.get("audio_channels", 2)) if info else True
        links = ""
        if has_audio:
            links = (f"<link><linkclipref>{vid}</linkclipref><mediatype>video</mediatype>"
                     f"<trackindex>1</trackindex><clipindex>{row['n']}</clipindex></link>")
            for track, aid in enumerate(aud, 1):
                links += (f"<link><linkclipref>{aid}</linkclipref><mediatype>audio</mediatype>"
                          f"<trackindex>{track}</trackindex><clipindex>{row['n']}</clipindex>"
                          f"<groupindex>1</groupindex></link>")
        video_items.append(
            f'<clipitem id="{vid}">{common}{file_xml}{marker}{labels}{links}</clipitem>')
        if has_audio:
            for track, aid in enumerate(aud, 1):
                audio_items.append((track,
                    f'<clipitem id="{aid}">{common}<file id="{file_id}"/>'
                    f"<sourcetrack><mediatype>audio</mediatype><trackindex>{track}</trackindex>"
                    f"</sourcetrack>{labels}{links}</clipitem>"))
        # The same note on the sequence ruler, so the whole selection reads
        # as a list in the Markers panel without opening a single clip.
        seq_marker_list.append(f"<marker><name>{marker_name}</name><comment>{comment}</comment>"
                               f"<in>{cursor}</in><out>-1</out></marker>")
        cursor += length + gap

    seq_markers = "".join(seq_marker_list) if spec.get("sequence_markers", True) else ""

    tracks_audio = "".join(
        "<track>" + "".join(item for t, item in audio_items if t == track) + "</track>"
        for track in (1, 2)) if audio_items else ""
    sample = rows[0]["info"].get("sample_rate", 48000) if rows[0]["info"] else 48000
    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4">'
        f"<bin><name>{escape(name)}</name><children>"
        f'<sequence id="sequence-1"><name>{escape(name)} SELECTS</name>'
        f"<duration>{cursor}</duration>{rate_xml(base, ntsc)}"
        f"<timecode>{rate_xml(base, ntsc)}<string>00:00:00:00</string><frame>0</frame>"
        f"<displayformat>NDF</displayformat></timecode>"
        f"<media><video><format><samplecharacteristics>{rate_xml(base, ntsc)}"
        f"<width>{width}</width><height>{height}</height>"
        f"<pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format>"
        f"<track>{''.join(video_items)}</track></video>"
        f"<audio><format><samplecharacteristics><depth>16</depth><samplerate>{sample}"
        f"</samplerate></samplecharacteristics></format>{tracks_audio}</audio></media>"
        f"{seq_markers}</sequence></children></bin></xmeml>\n")
    return xml, rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("selects", help="selects.json")
    parser.add_argument("--media-root",
                        help="folder that holds the media on the machine Premiere runs on")
    parser.add_argument("--fps", type=float,
                        help="sequence frame rate (default: the first clip's)")
    parser.add_argument("--out", help="output name without extension (default: next to the json)")
    args = parser.parse_args()

    spec_path = Path(args.selects)
    if not spec_path.exists():
        sys.exit(f"\n  Not found: {spec_path}\n")
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    xml, rows = build(spec, spec_path.parent, args.media_root, args.fps)

    stem = Path(args.out) if args.out else spec_path.with_suffix("")
    stem.parent.mkdir(parents=True, exist_ok=True)
    stem.with_suffix(".xml").write_text(xml, encoding="utf-8")

    with open(stem.with_suffix(".csv"), "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["#", "file", "in_s", "out_s", "length_s", "tc_in", "tc_out",
                         "rating", "role", "label", "why"])
        for r in rows:
            writer.writerow([r["n"], r["file"], f"{r['start']:.2f}", f"{r['end']:.2f}",
                             f"{r['end'] - r['start']:.2f}", r["tc_in"], r["tc_out"],
                             r["rating"], r["role"], r["label"], r["why"]])

    total = sum(r["end"] - r["start"] for r in rows)
    md = [f"# {spec.get('name') or 'Selects'}\n",
          f"{len(rows)} clips · {total:.0f} s in total · import `{stem.with_suffix('.xml').name}`"
          " in Premiere (File > Import)\n",
          "| # | File | In | Out | Length | ★ | Role | Clip | Why |", "|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        md.append(f"| {r['n']} | {r['file']} | {r['tc_in']} | {r['tc_out']} | "
                  f"{r['end'] - r['start']:.1f} s | {r['rating'] or ''} | {r['role']} | "
                  f"{r['label']} | {r['why']} |")
    stem.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"\n  {len(rows)} clips, {total:.1f} s")
    for r in rows:
        print(f"  {r['n']:>2}. {r['tc_in']} → {r['tc_out']}  {r['file']}  {r['label']}")
    print(f"\n  {stem.with_suffix('.xml')}   ← Premiere: File > Import")
    print(f"  {stem.with_suffix('.md')}  ·  {stem.with_suffix('.csv')}\n")


if __name__ == "__main__":
    main()
