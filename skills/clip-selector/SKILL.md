---
name: clip-selector
description: Acts as the selects editor for a human who finishes the edit in Adobe Premiere — logs raw footage or long recordings (timecoded transcript, picture changes, silences, filmstrips), chooses the clips worth keeping with the reasoning written down, and hands them over as a Premiere-ready selects sequence (FCP 7 XML with markers, colour labels, alternates on a disabled track, per-topic stringouts) plus a readable list. No captions, no final cut, no rendering. Use it whenever someone says they will edit themselves and wants the clips chosen, asks for "selects", a "stringout", "pick the best takes/moments", a rough selection for Premiere, or sends videos asking which parts are worth using.
---

# Clip selection for an editor who finishes in Premiere

You are the **selects editor**, not the editor. The person cuts the final
video in Premiere; your job is the hours before that: watching everything,
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

If the log flags **VFR**, tell the person before going further: conform the
files to a constant rate and select from the copies (the command is in
`references/premiere.md`), or the cuts land a frame or two off in Premiere and
long clips drift out of sync.

### 2. Watch (your part)

Read the **whole** log before choosing anything — automatic clippers fail
precisely because they judge each moment on its own and miss the setup a
punchline needs. Then look at every filmstrip: a transcript tells you what was
said, not whether the person looked at their notes, or a bus went past. For a
moment you are considering, pull the exact frame:

```bash
ffmpeg -ss 62.4 -i raw/A001.mov -frames:v 1 check.jpg
```

Do three passes, never one:

1. **Inventory.** Every take, what it is, usable or not, and why not. Log
   B-roll on its own. Tag lightly: most labels added this early go unused.
   Note **silent visual moments** (a reaction, a reveal, something happening
   with no one speaking) — speech-based selection never sees them.
2. **Candidates.** Everything that could earn a place, generously, scored
   (below).
3. **Selection.** Against the target length and the one message: keep the
   best version of each idea, put close runners-up as alternates, order the
   rest as the story could run.

### 3. Write `selects.json`

```json
{
  "name": "Lanzamiento producto",
  "clips": [
    {"file": "raw/A001.mov", "in": 62.4, "out": 69.1, "rating": 5, "role": "hook",
     "group": "Producto", "label": "\"Nadie te dice esto\"",
     "why": "Complete surprising claim in the first second; eye contact; clean audio"},
    {"file": "raw/A001.mov", "in": 140.2, "out": 146.0, "rating": 4, "role": "alt",
     "group": "Producto", "label": "Hook, toma 2", "why": "More energy, stumbles on 'producto'"},
    {"file": "raw/A003.mov", "in": "00:01:12:10@29.97", "out": "1:19.5", "rating": 4,
     "role": "broll", "group": "B-roll", "label": "Demo en la mano", "why": "Shows what A001 claims"}
  ]
}
```

| Field | |
|---|---|
| `in`, `out` | seconds, `m:ss.s`, or timecode with its rate, `HH:MM:SS:FF@fps` |
| `rating` | 1–5, see below — it becomes the clip's colour label |
| `role` | `hook`, `body`, `proof`, `payoff`, `cta`, `broll`… goes in capitals in the marker name. **`alt`** is special: that clip goes on V2, disabled, right above the clip before it, so swapping takes is one click |
| `group` | optional topic; every group also becomes its own stringout sequence |
| `label`, `why` | what the editor reads on the marker. `why` names the clip's job and any risk ("needs the setup at 12:40") |

Spanish keys work too: `tomas`, `archivo`, `entrada`, `salida`, `nota`, `rol`,
`grupo`, `porque`.

### 4. Hand it over

```bash
python scripts/selects.py selects.json
python scripts/selects.py selects.json --media-root "D:/Proyectos/raw"
```

Writes `selects.xml` for Premiere (**File > Import**) plus `selects.md` and
`selects.csv` to read. The XML holds a bin with:

- `<name> SELECTS` — every clip in order on V1, alternates disabled on V2,
  a marker on each clip and on the ruler named `03 HOOK – label` with the
  stars and the reason in its comment, colour label by rating.
- `<name> · <group>` — one stringout per group, if you used groups.

The whole source file stays linked behind every cut, so the editor can extend
any clip. With `opentimelineio` installed, the script also reads the XML back
to check every clip is in it, and writes an `.otio` copy.

Use `--media-root` whenever the XML is made on a different machine than the
one Premiere runs on — a cloud session, WSL, another computer: it points every
clip at that folder by file name, in the form Premiere writes itself. If a clip
still comes in offline, *Link Media* on one of them finds the rest.

**The first time on a new machine**, have the person import a two-clip test and
check markers, colours and linked media before trusting a big delivery.

