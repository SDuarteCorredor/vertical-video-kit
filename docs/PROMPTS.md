# Prompts you can copy

Two sections: prompts for a **coding agent** (Claude Code, Codex CLI, Gemini
CLI, Cursor), which edits the files for you, and prompts for **any free chat**
(ChatGPT, Claude, Gemini, Copilot, DeepSeek), which just hands back text for
you to paste.

> Español: [`PROMPTS.es.md`](PROMPTS.es.md) · Running it with no AI at all:
> [`NO-AGENT.md`](NO-AGENT.md)

Replace anything in `CAPS` with your own. Leave the rest — the odd-looking
constraints ("don't invent numbers", the 380px band) are what prevent 90% of
the problems.

---

## Part 1 — With a coding agent

The agent has already read `AGENTS.md` and the `SKILL.md` files. You don't need
to explain the repo; you need to say what video you want.

### Starting a video from nothing

```
Make me a 40-second vertical video for Instagram Reels about HOW OUR
ONBOARDING PROCESS WORKS.

Audience: OPERATIONS MANAGERS AT MID-SIZE COMPANIES.
What I want them to do after watching: BOOK A DEMO.
Tone: DIRECT, NO CORPORATE FILLER, THE WAY YOU'D EXPLAIN IT TO A COLLEAGUE.
Voice: US English, male.

Before building anything, give me three different options for the opening
line and wait for me to pick one. Don't invent figures, client names or
percentages — if you need a number, ask me for it.
```

Why it works: it gives an audience and a goal (without those the script comes
out generic), and it stops the agent before the hook, which is the decision
everything else hangs off.

### From something you already wrote

```
Take THIS ARTICLE / THIS LINKEDIN POST / THIS DECK and turn it into a vertical
video of 45 seconds maximum for TikTok.

<paste the text, or give me the file path>

Don't summarize all of it: pick ONE idea, the one that stands on its own
without the rest of the article. Whatever doesn't fit, leave out — and tell me
what you cut.
```

### Corporate video, on brand

```
30-second vertical video for LinkedIn announcing WHAT.

Our brand:
- Colors: #0B5FFF primary, #101828 text, light background
- Type: closest thing to Inter
- How we sound: ONE REAL SENTENCE OF OURS
- We never say: BANNED WORDS

Read skills/vertical-video/references/corporate.md before writing.
Set the brand with scripts/brand.py (it writes src/brand.json), not in the components.
Any figure or claim about the product, ask me — don't invent it and don't
round it.
```

### Cutting a long video into clips

```
I have RECORDING.MP4, a 50-minute webinar. Pull the 4 best moments as vertical
clips with burned-in captions, 25 to 50 seconds each.

Before cutting, show me the candidate moments with their transcripts and let
me choose. The recording is ours and we have the right to use it.
```

### Studying a reference

```
Analyze REFERENCE.MP4 and tell me why it works: how long the hook runs, how
often it cuts, words per minute, what second the payoff lands on.

Then propose a structure with that same shape for a video about OUR TOPIC.
The structure, not the content — I don't want a copy.
```

### Fixing something that already exists

```
The video is close, but THE TEXT IN SCENE 3 READS TOO FAST / THE CAPTION SITS
ON TOP OF THE LOGO / THE VOICE SOUNDS ROBOTIC IN THE SECOND LINE.

Fix it and show me a still of that scene before rendering the whole thing.
```

```
Change the narration in scene 2 to: "NEW TEXT". Regenerate whatever needs it
and tell me the new total runtime.
```

### Variants to test

```
From the video that's built, make three versions that change ONLY the hook —
same length, same design, same scenes from 2 onward. I want to test which one
holds attention.
```

---

## Part 2 — With a free chat (copy and paste)

These never touch your machine. They return text; you paste it into the files.

### Master prompt — the whole script

Paste it as is. Answer what it asks and it returns both files, ready to use.

