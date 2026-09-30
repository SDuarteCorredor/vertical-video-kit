# Analysing a reference, shot by shot

`scripts/breakdown.py` gives you numbers and sheets. The analysis is you looking
at every sheet and filling one card per reference. Do not skim: the person asked
for "toma por toma, recursos, fuentes, colores, iluminación, guion, formato".

## What the tools give you

For each video in `<folder>/analisis/`:

- `<id>_tomas.jpg` — one frame per detected cut, labelled `#n start (length)`.
- `<id>_timeline.jpg` — a frame every 1.5–3 s. **Most references are one or two
  camera takes with graphics changing on top**; the cut detector cannot see
  those, the timeline can.
- `<id>_tomas.json` — cut list, per-shot brightness (0–1), saturation (0–1) and
  a 5-colour palette.
- `<id>_voz.json` — transcript with timestamps and words per minute.
- `resumen.md` (from `fetch_refs.py`) — account, likes, comments, duration,
  caption, date.

Check the aspect ratio too (`ffprobe`): creators often post 16:9 or 4:3 on
Instagram on purpose for a cinematic look. That is a decision to raise with the
person, not an accident to ignore.

## The card

```markdown
### @account — "<hook or title>" (<id>) · <dur> s · <aspect> · <likes> likes · <comments> com.
- **Format:** essay / explainer / list / tier list / montage / vlog / skit / carousel of videos…
- **Shots:** A-roll (where, framing, camera height, lens) + B-roll (list what is shown and on which line).
  Cut rhythm, punch-ins, second angle.
- **Art direction:** light (key source, practical lamps in frame, coloured background light),
  background, wardrobe as signature, props (mic in hand, notebook).
- **Graphic layer:** what appears and when — cut-outs, stickers, screenshots as evidence,
  chapter cards, key-word cards, lists to save, numbering device (billiard balls, I/II/III).
- **Typography:** families (serif italic / grotesk / condensed / mono spaced caps / rounded display),
  sizes, where on screen, case, the one accent colour.
- **Subtitles:** size, position, colour, word-by-word or line, outline/pill.
- **Colour & light numbers:** brightness, saturation, palette; warm/cool; contrast.
- **Script:** hook (verbatim) → structure beat by beat → value → close/CTA (verbatim). wpm.
- **Sound:** voice only / music under / trending audio / lyrics as typography.
- **Series:** name, number, recurring close.
- **Why it worked:** the mechanism in one or two lines (identity, sendable, save-worthy,
  trend-jack, debate, utility, craft).
- **What to replicate / what not:** the shape to keep; anything off-limits for this brand
  (politics, copyrighted film clips, a tone that isn't theirs).
```

## Comparing sets

Put the numbers of each batch side by side (median duration, share of one-take
videos, median shot length, brightness, saturation, aspect ratios). In the first
68 references analysed the finding was stable: **most are 1–2 camera takes;
production value comes from art direction, the graphic layer and script
structure**. Check whether the new set confirms or breaks that.

## Mistakes

- Choosing takes or references from an unlabelled grid.
- Studying only the ones you like, or only viral outliers.
- Copying the topic instead of the structure.
- Reporting a restricted/private post as analysed. Say it was not, and ask for a
  screen recording.
