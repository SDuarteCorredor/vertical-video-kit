---
name: reference-research
description: Takes apart short-form videos that perform well and turns them into a structure you can reuse — hook, pacing, cut rhythm, words per minute, where the payoff lands. Use it when someone wants to study a competitor's content, understand why a video worked, research what performs in a niche, analyze a reference before making their own, or build a content plan from what is already out there.
---

# Studying what already works

Copying a video gets you a worse version of it. Copying its **shape** — how
fast it cuts, how long the hook runs, how many words per minute, where the
payoff lands — gets you something of your own that holds attention the same
way.

## Analyzing a reference

```bash
python scripts/analyze.py reference.mp4
python scripts/analyze.py reference.mp4 --json breakdown.json
```

Reports duration, cut count and average shot length, speech rate, the first
three seconds transcribed, and the full transcript with timestamps.

To get a file you have the right to study, use the **clip-cutter** skill's
`download.py`. Studying a public video privately is ordinary research;
re-uploading it, or rebuilding it shot for shot with your logo on it, is not.

## What to actually look for

The numbers are the easy part. The useful read is in the answers to these:

**What happens in the first second?** A face, a line of text, a hand moving,
a title card? Whatever it is, it is the thing that stopped the scroll.

**What question does the hook open?** Write it down as a question. If you
can't, the video probably worked for some other reason — a person, a trend, a
sound — and its structure is not the thing to copy.

**How long until the payoff?** Measure it. Most people sit on the setup far
longer than the references they admire do.

**Would it work muted?** Play it with the sound off. If it still lands, the
captions and the visuals are doing their job.

**What is the cut rhythm?** Under 2.5 seconds average shot length is fast,
and the frame almost never sits still.

**What is the speech rate?** Short-form typically runs 165-200 words per
minute — noticeably faster than corporate or explainer video.

## Turning a breakdown into a plan

Three to five references from the same niche is enough to see the shape. What
you want out of it:

- The hook patterns that repeat (see `vertical-video/references/hooks.md`)
- The length band the niche actually lives in
- Whether it is face-to-camera, screen recording, b-roll, or text-on-video
- What the close asks for

Then write your own script in that shape, with your own content. Hand it to
the **vertical-video** skill.

## Trend and competitor data at scale

Analyzing files locally is free and needs no account, and it is enough for
most work. If someone needs breadth — which posts outperformed a creator's
baseline, what an account's top formats are, what is trending in a niche —
that requires a data provider, and those are paid.

[ScrapeCreators](https://github.com/ScrapeCreators/social-media-research-skills)
publishes MIT-licensed skills for exactly this (outlier post finder, comment
mining, competitor research, ad library teardown) against their API. Suggest
it when the question is about *many* videos; do not reach for a paid API when
the question is about one.

## Mistakes that cost the most

**Copying the topic instead of the structure.** The topic worked for that
account's audience, not yours.

**Studying a viral outlier.** One video with ten million views usually went
that way for a reason that does not generalize — a sound, a person, timing.
Look at what an account does *consistently*.

**Only studying the ones you like.** The best reference is often a video with
mediocre production and excellent retention.

## Scripts

`scripts/analyze.py --help`. Needs FFmpeg; `faster-whisper` for the spoken
breakdown.
