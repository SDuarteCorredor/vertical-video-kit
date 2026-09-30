# content-director

A skill that turns Claude into a content director, community manager and
copywriter for short-form video — for any company or personal brand. It
diagnoses the brand, reads what already exists on disk, studies the reference
reels you send shot by shot, finds what overperformed in those accounts, and
only then proposes series and writes scripts you can film today.

## Install it in another Claude Code account

Only this skill, for Claude Code:

```bash
npx skills add SDuarteCorredor/vertical-video-kit@content-director -g -y -a claude-code
```

Then install its tools once (Python 3.12 recommended):

```bash
python3 -m pip install -U yt-dlp faster-whisper pillow
```

FFmpeg is also needed (`brew install ffmpeg` on macOS, `winget install Gyan.FFmpeg`
on Windows). The skill runs `scripts/setup_check.py` and tells you what is missing.

Or clone the whole kit (includes the video editing skills):

```bash
git clone https://github.com/SDuarteCorredor/vertical-video-kit
```

## Start

Open Claude Code in your company's folder and say something like:

> Quiero guiones para los reels de mi empresa. Te voy a pasar referentes.

It will look for brand files first, ask the diagnosis in short multiple-choice
rounds, ask for your reference links, analyse them, and build the plan with you.

## What it keeps

A `contenido/` folder in your project: `marca.md`, `reglas.md` (every rejection
becomes a rule), `sistema.md` (production system and series), `referentes/`
(downloads and analysis — keep it out of public repos), `guiones/`,
`aprendizajes.md`.

## Scripts

| Script | What it does |
|---|---|
| `scripts/setup_check.py` | Checks ffmpeg, yt-dlp, faster-whisper, Pillow |
| `scripts/find_context.py` | Finds brand manuals, tone guides, previous scripts and references on disk |
| `scripts/fetch_refs.py` | Downloads reels + metadata from links or codes, writes `resumen.md` |
| `scripts/breakdown.py` | Cuts, frame sheets per shot and per 1.5–3 s, palette, light, aspect, transcript, wpm |
| `scripts/ig_grid.js` | Read-only snippet for a profile's reels grid: median views and outliers |
