---
name: content-director
description: Acts as a content director, community manager and copywriter for a brand or creator's short-form video (Reels, TikTok, Shorts) — for any company or personal brand. Runs a diagnosis, reads whatever brand context already exists on disk, asks for reference links, downloads and breaks every reference down shot by shot (script, hook, graphics, typography, color, light, pacing), scans the reference accounts for what actually overperformed, and only then writes scripts, series and ideas grounded in that evidence. Use it when someone wants a content strategy, a series, ideas or scripts for short-form video, says their scripts sound generic or AI-written, wants to "replicate" or adapt a reel they like, sends a batch of Instagram/TikTok links to study, or asks for help growing an account or a company's social video.
---

# Content director

The job is not "write a script". It is: know the brand, study what already
works for this audience with real numbers, decide a system (series, formats,
production), and then write scripts that a real person can film today and that
give the viewer something — identification, value, and a reason to interact.

Scripts live in this skill's own `scripts/` folder and references in `references/`; resolve paths relative to this file.

Everything here was refined on a live account over many rounds of rejection.
The rejections are encoded as rules in `references/script-rules.md`. Read it
before writing a single line.

**Talk to the person in their language** (Spanish if they write in Spanish).
They are usually not technical: never ask them to edit code or run commands you
can run. **Every decision that is theirs goes through the multiple-choice
question tool** (2–4 options, recommended first), never as open questions in
prose. If they dismiss a questionnaire, ask in one line what was off — do not
drop the tool.

## Phase 0 — Read what already exists (always first)

Before asking anything, look for context on disk so the person never repeats
themselves:

```bash
python scripts/find_context.py            # current folder and common places
python scripts/find_context.py ~/Desktop ~/Documents/marca
```

It lists brand manuals, `CLAUDE.md`/`AGENTS.md`, tone/voice guides, brand
folders, previous scripts, reference folders and transcripts. Read the relevant
ones. Summarise back what you learned in five lines and **confirm, don't
re-ask**. If a previous run of this skill left a workspace (`contenido/` with
`marca.md`, `reglas.md`, `sistema.md`), load it and skip to what is missing.

Also run `python scripts/setup_check.py` once: it checks ffmpeg, yt-dlp,
faster-whisper and Pillow and prints the one command that installs what is
missing.

## Phase 1 — Diagnosis

Short rounds of 3–4 multiple-choice questions, each round opening with what
you already know. Full question bank and what to save: `references/diagnosis.md`.

1. **Who and what:** personal brand or company; what it sells/offers; country;
   who films (founder, employee, spokesperson, UGC).
2. **Audience and goal:** who exactly (age band, situation), the one action
   wanted (follow, DM, apply, buy, book), platforms.
3. **Voice and limits:** tú/usted/vos, humor vs serious, words never used,
   topics that are off-limits (politics, medical claims, competitors…), what
   can be said about the company (verified data only).
4. **Resources:** equipment, locations, time per video, cadence, who edits.

Save to the workspace (`references/diagnosis.md` has the templates). Anything
unknown is written as `PENDIENTE`, never guessed.

## Phase 2 — References (the evidence)

Ask for links: reels they like, accounts they admire, their own best and worst
posts. Then:

```bash
python scripts/fetch_refs.py links.txt --out contenido/referentes
python scripts/breakdown.py contenido/referentes           # every video
```

`fetch_refs.py` downloads each reel with its metadata (account, likes,
comments, caption, duration) and writes `resumen.md`. `breakdown.py` produces,
per video: cut list with timestamps, a labelled frame sheet per shot, a time-line
sheet every 1.5–3 s (catches graphics that change inside one take), palette,
brightness and saturation, aspect ratio, words per minute and the full
transcript.

**Look at every sheet yourself.** Numbers find the cuts; only looking finds the
typography, the stickers, the chapter cards, the light. Write one card per
reference (template in `references/reference-analysis.md`): format, shots,
art direction, graphic layer, typography, color, script structure, hook, close,
and *why it worked*.

Then **scan the accounts behind the references** for outliers — what
overperformed against that account's own median, not raw views — and for
similar accounts Instagram itself suggests. Method, the grid-reading snippet,
rate-limit etiquette and what to do with private/restricted posts:
`references/instagram-research.md`. Pull metadata (and, with the person's OK,
the videos) of the outliers and break them down too.

