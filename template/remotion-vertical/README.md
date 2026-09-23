# Vertical video project

Scaffolded by **vertical-video-kit**.

```bash
npm install                    # once — not needed inside the kit, which shares one install
python scripts/voice.py        # narration + scene timings
python scripts/captions.py     # word-by-word captions
npm run dev                    # Remotion Studio, live preview
npm run render                 # output/video.mp4
python scripts/publish.py      # upload/video.mp4, platform-ready
python scripts/share.py        # output/video_light.mp4, for email/WhatsApp
```

## The two files you edit

| File | Holds |
|---|---|
| `src/content.ts` | Everything **seen** on screen |
| `script.json` | Everything **said** out loud |

They are separate on purpose. Screen text can be fragments; narration needs
whole sentences. Scene ids must match between the two.

`src/brand.json` holds the look: a style to start from (bold, clean,
editorial, playful, corporate) plus the brand's colors, fonts and logo.
`python scripts/brand.py --help` fills it in — including from a design system
file — and `--compare` shows this video in every style side by side.

`src/timings.json` and `src/captions.json` are generated. Don't edit them.

`BRAND.md` is a brief to fill in once per company — who you are, how you sound,
which numbers you are allowed to state. Paste it into any AI chat before asking
for a script and what comes back sounds like you instead of like a press
release. Optional, and worth ten minutes.

## Checking your work

Rendering the whole video to look at one scene wastes minutes. Render a single
frame instead:

```bash
npx remotion still src/index.ts Short preview/frame.png --frame=120
```

Set `SHOW_SAFE_AREAS = true` in `src/theme.ts` to see where TikTok and Reels
draw their own interface, and make sure nothing you need read lands under it.
Set it back to `false` before rendering.
