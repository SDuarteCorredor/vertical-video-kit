# AGENTS.md

Instructions for any AI coding agent working in this repository — Codex CLI,
Cursor, Gemini CLI, opencode, GitHub Copilot, Windsurf, Aider, Claude Code, or
whatever comes next. This file is the [AGENTS.md open
standard](https://agents.md); Claude Code reads the same content through
`skills/`.

**No agent is required to use this kit.** Every script runs on its own from a
terminal — see [`docs/NO-AGENT.md`](docs/NO-AGENT.md).

---

## START HERE — install, then open the studio

If the person has just pointed you at this repository, or asks you to install
it, set it up, or get it running: **run this first, before reading anything
else.** It is the whole setup.

```bash
python install.py --yes
```

(`python3 install.py --yes` if `python` is not on the PATH. On Windows, `py
install.py --yes`.)

It installs Node, FFmpeg and the Python packages, scaffolds a project in
`my-video/`, and **opens the Remotion studio — the live preview — in the
browser**, then exits. The studio keeps running after the command finishes;
that is deliberate, so you are not left holding an open process.

The studio opening is the point. It is how the person sees that it worked.
Do not skip it, and do not replace it with `npm run dev` in the foreground —
that blocks your turn and they see nothing.

**Tell them the URL it printed** (`http://localhost:3000`, or the next free
port). If their browser did not open by itself, that address is what they
paste into it.

### If the studio needs opening again later

```bash
python skills/vertical-video/scripts/studio.py my-video
```

Same thing: detached, waits until it is really answering, opens a browser,
exits. Inside a project, `npm run dev` does it in the foreground instead.

### If `install.py` stops with something missing

It could not install Node or FFmpeg itself — no package manager, or no
permission. It prints exactly what is missing. Give the person the matching
commands from [`docs/NO-AGENT.md`](docs/NO-AGENT.md) for their platform, then
run `python install.py --yes` again. On Windows, Node and FFmpeg only land on
the PATH in a **new** terminal.

### What not to do here

- **Don't commit the project folder** `install.py` creates. It is the
  person's work, not part of the kit.
- **Don't run the studio in the foreground** as your own command; it never
  returns.
- **Don't wait for a render to check a layout.** Use a still — see below.

---

## What this repo is

A kit for making 9:16 short-form video (TikTok, Reels, Shorts) **in code**:
AI narration, word-by-word captions, and a real 1080×1920 Remotion render.

The one idea everything follows from: **content lives apart from design**.
Changing a line of narration is editing one line and re-running a script — not
re-recording and re-cutting.

## Read these before you act

| You are asked to | Read first |
|---|---|
| Make a vertical video from scratch | `skills/vertical-video/SKILL.md` |
| Cut a long video into shorts | `skills/clip-cutter/SKILL.md` |
| Study a reference video | `skills/reference-research/SKILL.md` |
| Make a corporate / brand video | `skills/vertical-video/references/corporate.md` |
| Lay anything out on screen | `skills/vertical-video/references/design.md` |
| Write or generate narration | `skills/vertical-video/references/voice.md` |
| Write the first sentence | `skills/vertical-video/references/hooks.md` |

Those files are the real instructions. This one is the index.

## The flow, in one screen

```bash
python install.py --yes        # once: dependencies, a project, the studio open

cd my-video
# edit script.json (what is SAID) and src/content.ts (what is SEEN)
python scripts/voice.py        # narration -> audio/ + src/timings.json
python scripts/captions.py     # word-by-word -> src/captions.json
npm run check                  # does it compile
npm run render                 # output/video.mp4
python scripts/publish.py      # upload/video.mp4, platform-ready
```

The studio reloads by itself on every save, so leave it open while you work —
the person watches the video change as you edit. `python scripts/doctor.py`
reports on the machine if something later looks wrong.

The studio opens on a brand-new project, before any audio exists: scenes fall
back to 3 seconds each until `voice.py` has measured the real narration.

## Rules that are not negotiable

**Never invent facts.** Percentages, prices, dates, claims about what a product
does, client names. A plausible number typed in to fill a line becomes a
promise the person publishing it never made. Ask for the number, or stay at the
level of generality you were actually given — and say what you left pending
when you hand the video over, instead of burying it in a code comment.

**Content and design stay separate.** `script.json` and `src/content.ts` are
the only files content touches. If a text change requires editing a component,
the change is going the wrong way.

**Audio drives timing.** Never hardcode a scene duration. `voice.py` measures
the narration and writes `src/timings.json`; the components read it.

**Nothing readable goes in the bottom ~380px or the right ~160px.** That is
where TikTok and Reels draw their own interface. Set `SHOW_SAFE_AREAS = true`
in `src/theme.ts` and look before you claim a layout is fine.

**Check with single frames, not full renders.** A render takes minutes, a frame
takes seconds:

```bash
npx remotion still src/index.ts Short preview/f.png --frame=90
```

Look at one frame of **each scene type**, not just the first.

**Don't commit generated media.** `audio/`, `output/`, `upload/`, `public/audio/`
and `node_modules/` are gitignored on purpose. They regenerate.

## Who you are usually helping

Often someone in marketing or communications, frequently non-technical. They do
not care what Node or React is, and they should not have to.

Handle the technical side yourself. Talk about what they care about: the hook,
the script, how long it runs, how it looks on a phone. **Never ask them to edit
code** — ask for the words and put them where they go.

If they write to you in Spanish, answer in Spanish. The repo ships
[`README.es.md`](README.es.md), [`docs/SIN-AGENTE.md`](docs/SIN-AGENTE.md) and
[`docs/PROMPTS.es.md`](docs/PROMPTS.es.md) for exactly that.

## Verifying a change to the kit itself

```bash
cd template/remotion-vertical
npm install
npm run check
python scripts/voice.py --engine edge --voice en-US-AndrewNeural
python scripts/captions.py
npx remotion still src/index.ts Short preview/f.png --frame=60
```

Type checking does not catch a layout that renders text under the platform UI.
Look at the frame.