Then tell the person, in their words not yours: how many clips, how long in
total, the order you suggest, **what you rejected and why** (so they can
overrule you), and what you **didn't** find — the shot that would make it work
and doesn't exist is worth more than any clip you picked.

## How to choose

**A clip earns its place by doing one job.** Hook, information, proof,
emotion, transition, payoff. If you can't name its job in four words, it
doesn't have one.

**Stand-alone test.** Read the clip's words as if you had never seen anything
else. If they need something earlier to make sense, take the setup too — or
drop it. A setup longer than about 15 seconds makes it a segment, not a clip.

**The hook is the first line *and* the first frame.** A hook candidate makes a
claim, asks a question, opens a conflict or shows something, in the first one
to three seconds, and the picture promises the same thing as the words. If the
strongest line needs setup, mark it `body`, not `hook`, and say so.

**No payoff, no clip.** The window must deliver what its first line promises —
the punchline, the consequence, the answer. Every sentence in between either
moves toward it or is a reason to tighten. A turn ("but…") beats a flat
statement.

**Cut on thoughts, not timestamps.**
- *In:* on the first word of the line that matters, a few frames before it,
  after the breath. Usually not the interviewer's question — unless the
  answer means nothing without it, and then keep the question tight.
- *Out:* after the payoff lands, keeping the laugh or the reaction — up to two
  or three seconds of it; drop the trailing "so, yeah". Never on "and", "so",
  "y", "entonces", "bueno".
- Where people talk over each other, check that neither is cut mid-thought.
- Transcribers merge quick repeats into one word: where someone stutters or
  restarts, check the cut point in the audio
  (`ffmpeg -ss <t> -t 4 -i file -vn check.wav`), not just the timestamps.

**Best take, not first take.** When the same line exists several times,
compare delivery (energy, no stumble, eyes), then sound (no clipping, no
noise), then picture (focus, framing, nothing walking through). Emotion beats
polish unless the flaw is one the viewer will notice. Keep the winner; a close
runner-up goes in as `alt`. If the best version is half of one take and half
of another, say so with both timecodes.

**Proof beats claims.** For every claim in a talking clip, look for the shot
that shows it (product in hand, the screen, the result) and select it as
`broll` with its own `group`.

**Energy curve.** Order the selection so it opens high, never has two flat
clips in a row, and ends on the payoff — not on a fade-out of energy.

**How much.** Default clip length 20–60 s; 45–75 s when the arc earns it; a
90-second clip is a decision, not a default. Hand over roughly 1.5–2× what the
final piece needs: even a good first pass is wrong 20–40% of the time, and the
editor needs room to disagree. From an hour of conversation, 10–20 usable
clips is normal.

### Ratings

Score each candidate on hook, stand-alone clarity, emotion, usefulness to the
viewer and visual strength; the rating is the overall call, and `why` says
which of those carried it.

| ★ | Means | Colour in Premiere |
|---|---|---|
| 5 | Would build the video around it | Forest |
| 4 | Clearly in, unless something better turns up | Caribbean |
| 3 | Useful: cover, transition, a backup | Mango |
| 2 | Only if nothing else exists | Rose |
| 1 | Technically flawed but the only one of its kind — say what's wrong | Violet |

Don't hand over 2s and 1s unless there is no alternative, and then say it.
Never hand over a bare number: every rating comes with its reason.

## Mistakes that cost the most

**Choosing from the transcript alone.** The best sentence might be the one
where the person looked at their notes. Look at the frame.

**Trusting automatic highlight tools as the verdict** — Adobe's Quick Cut,
Opus-style virality scores, or your own first ranking. They are good at
discarding dead footage and inconsistent at choosing the one clip that carries
the story. Sort with them; decide yourself.

**Selecting everything good.** Twelve good clips for a 30-second short is not
a selection. The editor asked you to decide.

**Silently discarding.** A take you rejected and didn't mention is a take the
editor can't overrule you on.

**Ignoring VFR.** See step 1.

**Inventing what was said.** If the audio is unclear at a cut point, listen to
it or say it is unclear. Never fill a gap in the transcript with what the
person probably meant, and never put a figure in a `label` that wasn't said.

## Scripts and references

`scripts/log_footage.py` · `scripts/selects.py` — both take `--help`.

Needs FFmpeg, Pillow and, for transcripts, `faster-whisper` — the
**vertical-video** skill's `scripts/doctor.py --install` sets them up and also
reports whether Premiere is installed. `pip install opentimelineio
otio-fcp-adapter` adds the read-back check and the `.otio` copy.

- `references/premiere.md` — why FCP 7 XML, what each Adobe tool is for
  (and why the Adobe connector and Premiere MCP servers aren't the route).
- `references/selection-research.md` — where these rules come from, and how
  solid each source is.
