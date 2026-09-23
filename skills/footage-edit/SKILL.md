---
name: footage-edit
description: Turns raw phone footage — a handful of takes from an event, an office, a team day, a product on a desk — into one polished vertical video with FFmpeg alone: trimmed, straightened, stabilized, a slow push-in on every shot, color-corrected and joined with crossfades, optionally with music. Use it whenever someone has recorded clips (or received them on WhatsApp) and wants a short, a reel or a recap made from them, needs help choosing which takes to use, or wants shaky or crooked footage cleaned up. No narration and no Remotion involved.
---

# Phone footage into one vertical video

The footage already exists. The job is choosing the good seconds, fixing what
the phone got wrong, and giving still shots some life — not animating anything.

When the piece needs narration, captions or text on screen, this is the wrong
skill: use **vertical-video**, and drop the finished clips from here into its
`public/media/` as scene backgrounds.

## The flow

### 1. Put the takes in one folder, untouched

```
my-edit/
  raw/        the original files, never modified
  edit.json   the cut, written in step 3
```

### 2. Look at every take, with names on it

```bash
python scripts/contact_sheet.py my-edit/raw
```

Writes `contact_sheet.jpg` (one labelled thumbnail per file, from the middle
of the take) and `contact_sheet.txt` (number, length, resolution, file name).

**Choose takes by file name, never by position on a grid.** Counting squares
on an unlabelled sheet is how three wrong clips ended up in a finished video.

For a closer look at a moment:

```bash
ffmpeg -ss 6.2 -i my-edit/raw/take.mp4 -frames:v 1 still.jpg
```

### 3. Write the cut

Copy `edit.example.json` next to the footage and fill in one entry per shot:

```json
{
  "output": "output/video.mp4",
  "crossfade": 0.5,
  "music": "music.mp3",
  "clips": [
    {"file": "raw/IMG_1043.mov", "start": 6.2, "duration": 4.5,
     "rotate": -3, "zoom": 1.09, "zoom_speed": 0.035, "x": 0.5, "y": 0.15}
  ]
}
```

| Field | What it does | Starting point |
|---|---|---|
| `start`, `duration` | the seconds to keep | 3–5 s per shot |
| `rotate` | straightens a tilted horizon, in degrees | check a still first; usually -2 to -4 or 2 to 4 |
| `zoom` | how close the shot starts | 1.06 |
| `zoom_speed` | how much it pushes in per second | 0.025–0.04 |
| `x`, `y` | where the push-in heads (0 = left/top, 1 = right/bottom) | 0.5, 0.2 |
| `stabilize` | removes hand shake | on; turn off for tripod shots |
| `color` (top level) | contrast, saturation, brightness, gamma | the defaults suit most phone footage |

Horizontal footage works too: it is cropped to fill 9:16, never squashed. Aim
`x` at the subject.

### 4. Render

```bash
python scripts/edit.py my-edit/edit.json
python scripts/edit.py my-edit/edit.json --join-only    # only re-join, after reordering
```

Each shot is processed into `work/`; `--join-only` reuses those, so trying a
different order or crossfade takes seconds instead of minutes.

The final line prints the real length next to the expected one. If they
differ, a `start` + `duration` ran past the end of its file.

### 5. Deliver

From a Remotion project, `python scripts/publish.py <file>` makes the upload
copy and `python scripts/share.py <file>` a light one for email or WhatsApp.
Both work on any MP4, not just Remotion renders.

## What makes the difference

**Straighten before anything else.** Stabilization removes shake, not a fixed
tilt, so the order is rotate → stabilize → move.

**Every shot moves.** A stabilized shot looks locked-off and flat. The slow
push-in gives it life back — and it is also how you get rid of clutter at the
edges: aim `x`/`y` away from the mug, the bottle, the cable, and the push-in
crops it out.

**Short shots.** Three to five seconds. Phone footage that holds longer than
that reads as unedited.

**Music, not live sound.** Clips are processed silent. Room audio from five
different takes never matches; one music track over all of them does.

## Mistakes that cost the most

**Picking takes from a grid without names.** See step 2.

**Rotating after stabilizing.** The tilt stays, and the stabilizer fights the
correction.

**Zooming too fast.** Above ~0.05 per second it reads as a camera move somebody
did on purpose — and badly.

**Editing the files in `raw/`.** Keep originals untouched; everything
regenerates from `edit.json`.

## Scripts

`scripts/contact_sheet.py` · `scripts/edit.py` — both take `--help`.

Needs FFmpeg (with vidstab: the Gyan build on Windows, Homebrew and apt all
include it) and Pillow for the contact sheet. The **vertical-video** skill's
`scripts/doctor.py` checks both. The original Spanish keys (`tomas`,
`archivo`, `inicio`, `duracion`, `rotar`...) are accepted in `edit.json` too.
