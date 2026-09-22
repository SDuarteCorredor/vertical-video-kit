---
name: vertical-video
description: Makes short-form vertical videos for TikTok, Instagram Reels and YouTube Shorts in code — AI narration that does not sound robotic, word-by-word captions, and a Remotion render at 1080x1920. Use it whenever someone wants to make a TikTok, a Reel, a Short or any 9:16 video; turn a script, an article or a post into a video; add a voice-over or captions to something; batch out variations of one video; or fix a vertical video that looks amateurish, has text hidden under the platform UI, or sounds like a text-to-speech robot.
---

# Short-form video in code

Content lives apart from design. That is the entire idea, and everything else
here follows from it: changing a line of narration is editing one line and
re-running a script, not re-recording and re-cutting.

It is the opposite of an editor timeline, where every fix means dragging
things around again — which is why videos made that way ship with mistakes
nobody was willing to go back and correct.

## Who you are usually helping

Often someone in marketing or content, frequently non-technical. They do not
care what Node or React is, and they should not have to.

Handle the technical side yourself. Talk about what they care about: the hook,
the script, how long it runs, how it looks on a phone. Never ask them to edit
code — ask for the words and put them where they go.

## The flow

### 1. Get the environment ready

```bash
python scripts/doctor.py --install
```

Reports what is missing and installs the Python pieces. Node and FFmpeg it
will not install silently — it prints the exact command for the platform.

On a machine with nothing on it, `python install.py --yes` from the kit root
does the whole setup in one command — dependencies, a project, and the
Remotion studio open in the browser. (`setup.sh` / `setup.ps1` bootstrap
Python itself first, if it is missing.)

If the person wants to drive it themselves rather than through you,
`scripts/wizard.py` asks five questions and produces the finished MP4 with no
agent involved. `docs/NO-AGENT.md` and `docs/PROMPTS.md` are the handover
documents for that.

### 2. Decide what the video is before building anything

Short-form is unforgiving about this. A 40-second video that starts badly is
not a 40-second video, it is a 2-second video.

What you need before writing a line:

- **Who it is for and what they should do after watching.** "Brand awareness"
  is not an answer you can build from.
- **The hook** — the first sentence. See `references/hooks.md`. Get this
  approved before anything else; everything downstream is built on its timing.
- **Where it is going.** TikTok, Reels and Shorts all take 1080x1920, but they
  cover different parts of the frame with their own interface.
- **How long.** Under 60s unless there is a real reason.

If they already have the content somewhere — a post, an article, a long video —
start from that rather than from a blank page. For a long video, use the
`clip-cutter` skill instead of writing anything new.

### 3. Create the project

```bash
python scripts/new_project.py my-video
python scripts/new_project.py my-video --engine edge --voice es-CO-SalomeNeural
```

### 4. Write both texts — before touching design

Two files, and they are the only ones content touches:

- **`src/content.ts`** — what is **seen**
- **`script.json`** — what is **said**

Write both completely first. Adjusting design against half-written text means
redoing the design when the real text arrives.

They are different texts on purpose. The screen can carry fragments; the voice
needs whole sentences. Writing one and pasting it into the other is the most
common reason a video sounds like a machine reading a slide.

If the video carries a company's name, read `references/corporate.md` before
writing — brand, approvals and what may not be claimed all change the job. A
project scaffolded by `new_project.py` ships a `BRAND.md` to fill in once per
company; if it has anything in it, read it first.

**Never invent facts.** Percentages, prices, dates, claims about what a product
does. A plausible number typed in to fill a line becomes a promise the person
publishing it did not make. If a detail is missing, ask for it or stay at the
level of generality you were actually given — and say what you left pending
when you hand the video over, rather than burying it in a code comment.

### 5. Generate the voice — and let it set the timing

```bash
python scripts/voice.py
```

Writes one MP3 per scene, measures each one, and writes `src/timings.json`.

**Audio first, animation second.** A scene lasts exactly as long as its
narration. Change the script, re-run, everything re-syncs itself.

Making it sound human is a craft with real rules — read
`references/voice.md` before generating anything. Short version: the engine
matters much less than the text you feed it.

### 6. Generate the captions

```bash
python scripts/captions.py
```

Transcribes the narration you just made and writes word-level timings to
`src/captions.json`. Most of the feed is watched with the sound off, so this
is not a finishing touch — it is the video.

### 7. Build the scenes

The template ships with scene types (`hook`, `point`, `list`, `stat`, `quote`,
`cta`). Declare content, the layout follows. Only write a new type when none
of them can carry the idea.

`references/design.md` has the rules that decide whether this looks
professional or homemade. **Read it before laying anything out** — especially
the safe areas, which are where most of these videos go wrong.

**Leave the studio open while you work.** It reloads on every save, so the
person watches the video change as you edit instead of waiting for a render:

```bash
python skills/vertical-video/scripts/studio.py my-video   # detached, opens a browser
```

It works on a brand-new project, before any audio exists — scenes hold 3
seconds each until `voice.py` has measured the real narration. Inside a
project, `npm run dev` does the same in the foreground; never run that as your
own command, it does not return.

### 8. Check with single frames, not full renders

```bash
npm run check                                              # does it compile
npx remotion still src/index.ts Short preview/f.png --frame=90   # how it looks
```

A full render takes minutes; a frame takes seconds. Look at **one frame of
each scene type**, not just the first. Look for text under the platform UI,
bad line breaks, low contrast, anything past the margin.

### 9. Render and publish

```bash
npm run render              # output/video.mp4
python scripts/publish.py   # upload/video.mp4, encoded the way platforms want
```

## How to hand it over

Show the result, don't explain the code. What actually helps them:

- Where the file is and how long it runs
- That changing any text costs them one sentence to you, not a re-edit
- What is still pending and why

## Mistakes that cost the most

**Building before the hook is agreed.** The most expensive one, every time.

**Text in the bottom third.** TikTok's caption, username and music ticker live
there; Reels covers roughly the same band. Text placed there is not "a little
tight" — it is invisible to most of the audience. Turn on `SHOW_SAFE_AREAS` in
`src/theme.ts` and look.

**Captions as an afterthought.** Add them last and they fight the layout you
already built. The template reserves their space from the start; keep it.

**Feeding the voice engine screen text.** Fragments, acronyms and symbols are
exactly what makes TTS sound like TTS. See `references/voice.md`.

**A hook that explains before it hooks.** "In this video I'm going to talk
about..." is a two-second goodbye.

**Rendering the whole thing to check one detail.** Use `still`.

**Sampling brand colors from a screenshot or a video frame.** Compression
shifts them. Take colors from a brand kit or a clean logo export.

## Resources

- `references/hooks.md` — how the first two seconds work, with patterns
- `references/voice.md` — engines, and how to make TTS sound human
- `references/captions.md` — caption styles and timing
- `references/design.md` — safe areas, type, motion. **Read before laying out.**
- `references/corporate.md` — brand, approvals, what may not be claimed
- `scripts/` — `doctor` · `new_project` · `wizard` · `studio` · `diagnose`.
  All take `--help`.
- `install.py` at the kit root — the one-command setup
- Inside a project: `scripts/voice.py` · `captions.py` · `publish.py`

Related skills: **clip-cutter** (long video into vertical clips),
**reference-research** (take apart a short that works).
