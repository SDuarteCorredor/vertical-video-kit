# Character sheets

A character sheet is what the video model copies. If the sheet is vague, every
shot invents its own version of the character.

## The set, in this order

Each one uses the previously approved one as a reference.

| # | Sheet | Format | Why |
|---|---|---|---|
| 1 | **Turnaround**: front, 3/4, side, back, full body | 16:9, one image | Proportions and outfit from every side. One image, not four: panels generated separately drift apart. |
| 2 | **Face close-up**, head and shoulders, straight to camera | 4:5 | The anchor for every video prompt. One face only. |
| 3 | **Expressions**: neutral smile, two talking mouth shapes, laugh, thinking, wink | 3:2 grid | Lip-sync and reactions stay on-model. |
| 4 | **Script poses**: the actions the video actually needs (walking in, pointing, holding a phone…) | 16:9 | Start frames are built from these. |

For a second character who shares scenes (a receptionist, a client), make 1 and
2 as well. Then make **one test frame of both together** in the real location,
with the same light, before any video: that is where a 3D character next to a
photoreal person either works or does not.

## What every sheet prompt carries

```
NEED        what this image is for, format and size
REFERENCES  each attached image and the one thing taken from it
            ("Image 2 = body proportions only. Ignore the hard hat.")
CHARACTER   the identity block, identical in every prompt
LAYOUT      panels, framing, same scale and eye-line in every panel, labels or none
BACKGROUND  seamless neutral mid-grey #8A8A8A, never white, soft floor shadow
LIGHT       soft even studio light, gentle rim to separate from the grey
RENDER      the style: 3D animated feature film / real photo with camera specs
AVOID       the drift you expect: face or outfit changing between panels, extra props,
            misspelled logos, white background, cropped feet, extra fingers
```

The **identity block** is a paragraph: age, build, face shape, eyes, brows,
nose, skin, hair, the exact outfit with colors, any logo and how it reads.
Write it once, then paste it unchanged into every sheet and every video prompt.

## Mascots and existing brand characters

When the character already exists as approved artwork, the artwork is the
reference and the prompt only describes it, to reinforce what the model sees:

- Attach the main pose as Image 1 and say "match 100%".
- Attach variants (with a hat, with glasses, different shirt) only for a
  specific thing — face angle, body proportions — and say what to ignore.
- Name the default outfit and say "no glasses, no hat" when variants exist,
  or the model mixes them in.
- Logos on clothing: describe them exactly and put "misspelled logo" in AVOID.
  Fix small logo errors in the edit rather than spending generations on them.

## Photoreal people

Make them unique on purpose: specific face shape, a mark or two, real skin
texture, natural asymmetry, and an AVOID line that names the faces of earlier
characters. **Never attach a photo of another person "for the light"** — the
model copies the face along with it.

## Model limits seen in practice

Seedream 5.0 Lite (unlimited stills on Higgsfield plans, used for every sheet):
prompts up to 3000 characters, reference images with aspect ratio between 0.4
and 2.5 (pad a wide logo onto a taller canvas before attaching it).
