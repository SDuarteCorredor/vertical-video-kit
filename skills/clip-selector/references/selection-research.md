# Where the selection rules come from

Researched in November 2026 from 44 popular YouTube videos (2024–2026) about
short-form editing, AI clipping and selects, and from the written sources
that describe the same tools and practices.

**How solid it is.** YouTube couldn't be reached from the research
environment, so no transcript was read first-hand and no view count was
checked. For 12 videos a third-party summary of that exact video was read.
For the other 32, only the title and description. Many written sources are
clipping-tool vendors (Opus, autoclip, Cutback, ChatCut), so they have an
interest in the claims. The only study built on real data is Paddy
Galloway's, from 2023. Treat the numbers as practitioners' defaults, not
laws.

## What makes a clip worth keeping

| Finding | Sources |
|---|---|
| It stands alone for a stranger who never saw the rest. A clip is a front door for new viewers, not a highlight for fans. | Podcast clipping guides; Grace Andrews on *The Diary of a CEO* clips |
| The hook is the first line *and* the first frame, and both promise the same thing. Visual hooks beat spoken ones. | Kallaway, "Copy This Hook" and "Irresistible Hooks"; Jenny Hoyos (TED, Jan 2025); Galloway |
| The payoff is non-negotiable: hook → minimal context → development → reward. Every sentence in the middle advances the promise or gets cut. | Hormozi, "Hook → Retain → Reward"; podcast clipping guides |
| A story turn beats a flat statement: question → conflict ("but…") → tension → an abrupt, satisfying end. | Jenny Hoyos (TED; Creator Science interview) |
| Emotion first, then story, then rhythm. Technical continuity is what gets sacrificed. | Walter Murch, Rule of Six |
| "Would the target viewer send it to someone?" | Steven Bartlett / DOAC, via Kallaway |

## How professionals select from raw footage

- Organize first, then build per-topic **stringouts**, then a **selects**
  sequence, then the rough cut. *(Frame.io; documentary-editing courses)*
- Transcribe everything and make a paper edit before touching the timeline.
  *(NYFA, Documentary Film Academy, Noam Kroll)*
- Tag lightly on the first pass. Most keywords added early are never used.
  *(Frame.io, "Log interviews better")*
- Log B-roll separately. *(Frame.io; Premiere Media Intelligence)*
- Performance beats technical cleanliness, unless the flaw is one the viewer
  will notice. The best version is sometimes assembled from two takes.
  *(Backstage; Frame.io)*
- Keep the alternates. DaVinci Resolve 20's IntelliScript builds the cut
  from the best takes and stacks the alternates on extra tracks for the
  editor. That is the handover shape `selects.py` copies.

## What automatic clippers get wrong (so you don't)

- **They lose context and jokes.** They don't see why a setup matters to its
  punchline. *(Reddit-sourced Opus review roundups)*
- **The edges are wrong.** Clips start after the setup or cut the punchline
  or reaction, and cut mid-sentence when people talk over each other.
  *(techpresso; scalereach)*
- **A high share of their clips is thrown away.** One 30-day test kept 47 of
  76 clips as-is, fixed 19 and threw away 10. Reviews generally put the
  discard rate at 20–40%. *(scalereach; techpresso; bigvu)*
- **Virality scores are inconsistent** from one run to the next. Use them
  for sorting, never as the verdict. *(Opus help docs; reviews)*
- **They miss silent, visual moments.** They listen for speech patterns.
  *(gaming reviews)*
- **Transcribers merge rapid repeats**, so a stutter comes back after a cut
  made on word timestamps. *(XDA, "I turned my terminal into a video
  editor using Claude Code")*

An agent that reads the **whole** transcript fixes the context and edge
errors. Looking at frames covers the visual blind spot.

## Numbers practitioners use

| Topic | Default |
|---|---|
| Clip length | 20–60 s. 45–75 s when the arc earns it. Galloway's data: 50–60 s Shorts that are actually watched do best. Hoyos aims for about 34 s. |
| Setup | Longer than about 15 s of setup makes it a segment, not a clip. |
| Hook window | The first 1–3 s. |
| End point | About 2–3 s after the payoff: keep the laugh or the reaction. |
| Yield | About 10–20 usable clips from an hour of conversation. |
| Expected misses | Even a good first pass is wrong 20–40% of the time, so propose 1.5–2× what is needed. |
| Pace | In short form the picture changes every 3–5 s. That is the editor's job, but it is a reason to log B-roll. |

## Videos with the most to learn from

These are the ones to read first if YouTube becomes reachable:

- Kallaway, *Copy This Hook*: https://www.youtube.com/watch?v=8VolLwMCLuY
- Jenny Hoyos at TED, *The Secret to Telling a Great Story — in Less Than 60
  Seconds*: https://www.youtube.com/watch?v=ZmNpeXTj2c4
- *Shorts Genius Shares Everything She Knows* (Creator Science):
  https://www.youtube.com/watch?v=As7abwNhG7Y
- *Opus Clips vs Vidyo vs Vizard: Brutally Honest Review*:
  https://www.youtube.com/watch?v=VrVVP-XaVRc
- *Podcast Clips: How I Turn Long-Form Videos Into Short Clips*:
  https://www.youtube.com/watch?v=FdBDrZ1JMe8
- *How I Edit Hours of Interview Footage for a Documentary*:
  https://www.youtube.com/watch?v=xKoAsZcc0oo
- *How To Stay Organized with Massive Documentary Edits (Full Selects
  Workflow)*: https://www.youtube.com/watch?v=1DZlKwQ7bIQ
