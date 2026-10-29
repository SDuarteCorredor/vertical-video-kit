---
name: ai-video
description: Plans and prompts AI-generated video shots (Higgsfield, Seedance, Kling, Wan, Veo) that have to sit inside a real edit — a mascot or presenter that stays the same character in every shot, a person in existing footage swapped for another character, a short cinematic hook in front of real screen recordings. Covers character sheets, start frames, video prompts, lip-sync and how to spend as few credits as possible. Use it whenever someone wants to add or replace shots with AI video, keep an AI character consistent, turn a mascot into a moving presenter, swap a person out of a video they already recorded, or asks how to prompt Higgsfield or a similar video model.
---

# AI video shots inside a real edit

AI video is the expensive, unreliable part of the job. Everything here exists
to spend credits only on shots that are already decided, and to make the
character come back the same every time.

The kit itself does not call any AI video service. It prepares what the
generator needs, writes the prompts, and takes the results back into the edit
(**vertical-video** or **footage-edit**). The person runs the generations in
their own account.

## Decide what is really generated

Go through the existing video shot by shot and put each one in one of four
boxes. Most of a how-to video stays real.

| Box | When | Tool |
|---|---|---|
| **Keep** | Screen recordings, UI, anything the viewer must see exactly as it is | the edit |
| **Swap** | A real shot is right but the person in it must become someone else | Genjutsu-style character swap, see `references/swap-real-footage.md` |
| **Insert** | Only a region changes: a face inside a phone camera box, a logo on a screen | generate the subject alone, composite it into the region |
| **Generate** | No footage exists: an establishing shot, a hook, a closing beat | image → video, see `references/prompting.md` |

Swap before generate. A swap keeps the real camera move, timing and cuts, so
it lines up with the narration that is already there; a generated shot has
to be cut to fit afterwards.

## The flow

### 1. Cut the shots that will change

```bash
python scripts/prep_shots.py video.mov --detect
python scripts/prep_shots.py video.mov --out shots/ --shot intro=0-2.9 --shot desk=2.9-7.89
```

`--detect` lists where the picture changes, so the times come from the footage.
Each shot comes out as an H.264 clip plus its first and middle frame, with the
full soundtrack and a `manifest.json`. Use the best original you can get: a
WhatsApp copy is about 464 px wide and every AI tool will show it.

### 2. Lock every character before any video

Still images are cheap or unlimited; video is not. Build each character's
sheet first and get it approved — `references/character-sheets.md`:

1. Turnaround (front, 3/4, side, back) in **one** image on mid-grey.
2. One clean face close-up: this is the anchor every video prompt points at.
3. Expressions (including mouth shapes for lip-sync) and the poses the script needs.

Save each character as a reusable reference in the tool (Higgsfield calls them
Elements, `@name`).

### 3. Make every start frame as an image

For **Generate** shots, build the first frame of each shot as a still, with
the approved sheet as reference, and fix it there. A wrong start frame only
gets worse once it moves.

### 4. Then video, cheaply first

Test at 720p or with the cheaper model tier, change one thing per attempt,
watch the whole clip (drift shows up in the middle), and only render the
chosen version at full resolution. Prompts: `references/prompting.md`.
Which model for what: `references/models.md`.

### 5. Back into the edit

Generated clips go in like any other footage: `public/media/` in a
**vertical-video** project, or the `raw/` folder of a **footage-edit** cut.
Keep the original narration timing from `narration.mp3`; if the voice is new,
generate it to the same script and let `voice.py` re-time the scenes.

## Rules

**Never put the real screen in the generator.** Interfaces, numbers, QR codes
and button labels come back warped. Keep those shots real and change only what
sits around or inside them.

**One character description, pasted verbatim into every prompt.** Rewording it
between shots is how a character drifts.

**Mid-grey behind characters, never white.** White melts into light clothes and
leaks into the subject; grey keeps edges clean for compositing.

**One face per reference image when generating video.** Sheets with many faces
make video models switch between them.

**Rights.** Swap only footage you own or are allowed to use, and only into
characters you have the rights to. A real person's face needs their permission.