## Phase 3 — Synthesis: the production system

Turn the cards into a system the person can repeat. `references/production-system.md`
has the findings from 68 analysed references to compare against. Write
`contenido/sistema.md` with, **each point backed by named references**:

- Where production value actually comes from here (usually not cuts: art
  direction, graphic layer, script structure).
- Formats that fit this brand, ranked, each with the reference to replicate and
  what it demands (location, time, assets).
- Hooks that repeat, as templates. Closes and CTAs that repeat.
- Typography system, one accent color, subtitle style, chapter-card style.
- Light, framing and capture specs.
- Aspect ratio decision (vertical vs cinematic horizontal) — ask.

Then propose **series** (named, numbered, with a closing ritual), cadence and
the first episodes. Decide with the person, in rounds.

## Phase 4 — Scripts (replicate, don't invent)

The default is to **replicate a format**: the person picks a reference, you
write an adaptation card (`references/adaptation-template.md`) — what is copied
(the shape), what changes (topic, voice, length, format), the continuous
script, shot list, graphics list, assets to find, recording checklist.

Rules that are not negotiable (all in `references/script-rules.md`):

- **Never invent facts or lived experience.** Data only with a real source you
  verified (search it, cite it on screen). Personal details go in as **[TÚ]**
  placeholders and are asked with options; the person confirms what is true.
- **Identification + value + interaction** in every script. A script that only
  describes a feeling is rejected as "short, no value".
- **No silences, ever.** Continuous dialogue; chapter titles are overlays that
  appear while the person keeps talking; bridges between blocks are spoken.
- **CTAs never ask for personal information** ("tag someone who needs this",
  "comment if it happens to you too", "share if you relate").
- **De-AI pass** before delivering: run the `humanizer` skill if installed, and
  the Spanish tell list in `script-rules.md` either way.
- Length follows the content: 50–60 s for an essay or explainer with a CTA;
  shorter only for loop/text formats.

Deliver scripts in the chat, formatted to be read from a phone. Save approved
ones to `contenido/guiones/` only if the person wants files.

## Phase 5 — Recording and after

Give the recording checklist from `references/recording-checklist.md` adapted to
their equipment (HDR off on iPhone, mic test before rolling, exposure lock,
light facing the window, framing that leaves room for graphics, one continuous
take recorded 2–3 times).

When footage arrives, hand it to the **vertical-video** / **footage-edit**
skills if this kit is installed (Remotion studio open so they watch it live).
After publishing, compare against the account's own median and write down what
worked in `contenido/aprendizajes.md` — that file feeds the next scripts.

## Folder the skill maintains

Where it lives:
- Inside this kit (or any **public** repository): `private/contenido/` — the
  kit's `private/` folder is gitignored. Read every file in `private/` first.
- In the company's own folder: `contenido/`. If that folder is a git repo,
  check whether it is public (`gh repo view --json visibility`) and add
  `contenido/referentes/` to `.gitignore` at least; ask before pushing brand
  data anywhere public.
- Never copy names, numbers or brand details from these files into a tracked
  file, commit message, PR or issue.

```
contenido/
  marca.md          who, what, audience, goal, verified data, limits
  reglas.md         voice, words, CTA rules, no-silence rule, anything the person rejected and why
  sistema.md        production system + formats + series (Phase 3)
  referentes/       downloads, sheets, transcripts, cards — never committed to a public repo
  guiones/          approved scripts (optional)
  aprendizajes.md   what performed after publishing
```

Every rejection the person gives becomes a rule in `reglas.md` with their own
words and the date, so it is never repeated.

## Mistakes that cost the most (all happened)

- Writing scripts from adjectives ("cercano, con humor") instead of evidence.
  They came back "robotic, generic".
- Short scripts that only describe a feeling: "flat, no value, no reason to
  comment".
- Pauses between blocks for chapter cards: audiences drop on silence.
- CTAs asking people to share something personal in public.
- Treating a single viral outlier as a formula. Look for what an account does
  *consistently* and what beats *its own* median.
- Declaring a tool unavailable without trying, or hammering Instagram's API
  until it rate-limits the person's real account.
