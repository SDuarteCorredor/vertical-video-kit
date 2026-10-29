# Video prompts

The start frame already carries the face, the outfit and the framing. The video
prompt is about **what moves and how the camera moves** — and about what must
not change.

## Template

```
SCENE        one line: where, when, what this shot is for in the edit
REFERENCES   @character (sheet / close-up), start frame, end frame if any
FIRST FRAME  the start image as given; positions of each character
ACTION       one action, concrete, with an ending: "…stops at the counter and smiles. The shot ends on the smile."
CAMERA       ONE named move: slow push-in · tracking shot following from behind · static locked-off ·
             handheld with a subtle breath · orbit 30° left · crane up. Lens if it matters (35 mm, 85 mm).
PERFORMANCE  expression and energy, in words an actor would understand
PHYSICS      what has weight: cloth, hair, a phone in the hand, footsteps
LIGHT        same as the start frame; name it again so it holds
AUDIO        real-world sound only (steps, room tone). Music goes in the edit.
STYLE        3D animated feature film / photoreal, matching the references
LOCKS        what must not change: "face, outfit and logo 100% match @character; no new objects;
             background unchanged; camera angle unchanged"
```

## What makes the difference

- **Name the camera move.** "Cinematic" or "dynamic" tells the model nothing,
  so it guesses, and guesses differently every time.
- **One move per clip.** Push-in *and* orbit *and* a crane is how bodies melt.
- **Say how the shot ends.** Without an end, the model fills the remaining
  seconds with something.
- **Repeat the identity block** at the top of every prompt, word for word.
- **Chain at most two or three clips** through last-frame-to-first-frame;
  errors add up. Then start again from the approved close-up.
- **Duration:** ask for the length the edit needs plus about half a second
  each side to cut on. Long single takes drift.

## Talking to camera (lip-sync)

The pattern that performs well, written for a 3D character:

```
Turn the image into a 9:16 video. Keep the setting, colors, framing and style exactly as they are.
Do not add elements, do not change the background, do not move the camera.
Subtle natural motion only: blinking, eyebrows, mouth.
The voice is fully lip-synced, with no delay, cuts or extra words.
The character looks straight at the viewer, with the same emotion as the image.
The spoken text must be EXACTLY: "<line>"
Language: Spanish. Voice: adult male, warm, clear and natural.
```

Generate one line per clip, not the whole script: a wrong word costs one short
clip instead of everything. If the narration in the edit is a separate voice
track, the character only needs to *look* like he is talking on the shots
where he is on screen.

## Compositing a character into a region

For an **Insert** shot — a selfie inside an app's camera box, a face on a TV —
generate the character alone, framed the way that region shows it (a phone
front camera: arm's length, slightly above eye level, wide lens), on mid-grey
or on a plausible background, and composite it into the real recording in the
edit. The app's interface, timer and buttons stay real.
