# Captions

Most of the feed is watched with the sound off. Captions are not accessibility
garnish here — they are the primary channel, and the voice-over is the
enhancement. Build them in from the start; the template reserves their band
before any scene is laid out.

## How they are made

```bash
python scripts/captions.py
```

Transcribes the narration MP3s that `voice.py` just produced and writes
word-level timings to `src/captions.json`.

Transcribing the audio rather than splitting the script is deliberate: the
highlight then lands on the word actually being said, including wherever the
engine decided to pause. Splitting the script by character count drifts a
little more with every sentence.

| Engine | Speed | Accuracy |
|---|---|---|
| `faster-whisper` (default) | fast on CPU | good |
| `whisper` | slower | same model, heavier runtime |
| `estimate` | instant | rough — spreads words evenly, drifts |

`--model small` or `medium` is worth it for strong accents or noisy audio.
`base` is enough for clean synthetic narration.

## Style rules

**Two to four words at a time.** More turns watching into reading. The
template uses three (`PER_LINE` in `Captions.tsx`).

**Highlight the word being said.** That is what makes the eye track along
instead of re-reading the line. Any high-contrast color works; the template
uses a yellow that survives both dark and bright backgrounds.

**Stroke, not shadow.** A drop shadow disappears the moment the background
behind it goes light. A thick outline works everywhere.

**Above the platform UI, never inside it.** `captionBaseline` in `theme.ts`
puts them there. Captions that land in the bottom band are hidden behind the
username and description for most of the audience.

**Don't caption music or sound effects.** This is not broadcast subtitling.

## When the transcript is wrong

Product names, industry terms and names of people are where Whisper guesses.
`src/captions.json` is a plain list of words — fix the text field of the ones
that are wrong and leave the timings alone. Do not re-run the script
afterwards or your fixes are overwritten.

If the same term is wrong every time, it is usually being mispronounced by the
voice engine too. Fix it in `script.json` phonetically and both problems go
away at once.

## Burned in, not a sidecar file

These captions are rendered into the video. That is on purpose: TikTok and
Reels ignore `.srt` sidecars, and their own auto-captions are styled by them,
not by you, and are frequently wrong.

The one place a sidecar still helps is YouTube Shorts, which does index
uploaded caption files for search.
