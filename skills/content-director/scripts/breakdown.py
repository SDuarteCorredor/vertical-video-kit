"""Shot-by-shot breakdown of every reference video in a folder.

    python breakdown.py contenido/referentes
    python breakdown.py contenido/referentes --lang es --model small
    python breakdown.py contenido/referentes --no-transcript

For each video it writes to <folder>/analisis/:
  <id>_tomas.jpg     one labelled frame per detected cut  (#n start (length))
  <id>_timeline.jpg  a frame every 1.5-3 s  -- catches graphics inside one take
  <id>_tomas.json    cuts, per-shot brightness/saturation/palette, aspect, fps
  <id>_voz.json      transcript with timestamps + words per minute
and a comparison table in <folder>/analisis/resumen_tomas.md.

Look at every sheet yourself afterwards: numbers find cuts, eyes find typography,
stickers, chapter cards and light. Skips videos already analysed.
"""
from __future__ import annotations
import argparse, json, re, statistics as st, subprocess, sys
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def font(size: int = 22):
    for p in ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "C:/Windows/Fonts/arialbd.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    try:
        return ImageFont.load_default(size)
    except TypeError:
        return ImageFont.load_default()
FONT = font()

def probe(p: Path) -> dict:
    o = json.loads(subprocess.check_output(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries",
        "stream=width,height,r_frame_rate,color_transfer:format=duration", "-of", "json", str(p)]))
    s = (o.get("streams") or [{}])[0]; w, h = s.get("width", 0), s.get("height", 1)
    num, _, den = (s.get("r_frame_rate") or "0/1").partition("/")
    r = w / h if h else 0
    aspect = "9:16" if r < 0.6 else "3:4/4:5" if r < 0.9 else "1:1" if r < 1.1 else "4:3" if r < 1.45 else "16:9"
    return {"duration": float(o["format"].get("duration", 0)), "width": w, "height": h, "aspect": aspect,
            "fps": round(float(num) / float(den or 1), 2), "hdr": s.get("color_transfer") in ("arib-std-b67", "smpte2084")}

def cuts(p: Path, th: float) -> list[float]:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(p), "-vf", f"select='gt(scene,{th})',showinfo",
                          "-an", "-f", "null", "-"], capture_output=True, text=True).stderr
    return [float(x) for x in re.findall(r"pts_time:([0-9.]+)", err)]

def frame(p: Path, t: float, w: int) -> Image.Image:
    for tt in (t, max(0, t - 0.3), max(0, t - 1.0)):
        try:
            raw = subprocess.check_output(["ffmpeg", "-v", "error", "-ss", f"{tt:.2f}", "-i", str(p), "-frames:v", "1",
                                           "-vf", f"scale={w}:-2", "-f", "image2pipe", "-vcodec", "png", "-"])
            return Image.open(BytesIO(raw)).convert("RGB")
        except Exception:
            pass
    return Image.new("RGB", (w, int(w * 16 / 9)))

def stats(img: Image.Image):
    small = img.resize((80, max(1, int(80 * img.height / img.width))))
    hsv = small.convert("HSV")
    px = list(hsv.get_flattened_data() if hasattr(hsv, "get_flattened_data") else hsv.getdata())
    pal = (small.quantize(5).getpalette() or [])[:15]
    return (round(sum(v for *_, v in px) / len(px) / 255, 2), round(sum(s for _, s, _ in px) / len(px) / 255, 2),
            ["#%02x%02x%02x" % tuple(pal[i:i + 3]) for i in range(0, len(pal) - 2, 3)])

