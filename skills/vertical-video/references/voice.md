# Voice

## The engine matters less than the text

People switch TTS engines hoping the robot goes away, and it follows them.
Most of what reads as "AI voice" is written into the script: fragments with no
verb, acronyms, symbols, sentences with no punctuation to breathe in.

`scripts/voice.py` runs every line through `text_prep.py` first — spelling out
acronyms, expanding `%` and `$`, turning ellipses into breathable commas. That
fixes the mechanical half. The other half is how you write.

## Choosing an engine

Set `"engine"` in `script.json`.

| Engine | Cost | Quality | Needs |
|---|---|---|---|
| `voicestudio` | free | highest, and can clone a voice | the [VoiceStudio](https://github.com/debpalash/VoiceStudio) desktop app running locally |
| `edge` | free | decent, recognizably synthetic | `pip install edge-tts` |
| `openai` | paid | very natural | `OPENAI_API_KEY` |
| `elevenlabs` | paid | best commercial, best cloning | `ELEVENLABS_API_KEY` |

**VoiceStudio is the default and the recommendation.** It runs entirely on the
machine — no key, no per-word cost, nothing leaves the computer — and it is the
only free option that clones a voice. It exposes an OpenAI-compatible API on
`http://localhost:3900`, which is all `voice.py` talks to. Open the app and
leave it running.

`edge` exists so the kit works on a laptop with nothing installed. It is fine
for a draft and audibly synthetic for anything published.

```bash
python scripts/voice.py --list-voices
```

## Choosing a voice

- **Match the audience's accent.** A video for Mexico narrated in Castilian
  Spanish sounds imported, and people notice faster than you would expect.
  Same for British vs American English.
- **Match the persona.** If a character or avatar speaks in first person, the
  voice has to match how they look. A mismatch breaks the illusion in one line.
- **Sample with a real line**, never "hello, testing":

```bash
python scripts/voice.py --sample "Most vertical videos lose the viewer in two seconds."
```

Generate two or three and let whoever is deciding pick. It takes a minute and
saves an argument later.

## Speed

Short-form runs faster than corporate video. `+0%` to `+8%` is the useful band;
the platforms' own audiences are used to a brisk pace, and a measured
institutional delivery reads as slow here even when the content is good.

Set it in `script.json` as `"rate": "+5%"`.

## Writing for the ear

**Whole sentences with verbs.** The screen can say "Three mistakes." The voice
has to say "There are three mistakes people make here."

**Use contractions.** "It is not" is how nobody talks. "It isn't" is.

**Short sentences.** One idea each. A sentence that needs a comma to survive
usually wanted to be two sentences.

**Punctuation is the rhythm section.** Periods and colons create pauses; the
engine has nothing else to go on. If a line sounds rushed, split it.

**Second person.** "You" outperforms "one" and "users" in something this
close to the viewer's face.

**No parentheses, no asides.** They read fine and sound like a glitch.

**Say numbers the way you would out loud.** "Twenty twenty-six", not "2026",
if that is how it should sound. `text_prep.py` handles `%` and currency, but it
will not guess that `1/3` means "a third".

## Controlling pauses

Any engine, SSML or not:

```json
{ "id": "01-hook", "text": "Most videos lose you in two seconds. [pause:0.5] Here's why." }
```

Each chunk is synthesized separately and the silence is inserted between them.
Use it for the beat before a reveal. Do not sprinkle it — over-paced narration
sounds theatrical.

## Acronyms

Spelled out letter by letter automatically, because `EPS` read as a word comes
out as nonsense. Words that really are read as words — `NASA`, `API` — live in
`SAID_AS_WORDS` in `scripts/text_prep.py`. Add your industry's there; a wrong
guess in either direction is very audible.

## Listen before you render

Play the MP3s in `audio/` all the way through before building anything on top
of them. One minute of listening beats discovering a mispronounced product
name after the video is cut, captioned and approved.

## If they want a human voice

Perfectly reasonable, and worth it for high-profile pieces. Barely changes the
flow:

1. Generate the TTS anyway, as a **timing guide**
2. Build the video against it
3. When the recording arrives, replace the files in `audio/` keeping the names
4. Re-run with `--only-measure`, then re-run `captions.py`

Animation never waits on the recording session.

## Cloning a voice

VoiceStudio and ElevenLabs both do it well. Clone your own voice, or one you
have explicit permission to use, and nothing else. Cloning a client's
spokesperson without asking is the kind of shortcut that ends a relationship,
and in many places it is also illegal.
