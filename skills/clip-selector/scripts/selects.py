"""Turn a clip selection into something Premiere opens: a selects sequence.

    python scripts/selects.py selects.json
    python scripts/selects.py selects.json --media-root "D:/Video/raw"

Reads selects.json (written by the selector, see SKILL.md) and writes, next
to it:

    <name>.xml        Final Cut Pro 7 XML (xmeml). In Premiere: File > Import.
                      A bin holding "<name> SELECTS": every chosen clip in
                      order on V1, cut at its in/out, alternates ("role":
                      "alt") disabled on V2 above the clip they could replace,
                      a marker on each with the role, label, stars and reason,
                      and a colour label by rating. Plus one stringout
                      sequence per "group", if any. The whole source file
                      stays linked, so the editor can roll any edit outward.
    <name>.csv        the same list for a spreadsheet
    <name>.md         the same list for a person to read
    <name>.otio       only with opentimelineio installed: the XML is read
                      back to check every clip made it, and saved as OTIO too

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
    "group": ("group", "grupo", "tema"),
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
    nominal, average = video.get("r_frame_rate"), video.get("avg_frame_rate")
    try:
        vfr = abs(float(Fraction(nominal)) - float(Fraction(average))) > 0.05
    except (TypeError, ValueError, ZeroDivisionError):
        vfr = False
    return {
        "duration": float(data.get("format", {}).get("duration", 0) or 0),
        "rate": average if average and average != "0/0" else nominal,
        "vfr": vfr,
        "width": width, "height": height,
        "audio_channels": int(audio.get("channels", 0) or 0),
        "sample_rate": int(audio.get("sample_rate", 48000) or 48000),
    }


STANDARD_RATES = [(24, True), (24, False), (25, False), (30, True), (30, False),
                  (50, False), (60, True), (60, False), (120, False)]


def xml_rate(rate_text: str | None, fallback: float) -> tuple[int, bool, float]:
    """(timebase, ntsc, real fps). 29.97 is timebase 30 with NTSC on.

    Phone footage averages slightly off its nominal rate (29.87 for a 29.97
    recording): a rate within 2% of a standard one snaps to it."""
    try:
        real = float(Fraction(rate_text)) if rate_text and rate_text != "0/0" else fallback
    except (ValueError, ZeroDivisionError):
        real = fallback
    best = min(STANDARD_RATES,
               key=lambda r: abs(real - (r[0] * 1000 / 1001 if r[1] else r[0])))
    best_real = best[0] * 1000 / 1001 if best[1] else float(best[0])
    if abs(real - best_real) / best_real <= 0.02:
        return best[0], best[1], best_real
    base = max(1, round(real))
    return base, False, float(base)


def pathurl(path: str) -> str:
    """file://localhost/D%3a/Video/a%20b.mov or file://localhost/Users/me/a.mov

    The Windows form, colon encoded as %3a, is copied from Premiere's own XML
    export: what Premiere writes is what it reads back most reliably."""
    text = path.replace("\\", "/")
    if len(text) > 1 and text[1] == ":":  # Windows drive
        return "file://localhost/" + text[0] + "%3a" + quote(text[2:], safe="/")
    return "file://localhost" + quote(text, safe="/")


def timecode(frames: int, base: int) -> str:
    ff = frames % base
    total = frames // base
    return f"{total // 3600:02d}:{total % 3600 // 60:02d}:{total % 60:02d}:{ff:02d}"


def rate_xml(base: int, ntsc: bool) -> str:
    return f"<rate><timebase>{base}</timebase><ntsc>{'TRUE' if ntsc else 'FALSE'}</ntsc></rate>"


def load_rows(spec: dict, spec_dir: Path, media_root: str | None) -> list[dict]:
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
        fbase, fntsc, freal = xml_rate(info.get("rate"),
                                       float(clip.get("fps", spec.get("fps", 30))))
        rows.append({
            "n": index, "file": file, "target": target, "info": info,
            "start": start, "end": end,
            "label": str(get(clip, "label", f"Clip {index}")),
            "why": str(get(clip, "why", "")),
            "rating": int(get(clip, "rating", 0) or 0),
            "role": str(get(clip, "role", "")).strip().lower(),
            "group": str(get(clip, "group", "") or "").strip(),
            "fbase": fbase, "fntsc": fntsc, "freal": freal,
            "file_frames": int(round((info.get("duration") or float(clip.get("duration", 0) or 0)
                                      or end) * freal)),
            "clip_in": int(round(start * freal)), "clip_out": int(round(end * freal)),
        })
        rows[-1]["tc_in"] = timecode(rows[-1]["clip_in"], fbase)
        rows[-1]["tc_out"] = timecode(rows[-1]["clip_out"], fbase)
    return rows


class Writer:
    """Builds xmeml sequences that share one set of <file> definitions."""

    def __init__(self) -> None:
        self.files: dict[str, str] = {}
        self.ids = 0

    def file_xml(self, row: dict, width: int, height: int) -> str:
        key = row["target"]
        if key in self.files:
            return f'<file id="{self.files[key]}"/>'
        file_id = f"file-{len(self.files) + 1}"
        self.files[key] = file_id
        info, rate = row["info"], rate_xml(row["fbase"], row["fntsc"])
        channels = info.get("audio_channels", 2) if info else 2
        audio = (f"<audio><samplecharacteristics><depth>16</depth>"
                 f"<samplerate>{info.get('sample_rate', 48000) if info else 48000}</samplerate>"
                 f"</samplecharacteristics><channelcount>{channels}</channelcount></audio>"
                 ) if channels else ""
        name = escape(PureWindowsPath(key).name if "\\" in key else PurePosixPath(key).name)
        return (f'<file id="{file_id}"><name>{name}</name>'
                f"<pathurl>{escape(pathurl(key))}</pathurl>{rate}"
                f"<duration>{row['file_frames']}</duration>"
                f"<timecode>{rate}<string>00:00:00:00</string><frame>0</frame>"
                f"<displayformat>NDF</displayformat></timecode>"
                f"<media><video><samplecharacteristics>{rate}"
                f"<width>{info.get('width') or width}</width>"
                f"<height>{info.get('height') or height}</height>"
                f"</samplecharacteristics></video>{audio}</media></file>")

    def sequence(self, title: str, placed: list[tuple[dict, int, int, bool]],
                 base: int, ntsc: bool, width: int, height: int, sample: int) -> str:
        """placed: (row, timeline start, layer, enabled). Layer 0 is V1 + A1/A2,
        layer 1 is V2 + A3/A4: alternates sit right above the clip they replace."""
        real = base * 1000 / 1001 if ntsc else float(base)
        layers = max(layer for _, _, layer, _ in placed) + 1
        video = [[] for _ in range(layers)]
        audio = [[] for _ in range(layers * 2)]
        markers, end_of_sequence = [], 0
        rate = rate_xml(base, ntsc)
        for row, start, layer, enabled in placed:
            self.ids += 1
            length = int(round((row["end"] - row["start"]) * real))
            end_of_sequence = max(end_of_sequence, start + length)
            stars = "★" * row["rating"] if row["rating"] else ""
            # Marker colours can't be set from XML; the role in capitals, in the
            # name, is what the editor scans for in the Markers panel.
            role = f" {row['role'].upper()} –" if row["role"] else ""
            title_text = escape(f"{row['n']:02d}{role} {row['label']}"[:120])
            comment = escape(" · ".join(x for x in (stars, row["role"], row["why"]) if x))
            label = LABEL_BY_RATING.get(row["rating"])
            labels = f"<labels><label2>{label}</label2></labels>" if label else ""
            on = "TRUE" if enabled else "FALSE"
            common = (f"<name>{title_text}</name><enabled>{on}</enabled>"
                      f"<duration>{row['file_frames']}</duration>{rate_xml(row['fbase'], row['fntsc'])}"
                      f"<start>{start}</start><end>{start + length}</end>"
                      f"<in>{row['clip_in']}</in><out>{row['clip_out']}</out>")
            vid = f"clip-{self.ids}-v"
            has_audio = bool(row["info"].get("audio_channels", 2)) if row["info"] else True
            aids = [f"clip-{self.ids}-a{ch}" for ch in (1, 2)] if has_audio else []
            links = ""
            if aids:
                links = (f"<link><linkclipref>{vid}</linkclipref><mediatype>video</mediatype>"
                         f"<trackindex>{layer + 1}</trackindex>"
                         f"<clipindex>{len(video[layer]) + 1}</clipindex></link>")
                for ch, aid in enumerate(aids):
                    track = layer * 2 + ch
                    links += (f"<link><linkclipref>{aid}</linkclipref><mediatype>audio</mediatype>"
                              f"<trackindex>{track + 1}</trackindex>"
                              f"<clipindex>{len(audio[track]) + 1}</clipindex>"
                              f"<groupindex>1</groupindex></link>")
            # The marker sits on the clip, so the note travels with it when the
            # editor moves it; a copy on the ruler lists the whole selection in
            # the Markers panel.
            marker = (f"<marker><name>{title_text}</name><comment>{comment}</comment>"
                      f"<in>{row['clip_in']}</in><out>-1</out></marker>")
            video[layer].append(f'<clipitem id="{vid}">{common}'
                                f"{self.file_xml(row, width, height)}{marker}{labels}{links}"
                                f"</clipitem>")
            for ch, aid in enumerate(aids):
                audio[layer * 2 + ch].append(
                    f'<clipitem id="{aid}">{common}<file id="{self.files[row["target"]]}"/>'
                    f"<sourcetrack><mediatype>audio</mediatype><trackindex>{ch + 1}</trackindex>"
                    f"</sourcetrack>{labels}{links}</clipitem>")
            if enabled:
                markers.append(f"<marker><name>{title_text}</name><comment>{comment}</comment>"
                               f"<in>{start}</in><out>-1</out></marker>")
        self.ids += 1
        return (f'<sequence id="sequence-{self.ids}"><name>{escape(title)}</name>'
                f"<duration>{end_of_sequence}</duration>{rate}"
                f"<timecode>{rate}<string>00:00:00:00</string><frame>0</frame>"
                f"<displayformat>NDF</displayformat></timecode>"
                f"<media><video><format><samplecharacteristics>{rate}"
                f"<width>{width}</width><height>{height}</height>"
                f"<pixelaspectratio>square</pixelaspectratio></samplecharacteristics></format>"
                + "".join(f"<track>{''.join(t)}</track>" for t in video)
                + f"</video><audio><format><samplecharacteristics><depth>16</depth>"
                f"<samplerate>{sample}</samplerate></samplecharacteristics></format>"
                + "".join(f"<track>{''.join(t)}</track>" for t in audio)
                + f"</audio></media>{''.join(markers)}</sequence>")


def build(spec: dict, rows: list[dict], seq_fps: float | None) -> str:
    first = rows[0]
    if seq_fps:
        base, ntsc, real = xml_rate(str(seq_fps), seq_fps)
    else:
        base, ntsc, real = first["fbase"], first["fntsc"], first["freal"]
    width = int(spec.get("width") or first["info"].get("width") or 1920)
    height = int(spec.get("height") or first["info"].get("height") or 1080)
    sample = (first["info"] or {}).get("sample_rate", 48000)
    name = str(spec.get("name") or spec.get("nombre") or spec.get("project") or "Selects")
    gap = int(round(float(spec.get("gap", 0)) * real))  # optional black between clips
    writer = Writer()

    # Selects: every clip in order on V1; an "alt" goes on V2, disabled, right
    # above the clip before it, so swapping takes is one click in Premiere.
    placed, cursor, parent_start = [], 0, 0
    for row in rows:
        if row["role"] == "alt" and placed:
            placed.append((row, parent_start, 1, False))
            continue
        parent_start = cursor
        placed.append((row, cursor, 0, True))
        cursor += int(round((row["end"] - row["start"]) * real)) + gap
    sequences = [writer.sequence(f"{name} SELECTS", placed, base, ntsc, width, height, sample)]

    # Stringouts: one sequence per group, everything in it end to end.
    groups: list[str] = []
    for row in rows:
        if row["group"] and row["group"] not in groups:
            groups.append(row["group"])
    for group in groups:
        placed, cursor = [], 0
        for row in (r for r in rows if r["group"] == group):
            placed.append((row, cursor, 0, True))
            cursor += int(round((row["end"] - row["start"]) * real)) + gap
        sequences.append(writer.sequence(f"{name} · {group}", placed, base, ntsc,
                                         width, height, sample))

    return ('<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE xmeml>\n<xmeml version="4">'
            f"<bin><name>{escape(name)}</name><children>{''.join(sequences)}"
            "</children></bin></xmeml>\n")


def spec_groups(rows: list[dict]) -> list[str]:
    seen: list[str] = []
    for row in rows:
        if row["group"] and row["group"] not in seen:
            seen.append(row["group"])
    return seen


def warn(rows: list[dict]) -> None:
    """Say what will go wrong in Premiere before the editor finds it there."""
    vfr = sorted({r["file"] for r in rows if r["info"].get("vfr")})
    if vfr:
        print("\n  ! Variable frame rate (phone footage): " + ", ".join(vfr))
        print("    In/out points can land a frame or two off and long clips drift out")
        print("    of sync in Premiere. Conform first and select from the copies:")
        print("    ffmpeg -i in.mov -fps_mode cfr -r 30000/1001 -c:v libx264 -crf 14 "
              "-c:a aac -b:a 256k in_cfr.mov")
    rates = sorted({(r["fbase"], r["fntsc"]) for r in rows})
    if len(rates) > 1:
        shown = ", ".join(f"{b * 1000 / 1001:.3f}" if n else str(b) for b, n in rates)
        print(f"\n  ! Mixed frame rates ({shown}). The sequence takes the first clip's;")
        print("    check the others land on the right frames, or conform them first.")


def check_and_write_otio(stem: Path, clip_count: int, sequence_count: int) -> str:
    """Read the XML back the way another program would, and write an .otio
    copy that Premiere 25.6+ opens too. Skipped if opentimelineio is missing."""
    try:
        import opentimelineio as otio
    except ImportError:
        return "(pip install opentimelineio otio-fcp-adapter to also check the XML and write .otio)"
    try:
        result = otio.adapters.read_from_file(str(stem.with_suffix(".xml")), adapter_name="fcp_xml")
    except Exception as err:  # noqa: BLE001 - any parse failure is the message
        sys.exit(f"\n  The XML did not read back: {err}\n")
    timelines = list(result) if isinstance(result, otio.schema.SerializableCollection) else [result]
    first = timelines[0]
    found = sum(1 for track in first.tracks if track.kind == "Video"
                for item in track if isinstance(item, otio.schema.Clip))
    if len(timelines) != sequence_count or found != clip_count:
        sys.exit(f"\n  The XML read back with {len(timelines)} sequences and {found} clips; "
                 f"expected {sequence_count} and {clip_count}.\n")
    otio.adapters.write_to_file(first, str(stem.with_suffix(".otio")))
    return f"{stem.with_suffix('.otio')}  (checked: the XML reads back with every clip)"


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
    rows = load_rows(spec, spec_path.parent, args.media_root)
    warn(rows)
    xml = build(spec, rows, args.fps)

    stem = Path(args.out) if args.out else spec_path.with_suffix("")
    stem.parent.mkdir(parents=True, exist_ok=True)
    stem.with_suffix(".xml").write_text(xml, encoding="utf-8")
    otio_note = check_and_write_otio(stem, len(rows), len(spec_groups(rows)) + 1)

    with open(stem.with_suffix(".csv"), "w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.writer(handle)
        writer.writerow(["#", "file", "in_s", "out_s", "length_s", "tc_in", "tc_out",
                         "rating", "role", "group", "label", "why"])
        for r in rows:
            writer.writerow([r["n"], r["file"], f"{r['start']:.2f}", f"{r['end']:.2f}",
                             f"{r['end'] - r['start']:.2f}", r["tc_in"], r["tc_out"],
                             r["rating"], r["role"], r["group"], r["label"], r["why"]])

    main_rows = [r for r in rows if r["role"] != "alt"]
    alts = len(rows) - len(main_rows)
    total = sum(r["end"] - r["start"] for r in main_rows)
    md = [f"# {spec.get('name') or spec.get('nombre') or 'Selects'}\n",
          f"{len(main_rows)} clips · {total:.0f} s on V1"
          + (f" · {alts} alternate{'s' if alts > 1 else ''} on V2, disabled" if alts else "")
          + f" · import `{stem.with_suffix('.xml').name}` in Premiere (File > Import)\n",
          "| # | File | In | Out | Length | ★ | Role | Group | Clip | Why |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        why = r["why"].replace("|", "/")
        md.append(f"| {r['n']} | {r['file']} | {r['tc_in']} | {r['tc_out']} | "
                  f"{r['end'] - r['start']:.1f} s | {r['rating'] or ''} | {r['role']} | "
                  f"{r['group']} | {r['label']} | {why} |")
    stem.with_suffix(".md").write_text("\n".join(md) + "\n", encoding="utf-8")

    print(f"\n  {len(main_rows)} clips, {total:.1f} s" + (f", {alts} alternates" if alts else ""))
    for r in rows:
        print(f"  {r['n']:>2}. {r['tc_in']} → {r['tc_out']}  {r['file']}  {r['label']}")
    print(f"\n  {stem.with_suffix('.xml')}   ← Premiere: File > Import")
    print(f"  {stem.with_suffix('.md')}  ·  {stem.with_suffix('.csv')}")
    print(f"  {otio_note}\n")


if __name__ == "__main__":
    main()
