"""Downloads reference reels (Instagram, TikTok, YouTube Shorts) with their metadata.

    python fetch_refs.py links.txt --out contenido/referentes
    python fetch_refs.py URL1 URL2 --out contenido/referentes
    python fetch_refs.py links.txt --meta-only        # caption, likes, comments, no video

Accepts full URLs or bare Instagram codes (DdAt7STCr3x). Strips tracking tails
(?stkn=, ?igsh=). Carousels of videos land as <id>_00001.mp4, _00002…
Writes resumen.md (one row per post) next to the files. Sleeps between requests.
Restricted/private posts are reported, not forced.
"""
from __future__ import annotations
import argparse, json, re, subprocess, sys, time
from pathlib import Path

def normalize(item: str) -> str:
    item = item.strip()
    if not item or item.startswith("#"):
        return ""
    if re.fullmatch(r"[A-Za-z0-9_-]{9,14}", item):
        return f"https://www.instagram.com/reel/{item}/"
    return re.sub(r"[?&](stkn|igsh|igshid|utm_[a-z]+)=[^&]*", "", item).rstrip("?&")

def ytdlp() -> list[str]:
    return [sys.executable, "-m", "yt_dlp"]

def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("items", nargs="+", help="links.txt files and/or URLs/codes")
    ap.add_argument("--out", default="contenido/referentes")
    ap.add_argument("--meta-only", action="store_true")
    ap.add_argument("--sleep", type=float, default=2.0)
    a = ap.parse_args()
    urls: list[str] = []
    for it in a.items:
        p = Path(it)
        lines = p.read_text().splitlines() if p.exists() else [it]
        urls += [u for u in (normalize(l) for l in lines) if u]
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    failed = []
    for i, u in enumerate(urls, 1):
        cmd = ytdlp() + ["-q", "--no-warnings", "--socket-timeout", "60", "--write-info-json",
                         "-o", str(out / "%(id)s_%(autonumber)s.%(ext)s")]
        cmd += ["--skip-download"] if a.meta_only else ["-f", "b[ext=mp4]/b"]
        r = subprocess.run(cmd + [u], capture_output=True, text=True)
        if r.returncode != 0:
            msg = (r.stderr.strip().splitlines() or ["error"])[-1]
            if "timed out" in msg:
                time.sleep(3); r = subprocess.run(cmd + [u], capture_output=True, text=True)
            if r.returncode != 0:
                reason = "restricted (age/audience): ask for a screen recording" if "available to everyone" in msg else msg[:160]
                failed.append((u, reason))
        print(f"  [{i}/{len(urls)}] {'ok' if r.returncode == 0 else 'FAILED'}  {u}")
        time.sleep(a.sleep)
    rows = []
    for f in sorted(out.glob("*.info.json")):
        d = json.loads(f.read_text())
        if d.get("_type") == "playlist":
            continue
        rows.append(d)
    lines = ["# Referentes — resumen", "", "| id | cuenta | dur | likes | coment. | fecha | caption |", "|---|---|---|---|---|---|---|"]
    seen = set()
    for d in rows:
        key = d.get("id")
        if key in seen:
            continue
        seen.add(key)
        dur = d.get("duration")
        if not dur:
            vid = next(iter(sorted(out.glob(f"{key}_*.mp4"))), None)
            if vid:
                try:
                    dur = float(subprocess.check_output(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                                                         "-of", "csv=p=0", str(vid)]).strip())
                except Exception:
                    dur = None
        cap = (d.get("description") or "").replace("\n", " / ").replace("|", "/")[:140]
        lines.append(f"| {key} | @{d.get('channel') or d.get('uploader_id')} | {int(dur) if dur else '?'} | "
                     f"{d.get('like_count')} | {d.get('comment_count')} | {d.get('upload_date')} | {cap} |")
    if failed:
        lines += ["", "## No descargados", ""] + [f"- {u} — {why}" for u, why in failed]
    (out / "resumen.md").write_text("\n".join(lines) + "\n")
    print(f"\n  {len(seen)} posts in {out}/resumen.md" + (f", {len(failed)} failed" if failed else ""))
    print("  Note: likes can read as 3 when the creator hides them; views are only visible on the profile grid.")

if __name__ == "__main__":
    main()
