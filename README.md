# vertical-video-kit

Make TikToks, Reels and Shorts in code — narration that doesn't sound like a
robot, word-by-word captions, and a real 1080×1920 render.

Built for AI coding agents (Claude Code, Cursor, and anything else that reads
skills), but every script runs on its own from a terminal.

<p align="center">
  <img src="docs/preview-hook.png" width="240" alt="Hook scene">
  <img src="docs/preview-list.png" width="240" alt="List scene">
  <img src="docs/preview-stat.png" width="240" alt="Stat scene">
</p>

## Why

Editing a short in a timeline means every correction is a manual redo. So
corrections don't happen, and videos ship with mistakes nobody was willing to
go back and fix.

Here the content lives apart from the design. Changing a line of narration is
editing one line and re-running a script — the voice regenerates, the scene
length changes to match, the animation re-syncs, and the captions follow.

Three problems this solves properly:

- **TTS that sounds like TTS.** Most of it is the text, not the engine. Every
  line is normalized for the ear before it reaches the voice — acronyms
  spelled out, symbols expanded, pacing punctuation — and you can place real
  pauses with `[pause:0.4]`. The default engine runs locally and free.
- **Captions as an afterthought.** They're generated from the audio that was
  actually rendered, so the highlight lands on the word being said. The layout
  reserves their band from the start.
- **Text under the platform UI.** TikTok and Reels cover the bottom ~380px and
  the right ~160px of your video. The template knows, and you can switch on an
  overlay to see it.

## Install

**As agent skills** — works with 75+ agents via [skills.sh](https://skills.sh):

```bash
npx skills add SDuarteCorredor/vertical-video-kit
```

**As a Claude Code plugin:**

```
/plugin marketplace add SDuarteCorredor/vertical-video-kit
/plugin install vertical-video-kit
```

**Or just clone it** and run the scripts yourself:

```bash
git clone https://github.com/SDuarteCorredor/vertical-video-kit
cd vertical-video-kit
python skills/vertical-video/scripts/doctor.py --install
```

## Quick start

```bash
python skills/vertical-video/scripts/new_project.py my-video
cd my-video

# write script.json (what is said) and src/content.ts (what is seen)

python scripts/voice.py        # narration + scene timings
python scripts/captions.py     # word-by-word captions
npm run dev                    # live preview
npm run render                 # output/video.mp4
python scripts/publish.py      # upload/video.mp4, encoded for the platforms
```

## What's inside

| | |
|---|---|
| `skills/vertical-video` | Script → voice → captions → render. The main one. |
| `skills/clip-cutter` | A long horizontal video → vertical clips with burned captions |
| `skills/reference-research` | Take apart a short that works and reuse its structure |
| `template/remotion-vertical` | The 9:16 Remotion project, scaffolded by `new_project.py` |

Each skill's `SKILL.md` is written to be read by a human too — the design
rules, hook patterns and voice craft are in `skills/vertical-video/references/`.

## Voice engines

Set `"engine"` in `script.json`. Swappable, same interface.

| Engine | Cost | Quality | Needs |
|---|---|---|---|
| `voicestudio` | free | highest, clones voices | [VoiceStudio](https://github.com/debpalash/VoiceStudio) running locally |
| `edge` | free | decent, audibly synthetic | `pip install edge-tts` |
| `openai` | paid | very natural | `OPENAI_API_KEY` |
| `elevenlabs` | paid | best commercial | `ELEVENLABS_API_KEY` |

The default is local and free, and nothing leaves the machine.

## Requirements

- **Node 18+** and **FFmpeg** — required
- **Python 3.9+** — for the scripts
- `pip install edge-tts faster-whisper yt-dlp` — voice fallback, captions,
  downloads

`python skills/vertical-video/scripts/doctor.py --install` checks all of it and
installs what it can.

## Built on

[Remotion](https://github.com/remotion-dev/remotion) for rendering ·
[VoiceStudio](https://github.com/debpalash/VoiceStudio) for local voice ·
[Whisper](https://github.com/openai/whisper) via
[faster-whisper](https://github.com/SYSTRAN/faster-whisper) for captions ·
[FFmpeg](https://ffmpeg.org) ·
[yt-dlp](https://github.com/yt-dlp/yt-dlp)

Remotion is free for individuals and small teams but
[requires a company license](https://remotion.dev/license) above that
threshold. The rest is free.

## Use it responsibly

Download only what you have the right to use. Clone only your own voice, or
one you have explicit permission to clone. Don't put claims, numbers or
promises in a video that nobody verified.

## License

MIT. See [LICENSE](LICENSE).

[Español](README.es.md)
