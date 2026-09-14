# Design for a 9:16 phone screen

Everything here is a mistake that is expensive to find late. Read it before
laying anything out, not after the first render looks wrong.

## The safe areas are the whole game

The canvas is 1080x1920, but you do not get to use all of it. Each platform
draws its own interface on top of your video:

| Region | Reserved | What sits there |
|---|---|---|
| Bottom ~380px | always | caption, username, music ticker, "follow" |
| Right ~160px | always | like / comment / share / sound |
| Top ~140px | usually | status bar, "Following \| For You" |

Those numbers are in `src/theme.ts` as `safe`. Nothing that must be read goes
inside them. Backgrounds and decoration are fine there — text is not.

```ts
export const SHOW_SAFE_AREAS = true;   // in src/theme.ts
```

Turn it on, look at a frame, turn it back off before rendering. Every video
that "looked fine in the editor" and shipped with its last line hidden under
the username skipped this step.

## Type

The viewer is holding the phone at arm's length and is not committed to you
yet. Type that would be generous in a presentation is barely adequate here.

- Body text below ~40px on a 1920-tall canvas is unreadable in the feed
- Titles carry the video: 80px and up, heavy weight
- One typeface. Two at most, and only if one of them is doing a real job
- Set `textWrap: "balance"` on headlines — a title that breaks one word onto
  its own line looks like a bug

## Contrast

Text over footage needs a scrim. `Chrome.tsx` puts a gradient behind every
media background for exactly this: without it, white text is legible for most
of the clip and invisible for the three seconds where the background is a
bright wall — and you cannot predict which three.

Never rely on a color alone to carry meaning; a chunk of the audience watches
in sunlight on an auto-dimmed screen.

## Motion

- **Something moves at all times.** A still frame for three seconds reads as a
  buffering video and people swipe.
- **But it does not have to be the text.** A slow background push is enough.
- **Entrances, not exits.** Animate things in; cut them out. Watching a card
  animate away is dead time.
- **Stagger by 4-6 frames**, no more. At 30fps, a 15-frame stagger means the
  last item of a list arrives a half second late, which feels broken.
- **Cuts, not crossfades.** A half-second dissolve reads as lag here, not
  polish. The template uses a 4-frame edge only to hide the seam.

## The first frame

It is the thumbnail, the autoplay frame and the scroll-stopper, and it gets
looked at before a single word is heard. It should be legible and finished on
its own. Do not open on a fade from black — for the length of the fade you are
showing nothing to someone who is deciding whether to stay.

## Density

One idea per scene. If a scene needs three lines of body text to make sense,
it is two scenes. The narration can carry nuance; the screen carries the
anchor.

Lists top out at three items. Four fit on the canvas and none of them land.

## Color

Take brand colors from a brand kit or a clean logo export — never sampled from
a video frame or a screenshot. Compression shifts them, and the drift only
becomes obvious once the wrong color sits next to the right one.

Use one accent consistently. Two accents in one video is what happens when
scenes get built from different sources on different days, and it is the
clearest tell that a video was assembled rather than designed.

Semantic colors (red, amber, green) only where the meaning is genuinely that.
As decoration they make a video look disorganized.

## Icons

Not emoji. 📄 💰 ✍️ render differently on every device, carry someone else's
art direction, and read as a school project. Use SVG drawn to one consistent
metric.
