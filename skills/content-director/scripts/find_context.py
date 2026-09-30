"""Finds brand and content context already on disk, so nobody is asked twice.

    python find_context.py                 # current folder + common places
    python find_context.py ~/Desktop/marca ~/Documents

Lists (never reads out loud) files that look like brand manuals, voice/tone
guides, agent instructions, previous scripts, reference folders and
transcripts, newest first. The agent then reads the relevant ones.
"""
from __future__ import annotations
import os, sys, time
from pathlib import Path

PATTERNS = {
    "agent instructions": ["claude.md", "agents.md"],
    "brand / manual": ["marca", "brand", "manual", "brandbook", "identidad", "guidelines", "brand-profile"],
    "voice / tone": ["tono", "tone", "voice", "voz", "estilo"],
    "strategy / calendar": ["calendario", "calendar", "pilares", "pillars", "estrategia", "strategy", "content-plan"],
    "scripts / captions": ["guion", "guiones", "script", "caption", "copy", "reels.md"],
    "references": ["referente", "reference", "inspo", "benchmark", "competencia", "competitor"],
    "content-director workspace": ["contenido/marca.md", "contenido/reglas.md", "contenido/sistema.md"],
}
EXTS = {".md", ".txt", ".pdf", ".docx", ".json", ".csv", ".key", ".pptx"}
SKIP = {"node_modules", ".git", ".venv", "venv", "__pycache__", "Library", ".cache", "dist", "build"}

def scan(root: Path, depth: int = 5):
    root = root.expanduser()
    if not root.exists():
        return
    base = len(root.parts)
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP and (not d.startswith(".") or d == ".context")]
        if len(Path(dirpath).parts) - base >= depth:
            dirnames[:] = []
        for f in filenames:
            p = Path(dirpath) / f
            if p.suffix.lower() not in EXTS:
                continue
            if "/private/" in str(p) and "private" in str(root):
                yield "private/ (read all of it first)", p
                continue
            name, low = p.name.lower(), str(p).lower()
            kind = next((k for k, keys in PATTERNS.items() if any(x in name for x in keys)), None) \
                or next((k for k, keys in PATTERNS.items() if any(x in low for x in keys)), None)
            if kind:
                yield kind, p

def main() -> None:
    roots = [Path(a) for a in sys.argv[1:]] or [Path.cwd() / "private", Path.cwd(), Path("~/Desktop"), Path("~/Documents"), Path("~/Downloads")]
    found: dict[str, list[Path]] = {}
    seen = set()
    for r in roots:
        for kind, p in scan(r):
            if p in seen:
                continue
            seen.add(p); found.setdefault(kind, []).append(p)
    if not found:
        print("No brand or content files found. Start the diagnosis from zero.")
        return
    for kind, paths in found.items():
        paths.sort(key=lambda p: p.stat().st_mtime, reverse=True)
        print(f"\n## {kind} ({len(paths)})")
        for p in paths[:15]:
            age = (time.time() - p.stat().st_mtime) / 86400
            print(f"  {p}   ({age:.0f} d)")
        if len(paths) > 15:
            print(f"  … {len(paths) - 15} more")

if __name__ == "__main__":
    main()
