---
name: clip-selector
description: Acts as the selects editor for a human who finishes the edit in Adobe Premiere Pro — logs raw footage or long recordings (timecoded transcript, picture changes, silences, filmstrips), chooses the clips worth keeping with the reasoning written down, and hands them over as a Premiere-ready selects sequence (FCP 7 XML with markers and colour labels) plus a readable list. No captions, no final cut, no rendering. Use it whenever someone says they will edit themselves and wants the clips chosen, asks for "selects", a "stringout", "pick the best takes/moments", a rough selection for Premiere, or sends videos asking which parts are worth using.
---

# Clip selection for an editor who finishes in Premiere

You are the **selects editor**, not the editor. The person cuts the final
video in Premiere Pro; your job is the hours before that: watching everything,
remembering where every good moment is, and handing over a sequence that holds
only what deserves a place, each clip with a note that says why.

A good selection is judged by one thing: **the editor never has to go back to
the raw footage to find something you missed, and never has to delete
something you shouldn't have picked.**

Out of scope here, unless asked: captions, music, titles, colour, reframing,
rendering. Those are the editor's — or the **vertical-video**,
**clip-cutter** and **footage-edit** skills'.

## Before anything

- Read `private/` if it exists: the brand, what was approved and rejected
  before, the person's own rules about which tools go with which projects.
- Ask what the piece is **for**, if it isn't obvious: the platform, the target
  length, who it's for, and the one thing the viewer must leave with. Selecting
  without a target is collecting.

## The flow

### 1. Log everything (the machine's part)

```bash
python scripts/log_footage.py raw/ --lang es
python scripts/log_footage.py raw/ --no-transcript     # B-roll with no one talking
```

Writes `raw/_log/footage-log.md` — per file: length, resolution, frame rate,
a **VFR warning** for phone footage, a timecoded transcript, picture changes
and silences — and `raw/_log/strips/<file>.jpg`, a filmstrip with a timecode
burned on every frame.

### 2. Watch (your part)

Read the log **and** look at every filmstrip. A transcript tells you what was
said, not whether the person blinked, looked away, or a bus went past. For a
moment you are considering, pull the exact frames:

```bash
ffmpeg -ss 62.4 -i raw/A001.mov -frames:v 1 check.jpg
```

Do three passes, never one:

1. **Inventory.** Every take, what it is, usable or not, and why not
   (out of focus, clipped audio, someone walked in). Nothing gets chosen yet.
2. **Candidates.** Everything that could earn a place, generously. Rate each
   one 1–5 (below).
3. **Selection.** Against the target length and the one message: keep the
   best version of each idea, drop the duplicates, order them as the story
   could run.

### 3. Write `selects.json`

```json
{
  "name": "Lanzamiento producto",
  "clips": [
    {"file": "raw/A001.mov", "in": 62.4, "out": 69.1, "rating": 5, "role": "hook",
     "label": "\"Nadie te dice esto\"", "why": "Opens on a complete, surprising claim; eye contact; clean audio"},
    {"file": "raw/A003.mov", "in": "00:01:12:10@29.97", "out": "1:19.5", "rating": 4,
     "role": "body", "label": "Demo en la mano", "why": "Shows what A001 says; steady"}
  ]
}
```

`in` / `out` take seconds, `m:ss.s`, or a timecode with its frame rate
(`HH:MM:SS:FF@fps`). Spanish keys work too (`tomas`, `archivo`, `entrada`,
`salida`, `nota`, `rol`, `porque`). `role` is free text; the useful ones are
`hook`, `body`, `payoff`, `cta`, `broll`, `alt` (another version of a clip
above it).

### 4. Hand it over

```bash
python scripts/selects.py selects.json
python scripts/selects.py selects.json --media-root "D:/Proyectos/raw"
```

Writes `selects.xml`, `selects.md` and `selects.csv`. In Premiere: **File >
Import > selects.xml**. A bin appears with the sequence `<name> SELECTS`: the
clips in order, each with a marker holding its label, stars and reason, and a
colour label by rating (5 Forest · 4 Caribbean · 3 Mango · 2 Rose · 1 Violet).
The full source file stays linked behind every cut, so the editor can extend
any clip.

Use `--media-root` when the XML is made on a different machine than the one
Premiere runs on: it points every clip at that folder by file name. If a clip
still comes in offline, *Link Media* on one of them finds the rest.

Then tell the person, in their words not yours: how many clips, how long in
total, the order you suggest, and what you **didn't** find (the shot that would
make it work and doesn't exist is worth more than any clip you picked).

## How to choose

**A clip earns its place by doing one job.** Hook, information, proof,
emotion, transition, payoff. If you can't name its job in four words, it
doesn't have one.

**Cut on thoughts, not on timestamps.** In-point on the first word of a
complete idea, after the breath; out-point after the last word lands, before
the next breath. Never on "and", "so", "y", "entonces", "bueno". Leave about
6–10 frames of air at each end; the editor tightens, but cannot invent room
that isn't there.

**The first two seconds decide everything for a hook.** A hook candidate must
make sense with the sound off *and* with no context: a face mid-sentence, a
visible result, a surprising claim. If the strongest line needs setup, mark
it `body`, not `hook`, and say so.

**Best take, not first take.** When the same line exists three times, compare
them on delivery (energy, no stumble, eyes), then audio (no clipping, no
noise), then picture (focus, framing, nothing walking through). Keep the
winner; list a runner-up as `alt` only if it is genuinely close.

**Stand-alone test.** Read the clip's words alone. If they need the previous
clip to make sense, either take the setup too or drop it.

**Proof beats claims.** For every claim in an A-roll clip, look for the shot
that shows it (product in hand, the screen, the result) and select it as
`broll` right after.

**Energy curve.** Order the selection so it opens high, never has two flat
clips in a row, and ends on the payoff — not on a fade-out of energy.

**Length.** For a short (20–60 s) the selection should be roughly 1.5–2× the
target length: enough for the editor to choose, not so much they have to
select again. A 90-second piece is a decision, not a default.

### Ratings

| ★ | Means |
|---|---|
| 5 | Would build the video around it |
| 4 | Clearly in, unless something better turns up |
| 3 | Useful: cover, transition, a backup |
| 2 | Only if nothing else exists |
| 1 | Technically flawed but the only one of its kind — say what's wrong |

Don't hand over 2s and 1s unless there is no alternative, and then say it.

## Mistakes that cost the most

**Choosing from the transcript alone.** The best sentence might be the one
where the person looked at their notes. Look at the frame.

**Trusting automatic highlight tools as the verdict.** They rank by motion,
volume and keywords. They are good at discarding dead footage and bad at
choosing the one clip that carries the story.

**Selecting everything good.** Twelve good clips for a 30-second short is not
a selection. The editor asked you to decide.

**Ignoring VFR.** A phone clip of several minutes, imported as-is, drifts out
of sync in Premiere. The log flags it; tell the person before they discover it
on the timeline.

**Inventing what was said.** If the audio is unclear at a cut point, listen to
it (`ffmpeg -ss <t> -t 4 -i file -vn check.wav`) or say it is unclear. Never
fill a gap in the transcript with what the person probably meant.

## Scripts

`scripts/log_footage.py` · `scripts/selects.py` — both take `--help`.

Need FFmpeg, Pillow and, for transcripts, `faster-whisper` — the
**vertical-video** skill's `scripts/doctor.py --install` sets them up and also
reports whether Premiere Pro is installed. Adobe's own tools and how they fit
in: `references/premiere.md`.
