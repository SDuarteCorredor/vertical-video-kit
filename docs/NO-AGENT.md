# Running it without Claude Code, without Codex, and without paying

**Short answer: this kit needs no AI at all.**

The scripts are ordinary Python and Node. The only thing an AI agent does is
*write your text and edit two files for you*. You can do that yourself in five
minutes, or ask any free AI chat to do it and paste the result back.

This document is for someone sitting at a machine with nothing installed and no
intention of paying for a subscription.

> Español: [`SIN-AGENTE.md`](SIN-AGENTE.md) · Copy-paste prompts:
> [`PROMPTS.md`](PROMPTS.md)

---

## 1. What you must install

This part is the same whichever AI you use, or none at all:

| | What for | Cost |
|---|---|---|
| **Node 18+** | rendering the video (Remotion) | free |
| **FFmpeg** | measuring audio, building pauses, encoding the MP4 | free |
| **Python 3.9+** | the voice, caption and publish scripts | free |

Plus four Python packages: `edge-tts` (the voice), `faster-whisper` (the
captions), `yt-dlp` (downloads, only if you're cutting up a long video) and
`pillow` (contact sheets, only if you're editing phone footage).

### The easy way: one command

Open a terminal, go where you want the project, and:

```bash
git clone https://github.com/SDuarteCorredor/vertical-video-kit
cd vertical-video-kit
```

Then the only command that matters:

```bash
python install.py
```

It installs Node, FFmpeg and the Python packages, creates your first project,
and **opens the Remotion studio in your browser**. That's the live preview —
it updates itself every time you save a file.

If `python` isn't recognised, try `python3` (macOS, Linux) or `py` (Windows).

**If Python isn't installed yet**, start with the bootstrap script, which
installs it:

```powershell
powershell -ExecutionPolicy Bypass -File setup.ps1     # Windows
```

```bash
bash setup.sh                                          # macOS, Linux
```

If it installs Node or FFmpeg on Windows, **close the terminal and open a new
one** before continuing — that's how Windows notices they exist. Then
`python install.py`.

### Opening the studio again

It stops when you shut the machine down, or kill the process. To bring it back:

```bash
python skills/vertical-video/scripts/studio.py my-video
```

Or `npm run dev` from inside the project folder.

> No `git`? On the repository page on GitHub: green **Code → Download ZIP**,
> then unzip. Same thing.

### Installing by hand

<details>
<summary><b>Windows</b></summary>

```powershell
winget install OpenJS.NodeJS.LTS
winget install Gyan.FFmpeg
winget install Python.Python.3.12
# close the terminal, open a new one, then:
pip install edge-tts faster-whisper yt-dlp pillow
```
</details>

<details>
<summary><b>macOS</b></summary>

```bash
# if you don't have Homebrew:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

brew install node ffmpeg python
pip3 install edge-tts faster-whisper yt-dlp pillow
```
</details>

<details>
<summary><b>Linux (Debian / Ubuntu)</b></summary>

```bash
sudo apt update
sudo apt install -y nodejs npm ffmpeg python3 python3-pip python3-venv
# apt's nodejs is usually old; if `node -v` is below 18:
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
nvm install 22

pip3 install edge-tts faster-whisper yt-dlp pillow
```

If `pip3` says *externally-managed-environment*, use a virtualenv — `setup.sh`
does this for you:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install edge-tts faster-whisper yt-dlp pillow
```

That `activate` line has to be run in every new terminal.
</details>

To confirm it all landed:

```bash
python skills/vertical-video/scripts/doctor.py
```

---

## 2. Making the video

Four routes. All of them end at the same MP4.

### Route A — the wizard (start here if a terminal is unfamiliar)

```bash
python skills/vertical-video/scripts/wizard.py
```

It asks five things — folder name, which accent, and the narration lines — and
does the rest by itself: creates the project, generates the voice, builds the
captions, and renders if you say yes.

No AI is involved. You write the lines.

### Route B — by hand, editing two files

```bash
cd my-video     # the one install.py made for you
```

Open the `my-video` folder in any text editor — Notepad works,
[VS Code](https://code.visualstudio.com) is free and easier.

**Only two files get touched.** Everything else is machinery.

| File | Holds |
|---|---|
| `script.json` | everything **said** out loud |
| `src/content.ts` | everything **seen** on screen |

They're different texts on purpose. The screen can carry fragments; the voice
needs whole sentences. Writing one and pasting it into the other is the single
most common reason a video sounds like a machine reading a slide.

`script.json` looks like this — change `voice` and replace the text:

```json
{
  "engine": "edge",
  "voice": "en-US-AndrewNeural",
  "lang": "en",
  "scenes": [
    { "id": "01-hook",  "text": "Your first sentence, the one that stops the scroll." },
    { "id": "02-point", "text": "The second idea, as a whole sentence." },
    { "id": "03-cta",   "text": "What you want them to do after watching." }
  ]
}
```

Free voices that hold up:

| Audience | Female | Male |
|---|---|---|
| US English | `en-US-AriaNeural` | `en-US-AndrewNeural` |
| UK English | `en-GB-SoniaNeural` | `en-GB-RyanNeural` |
| Colombia | `es-CO-SalomeNeural` | `es-CO-GonzaloNeural` |
| Mexico | `es-MX-DaliaNeural` | `es-MX-JorgeNeural` |
| Spain | `es-ES-ElviraNeural` | `es-ES-AlvaroNeural` |

Use the accent of the country you're talking to. `python scripts/voice.py
--list-voices` prints the full catalogue.

In `src/content.ts` the `id`s must **match** the ones in `script.json` — that's
how narration, timings and captions find each other.

Then:

```bash
python scripts/voice.py        # narration + how long each scene lasts
python scripts/captions.py     # word-by-word captions
npm run dev                    # live preview in your browser
npm run render                 # output/video.mp4
python scripts/publish.py      # upload/video.mp4, encoded for the platforms
python scripts/share.py        # output/video_light.mp4, small enough for WhatsApp
```

Changed a line? Re-run `voice.py` and `captions.py`. The scene re-times itself.
That's what a correction costs here.

### Route C — with Codex (or any agent)

**Clone first, and start the agent inside the folder.** In that order:

```bash
git clone https://github.com/SDuarteCorredor/vertical-video-kit
cd vertical-video-kit
codex
```

The order matters. Codex reads the `AGENTS.md` of the folder it starts in, and
that file **opens** with the install command and the instruction to leave you
looking at the studio. Start Codex in an empty folder and paste the link for it
to clone, and it may not read `AGENTS.md` in the same turn — then it improvises.

Once you're in:

```
Install this and leave the studio open for me.
```

Three things worth knowing first — friction, not faults:

- **Codex asks permission before every command.** Say yes. That's normal.
- **Codex cannot type an administrator password.** On Linux, if Node or FFmpeg
  are missing, `install.py` can't install them from in there: it prints the
  exact `sudo apt install ...` command for you to run in a normal terminal, and
  then you continue. Doesn't apply on Windows or macOS — winget and brew don't
  need sudo.
- **If the studio doesn't stay open**, open it yourself in a normal terminal:
  `cd my-video && npm run dev`. Some agents kill the processes they leave
  running when the command finishes.

Prefer to skip all that? Run `python install.py` yourself in a terminal (Route
A or B) and use Codex only to write the text.

Then ask for the video in plain language:

```
Make me a 40-second vertical video about OUR ONBOARDING PROCESS, for
operations managers, US English, male voice.
Give me three hook options before building anything.
```

More examples in [`PROMPTS.md`](PROMPTS.md).

### Route D — let a free AI write the text

If you'd rather not install an agent at all: open [`PROMPTS.md`](PROMPTS.md),
copy the script prompt, paste it into **any** free chat — ChatGPT, Claude, Gemini, Copilot, DeepSeek, whichever — answer what
it asks, and it hands back `script.json` and `content.ts` ready to paste. Then
continue with Route B.

This needs nothing installed and costs nothing, because the chat only writes
text: your machine makes the video.

---

## 3. Which coding agents are free?

An agent (Claude Code, Codex CLI…) does Route B for you: edits the files and
runs the commands so you don't have to. Convenient, **not required**.

| Tool | Free? | What it needs |
|---|---|---|
| **No AI** | yes | nothing. The wizard, or the two files by hand |
| **Any web chat** | yes | a free account. Copy and paste ([`PROMPTS.md`](PROMPTS.md)) |
| **Codex CLI** (OpenAI) | **yes, with limits** | a free ChatGPT account. `npm i -g @openai/codex` |
| **Gemini CLI** (Google) | **yes** | a Google account. ~1,000 requests a day |
| **GitHub Copilot** | limited free tier | a GitHub account, inside VS Code |
| **Claude Code** | **no** | a paid Claude plan (Pro, from ~US$20/mo) or API credits |

**Can you install this with Codex?** Yes. Codex CLI reads the
[`AGENTS.md`](../AGENTS.md) at the repository root — the open standard that
Cursor, opencode, Copilot and Windsurf also understand. Clone the repo, run
`codex`, and ask for what you want.

**Is Codex paid-only?** No. Codex CLI signs in with a **free** ChatGPT account;
the free tier covers short local coding tasks, which is exactly the size of the
work here. Paying (Plus, ~US$20/mo) raises the usage limits and adds the cloud
features, but isn't needed for this kit.

**Claude Code is paid.** The free Claude plan doesn't include it — you need Pro,
Max, Team or Enterprise, or API credits. Which is why the kit works without it.

### Installing them

```bash
# Codex CLI — free with a ChatGPT account
npm install -g @openai/codex
codex          # first run sends you to the browser to sign in

# Gemini CLI — free with a Google account
npm install -g @google/gemini-cli
gemini
```

Gemini CLI looks for `GEMINI.md` by default. To point it at this repo's
`AGENTS.md`, create `.gemini/settings.json` inside the repository:

```json
{ "context": { "fileName": ["AGENTS.md", "GEMINI.md"] } }
```

And for anyone who does have Claude Code:

```
/plugin marketplace add SDuarteCorredor/vertical-video-kit
/plugin install vertical-video-kit
```

---

## 4. When something breaks

| What you see | What happened |
|---|---|
| `'python' is not recognized` | Windows: reinstall Python with **Add python.exe to PATH** ticked, or use `py` instead of `python` |
| `FFmpeg is missing` | Not on the PATH. Close the terminal, open a new one. Still missing? Reinstall |
| `VoiceStudio is not answering` | You're on the `voicestudio` engine without the app open. Set `"engine": "edge"` in `script.json` |
| `edge-tts is missing` | `pip install edge-tts` |
| Captions come out empty | `faster-whisper` is missing. `pip install faster-whisper`. First run downloads the model, so it's slow |
| `node -v` below v18 | Remotion needs 18+. Get a current build from [nodejs.org](https://nodejs.org) |
| `externally-managed-environment` | Use a virtualenv: `python3 -m venv .venv && source .venv/bin/activate` |
| Text hidden behind TikTok's UI | Set `SHOW_SAFE_AREAS = true` in `src/theme.ts` and look. See [`design.md`](../skills/vertical-video/references/design.md) |
| The render takes forever | Normal the first time — Remotion downloads a Chromium. It's faster after that |
| The studio doesn't open by itself | Paste the address it printed (`http://localhost:3000`) into your browser |
| `localhost:3000` doesn't answer | Check `studio.log` inside the project folder — the error is in there |
| Port 3000 is taken | It moves to 3001, 3002… Use the address it printed |

To measure a video that already exists and find out what's wrong with it:

```bash
python skills/vertical-video/scripts/diagnose.py my-video.mp4
```

---

## 5. The minimum you need to know so it doesn't look homemade

Three things, and they're the ones that break most often:

**The first two seconds.** A 40-second video that opens badly isn't a
40-second video, it's a 2-second one. The first sentence has to open a question
in someone's head. "In this video I'm going to talk about..." is a goodbye.

**Nothing important at the bottom or on the right.** TikTok and Reels cover the
bottom ~380px and the right ~160px with their own interface. Text there isn't
"a little tight" — it's invisible.

**Captions aren't a finishing touch.** Most of the feed is watched with the
sound off. No captions, no message.

The rest is written out in
[`skills/vertical-video/references/`](../skills/vertical-video/references/) —
hooks, voice, captions, design and corporate video.
