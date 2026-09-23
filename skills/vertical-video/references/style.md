# The look: ask, don't assume

Every project starts in the **bold** style: dark, heavy white type, violet and
green. It is a placeholder, not a decision. A video that ships in it looks like
this kit, not like the person's brand, and they will notice the moment it sits
next to their other posts.

So before building scenes, settle the look. It takes one message and one
image, and it saves the round of "can we make it more like us" that otherwise
comes after the render.

Everything below ends up in `src/brand.json`, and `scripts/brand.py` writes
that file for you. Nothing about the look is set in a component.

## Ask in one message

In the person's language, all at once, with options — not a questionnaire
spread over ten turns. Skip what they already told you. Something like:

> Before I build it, a few questions about the look:
>
> 1. **Do you have brand guidelines?** A brand manual (PDF), a design system,
>    Figma tokens, a website whose style we should match — any of those.
> 2. **Logo?** Ideally SVG, or a PNG with a transparent background. Should it
>    appear in a corner the whole time, big at the end, both, or not at all?
> 3. **Colors?** Main color and a second one, as hex codes if you have them
>    (#0B5FFF). Light or dark background?
> 4. **Font?** The brand's typeface, if there is one — the name, or the font
>    file.
> 5. **Feel?** Pick one, or show me an account or video whose style you like:
>    bold (dark, creator style) · clean (light, airy) · editorial (serif,
>    magazine) · playful (saturated, round, bouncy) · corporate (white and
>    navy, measured).
> 6. **Captions?** Outlined words · words on a solid block · the active word
>    in a colored pill.
>
> If you don't have any of this, say so — I'll pick a style for the audience
> and show you the options side by side.

## Turn the answers into brand.json

Run these from inside the project. Each call adds to what is already there.

| They gave you | Run |
|---|---|
| Design tokens (JSON), CSS/SCSS variables, a Tailwind config | `python scripts/brand.py --import tokens.json` |
| A brand manual PDF | read it yourself, then `--accent`, `--accent2`, `--bg`, `--text`, `--font` with what it says |
| A website to match | read its CSS, save the variables to a file, `--import` it |
| A logo | `--logo path/to/logo.svg --logo-placement corner\|end\|both\|none` |
| Colors | `--accent "#0B5FFF" --accent2 "#FF7A00" --bg "#FFFFFF" --text "#0F1B2D"` |
| A font name | `--font "Montserrat"` (headings and body) · `--body-font "Inter"` |
| The brand's own font file | `--font path/to/BrandSans-Bold.woff2` |
| A feel | `--style clean` (or bold, editorial, playful, corporate) |
| A caption preference | `--captions stroke\|box\|pill` |
| A reference video they like | study it with the **reference-research** skill, then map what you see onto the above |
| Nothing at all | choose a style for the audience and platform, then show `--compare` |

`--import` prints every color it found and which one it picked for each role.
**Read that list.** Token names vary between companies, and a wrong guess (the
error red picked as the primary) is one `--accent` away from fixed.

Other settings: `--motion calm|snappy|bouncy`, `--transition cut|depth`,
`--background gradient|solid`, `--radius 0` for square corners,
`--uppercase yes` for uppercase headlines, `--reset` to drop all overrides.

## Show, then confirm

```bash
python scripts/brand.py --compare
```

Renders the person's own first scene in every style next to their current
brand.json, into `preview/styles.jpg`. **Send them that image** and let them
point. People who cannot describe a look recognize the right one immediately.

Then look at single frames of every scene type with the real brand before
writing more — see `design.md`.

## Rules

**Never invent brand colors.** If they have no hex codes, use the style's and
say so in the handover: "colors are the style's defaults until you send the
brand ones."

**Never sample a color from a screenshot or a video frame.** Compression and
color profiles shift it, and the drift shows the moment the video sits next to
the real logo. A brand manual, a design system or a clean logo export only.
`brand.py --logo` prints the colors in a PNG logo as suggestions — use them
only when the person confirms.

**Ask for the right logo file.** Transparent background, and the version made
for the background you are using: a dark logo on a dark style disappears. A JPG
logo shows as a white rectangle.

**Read the report `brand.py` prints.** It flags text that fails 4.5:1 contrast
against the background, accents that vanish, a logo file that is not there.
Fix those before building; a brand color can be right for the website and
still unreadable as 46px type on a phone.

**A brand font that is not on Google Fonts needs the file.** `--font` rejects a
name it cannot load rather than silently falling back to a system font.
Licensing is the person's call: a font file in the project gets rendered into
a published video.