```
You're a scriptwriter for short-form vertical video (TikTok, Reels, Shorts).
You're going to write a 30-to-45-second script.

FIRST, ask me, all in one go:
1. What the video is about
2. Who it's for (specifically — who am I talking to)
3. What I want them to do after watching
4. Which platform it's going on
5. The tone, plus one example sentence that sounds like us

With my answers, return TWO code blocks and nothing else.

BLOCK 1 — script.json (what is SAID out loud):

{
  "engine": "edge",
  "voice": "en-US-AndrewNeural",
  "lang": "en",
  "tailSeconds": 0.35,
  "scenes": [
    { "id": "01-hook",  "text": "..." },
    { "id": "02-point", "text": "..." },
    { "id": "03-list",  "text": "..." },
    { "id": "04-stat",  "text": "..." },
    { "id": "05-cta",   "text": "..." }
  ]
}

BLOCK 2 — src/content.ts (what is SEEN on screen). The ids must match exactly,
in the same order. The available types are:

export const SCENES: Scene[] = [
  { id: "01-hook",  type: "hook",  kicker: "OPTIONAL", text: "..." },
  { id: "02-point", type: "point", title: "...", body: "optional" },
  { id: "03-list",  type: "list",  title: "...", items: ["...", "...", "..."] },
  { id: "04-stat",  type: "stat",  value: "80%", label: "..." },
  { id: "05-cta",   type: "cta",   text: "...", handle: "@handle" },
];

RULES, in order of importance:

1. DON'T INVENT DATA. No percentages, prices, dates, client names, or claims
   about what a product does. If you're missing something, write
   [MISSING: what you need] and list them at the end. An invented number
   becomes a promise nobody made.

2. The two texts are DIFFERENT. script.json is whole sentences written to be
   heard. content.ts is short fragments to be read at a glance. Never the
   same text in both.

3. The first sentence opens a question in the viewer's head. No "in this
   video I'm going to talk about". If the hook explains before it hooks,
   you've lost.

4. On screen: 6 words max in the hook and the cta, 5 max per list item,
   8 max in a title. It's a phone screen.

5. Write for the EAR: no acronyms you wouldn't say out loud, no symbols
   (%, &, #, →), no parentheses, no dashed lists. Spell out numbers that
   read awkwardly.

6. You can place a real pause with [pause:0.4] inside a script.json line.
   Use it right before an idea turns, not at every comma.

7. Total: 85 to 130 spoken words. More than that doesn't fit in 45 seconds
   without sounding rushed.

At the end, outside the blocks, write:
- Any [MISSING: ...] items left open
- Two alternative hooks for scene 1, in case the first doesn't land
```

### Hooks only

```
Give me 10 different opening lines for a vertical video about TOPIC, aimed at
AUDIENCE.

Each one: 14 words max, written to be said out loud, and it has to open a
question in the listener's head. No "in this video", no "today I'm bringing
you", no rhetorical questions nobody wants the answer to.

Use different patterns from each other: name the mistake out loud, promise one
specific outcome, start mid-story and explain later, contradict something
everyone assumes, or lead with an uncomfortable fact.

Flag which ones need a number I'd have to verify.
```

### Fixing narration that sounds robotic

```
These lines are going through a text-to-speech engine and they sound like a
machine. Rewrite them to sound like a person, without changing what they say:

<paste your lines>

Do: spell acronyms the way they're spoken, turn symbols into words, split long
sentences in two, add punctuation that sets the rhythm, and place [pause:0.3]
or [pause:0.5] where a person would breathe.

Don't: change the meaning, add information I didn't give you, or make it
longer.
```

### Adapting something you already have

```
Turn THIS into the spoken script for a 40-second vertical video:

<paste your text — the post, the press release, the brochure section>

Pick ONE idea, the one that holds up alone. Whole sentences, written to be
heard, 85 to 130 words total. Don't add a single fact that isn't in the text I
gave you. At the end, tell me what you left out.
```

### Corporate video, on brand

```
Write the script for a 30-second vertical video for LinkedIn.

Company: WHO WE ARE, IN ONE SENTENCE
Topic: WHAT THE VIDEO IS ABOUT
Audience: WHO WE'RE TALKING TO
Goal: WHAT WE WANT THEM TO DO
How we sound: <paste two or three real sentences from the company>
We never say: WORDS WE DON'T USE

Rules:
- No figure, percentage, award, certification or client name that I haven't
  given you. If one is needed, write [MISSING: ...].
- No "industry-leading", "end-to-end solutions", "synergy", "empowering".
- One idea per scene. Five scenes maximum.
- The last scene says what to do, not "follow for more content".

Output format: the script.json object and the content.ts array, same as the
master prompt.
```

---

## Pasting the results back

1. The first block replaces all of `script.json`.
2. The second block replaces **only** the `export const SCENES: Scene[] = [...]`
   part of `src/content.ts`. Everything above it — the types and the comments —
   stays.
3. Deal with the `[MISSING: ...]` items before generating the voice. That's the
   moment to get the number or cut the line.
4. Then:

```bash
python scripts/voice.py
python scripts/captions.py
npm run dev
```

---

## What rarely works

**"Make me a video about digital marketing."** With no audience and no goal,
you get something generic, and it doesn't matter who wrote it.

**Asking for the video and the hook in one go.** The hook sets the pace for
everything downstream. Approve it first, then build.

**Letting the AI supply the numbers.** It will write "73% of companies" because
it sounds right and fits the sentence. You're the one publishing that number.

**Asking for one text for both the voice and the screen.** It's the number one
reason a video sounds like a slide being read aloud.
