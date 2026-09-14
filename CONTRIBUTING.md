# Contributing

Issues and pull requests are welcome.

## What is most useful

- **Scene types.** The template ships with six. Real work needs more —
  before/after, comparison, chat thread, code, countdown.
- **Voice engine adapters.** `scripts/voice.py` takes text and returns MP3
  bytes; a new engine is one function plus a row in the table.
- **Language coverage in `text_prep.py`.** Symbol expansion currently covers
  English and Spanish. Adding a language is a dictionary entry, and getting it
  right needs a native speaker.
- **Platform safe areas.** They shift when the apps change. If a number in
  `theme.ts` is wrong, a screenshot in the issue settles it fast.

## Ground rules

**Keep content separate from design.** A change that makes editing text
require touching a component is going the wrong way.

**Audio drives timing.** Nothing should hardcode a scene duration.

**No brand assets.** This repo stays generic. The placeholder palette is
placeholder on purpose.

**Comments explain why, not what.** The code says what it does.

## Testing a change

```bash
cd template/remotion-vertical
npm install
npm run check
python scripts/voice.py --engine edge --voice en-US-AndrewNeural
python scripts/captions.py
npx remotion still src/index.ts Short preview/f.png --frame=60
```

Look at the frame. Type checking does not catch a layout that renders text
under the platform UI.
