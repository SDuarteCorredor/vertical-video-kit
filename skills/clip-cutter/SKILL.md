---
name: clip-cutter
description: Turns a long horizontal video — a webinar, interview, podcast, lecture, livestream or talk — into vertical clips for TikTok, Reels and Shorts, with burned-in captions. Use it whenever someone wants to cut a long video into shorts, repurpose a recording, find the best moments of a talk, reframe 16:9 footage to 9:16, download a video to work with, or add captions to an existing clip.
---

# Long video into vertical clips

The content already exists. The job is finding the parts that stand on their
own and reframing them for a phone — not writing anything new.

## The flow

### 1. Get the file

If it is already on disk, skip this.

```bash
python scripts/download.py <url>
python scripts/download.py <url> --browser chrome   # signed-in content
```

Only download what there is a right to use. Someone else's video is someone
else's video, whatever the platform makes technically easy. If the person
asking does not own it and is not licensed to use it, say so instead of
downloading it — the one exception being reference you study privately and do
not republish, which is what the `reference-research` skill is for.

### 2. Find the moments worth cutting

```bash
python scripts/find_moments.py talk.mp4
python scripts/find_moments.py talk.mp4 --min 20 --max 55 --top 8
```

Transcribes the whole thing and proposes self-contained windows, ranked by how
well they open and how densely they are spoken.

**Treat the ranking as a shortlist, not a verdict.** It is reliable at
discarding the 90% that is throat-clearing and mediocre at picking the single
best clip. Read the transcript of the top few and choose yourself.

A clip is worth cutting when:

- It opens on a complete thought, not on "and so"
- It makes sense to someone who has not seen the rest
- It has a payoff inside the window, not after it

### 3. Cut and reframe

```bash
python scripts/cut.py talk.mp4 --start 412 --end 458 --captions
```

| Mode | What it does | When |
|---|---|---|
| `blur` | whole frame centered on a blurred fill | default; nothing is lost |
| `crop` | fills the screen, cuts the sides off | one speaker, centered |
| `fit` | whole frame on black bars | screen recordings, slides |

Use `--focus left` or `right` with `crop` when the person is not centered —
which is most interview footage.

`--captions` transcribes the cut clip and burns captions into it. Always use
it. A clip from a talk is nothing but speech, and most of the feed is muted.

### 4. Check before publishing

Watch the first two seconds. That is where a repurposed clip usually fails:
the speaker is mid-breath, or the first word is "and". Nudge `--start` a
second later and cut again — it takes seconds.

## When to build instead of cut

If the source has no usable hook, a cut clip will not gain one. Cases where
the right move is the **vertical-video** skill instead:

- The good line is 40 minutes in and needs setup to make sense
- It is a slide deck being read aloud
- The audio is unusable

You can also combine them: cut the clip here, and use it as background media
in a vertical-video project with your own narrated hook in front.

## Mistakes that cost the most

**Cutting on a timestamp instead of a thought.** A clip that starts mid-
sentence is over before it starts.

**Cropping blind.** Check that the speaker is actually in frame after
cropping — `crop` with default centering throws away whoever sits on the left
of a two-person interview.

**Clips over 60 seconds by default.** If the idea needs 90 seconds, fine, but
it should be a decision.

**Skipping captions** because the original had good audio. The original was
not watched on mute in a supermarket queue.

## Scripts

`scripts/download.py` · `scripts/find_moments.py` · `scripts/cut.py` — all
take `--help`.

Needs FFmpeg, `yt-dlp` and `faster-whisper`. The **vertical-video** skill's
`scripts/doctor.py --install` sets all of it up.