def sheet(imgs, labels, path: Path, cols: int = 8):
    if not imgs:
        return
    w, h = imgs[0].size; rows = (len(imgs) + cols - 1) // cols
    sh = Image.new("RGB", (min(cols, len(imgs)) * (w + 4), rows * (h + 30)), (20, 20, 20)); d = ImageDraw.Draw(sh)
    for i, (im, lab) in enumerate(zip(imgs, labels)):
        x, y = (i % cols) * (w + 4), (i // cols) * (h + 30)
        sh.paste(im.resize((w, h)), (x, y + 28)); d.text((x + 4, y + 3), lab, font=FONT, fill=(255, 230, 120))
    sh.save(path, quality=82)

def transcribe(p: Path, model, lang: str | None) -> dict:
    segs, info = model.transcribe(str(p), language=lang, word_timestamps=False, vad_filter=True)
    tr = [{"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()} for s in segs]
    words = sum(len(t["text"].split()) for t in tr); spoken = sum(t["end"] - t["start"] for t in tr)
    return {"language": info.language, "wordsPerMinute": round(words / spoken * 60, 1) if spoken > 3 else 0,
            "hook": " ".join(t["text"] for t in tr if t["start"] < 3.5), "transcript": tr}

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder"); ap.add_argument("--lang"); ap.add_argument("--model", default="small")
    ap.add_argument("--threshold", type=float, default=0.28); ap.add_argument("--no-transcript", action="store_true")
    a = ap.parse_args()
    folder = Path(a.folder); out = folder / "analisis"; out.mkdir(exist_ok=True)
    vids = sorted([*folder.glob("*.mp4"), *folder.glob("*.mov"), *folder.glob("*.MOV"), *folder.glob("*.MP4")])
    model = None
    if not a.no_transcript:
        try:
            from faster_whisper import WhisperModel
            model = WhisperModel(a.model, device="auto", compute_type="int8")
        except Exception as e:
            print(f"  (no transcripts: {e})")
    rows = []
    for v in vids:
        j = out / f"{v.stem}_tomas.json"
        if j.exists():
            rows.append(json.loads(j.read_text())); continue
        info = probe(v); D = info["duration"]
        c = cuts(v, a.threshold); c = [t for i, t in enumerate(c) if i == 0 or t - c[i - 1] > 0.25]
        b = [0.0] + c + [D]
        shots = [{"start": round(x, 2), "end": round(y, 2), "len": round(y - x, 2)} for x, y in zip(b, b[1:]) if y - x >= 0.15]
        imgs = []
        for s in shots[:40]:
            im = frame(v, s["start"] + s["len"] / 2, 240); s["luma"], s["sat"], s["palette"] = stats(im); imgs.append(im)
        sheet(imgs, [f"#{i+1} {s['start']:.1f}s ({s['len']:.1f})" for i, s in enumerate(shots[:40])], out / f"{v.stem}_tomas.jpg")
        n = min(32, max(8, int(D / 1.5))); ts = [D / n * (i + 0.5) for i in range(n)]
        sheet([frame(v, t, 260) for t in ts], [f"{t:.1f}s" for t in ts], out / f"{v.stem}_timeline.jpg")
        lens = [s["len"] for s in shots] or [D]
        rec = {"file": v.name, **info, "shots": len(shots), "avg_shot": round(st.mean(lens), 2),
               "luma": round(st.mean([s["luma"] for s in shots if "luma" in s] or [0]), 2),
               "sat": round(st.mean([s["sat"] for s in shots if "sat" in s] or [0]), 2), "shot_list": shots}
        if model:
            try:
                vo = transcribe(v, model, a.lang); (out / f"{v.stem}_voz.json").write_text(json.dumps(vo, ensure_ascii=False, indent=1))
                rec["wpm"] = vo["wordsPerMinute"]; rec["hook"] = vo["hook"]
            except Exception as e:
                rec["wpm"] = None; print(f"  transcript failed for {v.name}: {e}")
        j.write_text(json.dumps(rec, ensure_ascii=False, indent=1)); rows.append(rec)
        print(f"  {v.name:32s} {D:6.1f}s {info['aspect']:7s} tomas={len(shots):3d} prom={rec['avg_shot']:.1f}s wpm={rec.get('wpm')}"
              + ("  HDR" if info["hdr"] else ""))
    if rows:
        md = ["# Resumen toma por toma", "", "| archivo | dur | formato | fps | tomas | toma prom | luz | sat | wpm | gancho |",
              "|---|---|---|---|---|---|---|---|---|---|"]
        for r in rows:
            md.append(f"| {r['file']} | {r['duration']:.0f} | {r['aspect']} | {r['fps']} | {r['shots']} | {r['avg_shot']} | "
                      f"{r['luma']} | {r['sat']} | {r.get('wpm')} | {(r.get('hook') or '').replace('|','/')[:80]} |")
        one = sum(1 for r in rows if r["shots"] <= 2)
        md += ["", f"Mediana de duración: {st.median(r['duration'] for r in rows):.0f} s · "
                   f"una o dos tomas de cámara: {one}/{len(rows)} · formatos: "
                   + ", ".join(f"{k} {sum(1 for r in rows if r['aspect']==k)}" for k in sorted({r['aspect'] for r in rows}))]
        (out / "resumen_tomas.md").write_text("\n".join(md) + "\n")
        print(f"\n  {out}/resumen_tomas.md — now LOOK at every *_timeline.jpg and write the cards.")

if __name__ == "__main__":
    main()
