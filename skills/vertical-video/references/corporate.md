# Corporate video, specifically

A corporate short is not a consumer short with a logo on it. The constraints
are different, the failure modes are different, and the person approving it is
usually not the person who briefed it.

Read this alongside `hooks.md`, `voice.md` and `design.md` — none of it is
replaced here, it is what changes when the video belongs to a company.

## The one that ruins the most videos

**Nothing in the video is yours to invent.** Not a percentage, not a client
name, not a certification, not a launch date, not a claim about what the
product does, not "trusted by hundreds of companies."

A consumer script that guesses a number is sloppy. A corporate script that
guesses one is a statement the company did not approve, published under its
name, in a format that gets screenshotted. Legal, compliance and the sales team
all have a say in numbers, and none of them were in the room.

So: if a detail is missing, ask for it. If nobody answers, write the line
without it. And when you hand the video over, say plainly what is still
unverified — in the message, not buried in a code comment.

```
Pending before this can be published:
- Scene 3 says "under 48 hours". Nobody confirmed that number.
- The client logo in scene 4 needs written permission.
```

## Who is actually watching

Not "our audience." Corporate shorts get watched by three different people and
they want different things:

- **The buyer** — has a problem and thirty seconds. Wants to know if this is
  about their problem. Leaves at the first sentence that isn't.
- **The employee or candidate** — wants to know what it's like to work there.
  Reads tone more than content.
- **The competitor and the industry** — will read anything overclaimed as an
  opening, and screenshot it.

Write for the first one. The other two decide whether what you wrote survives
contact with the internet.

## Corporate words that kill a hook

These don't sound professional. They sound like nobody wanted to say anything
specific:

> leading · innovative · end-to-end solutions · synergy · empowering ·
> best-in-class · seamless · we are passionate about · transforming the way ·
> at the forefront of · robust · holistic · value proposition

> líderes en · soluciones integrales · de la mano de · sinergia · potenciar ·
> vanguardia · transformar la manera en que · aliado estratégico ·
> comprometidos con la excelencia

The test: could a competitor put their logo on this sentence without changing a
word? Then it says nothing. A specific, unglamorous sentence beats a polished
empty one every time — "we ship in 48 hours" beats "committed to operational
excellence."

## The hook, when it has to be corporate-safe

The hook patterns in `hooks.md` still apply. Three that work inside a brand
without overclaiming:

**Name the problem the buyer already has.** "Your onboarding takes three weeks
and nobody can tell you why." Safe because it's about them, not a claim about
you.

**Start mid-process.** Open on the thing happening, explain after. "This is
what happens to an order between the click and the truck."

**A number you actually own.** Your own operational data, verified, in a
sentence that attributes it. Not an industry statistic you found somewhere.

What never works: opening with the company name, the logo animation, or "We
are COMPANY, and we do X." That's a two-second goodbye, and the logo at the
start is the most common reason a corporate short has a 90% drop-off.

Put the brand at the **end**, on the CTA, where someone who watched has a
reason to care who made it.

## Brand, in practice

The entire visual identity is `src/brand.json`, and `scripts/brand.py` writes
it — from a design system, a logo, colors and fonts. If a brand change
requires touching a component, something is in the wrong place. Start with
the **corporate** style and override it; `references/style.md` has the
questions to ask first.

```bash
python scripts/brand.py --style corporate --import design-tokens.json
python scripts/brand.py --logo logo.svg --logo-placement end
python scripts/brand.py --caption-color "#FFE55C"   # keep the highlight loud
```

Two things that go wrong every time:

**Colors sampled from a screenshot or a video frame.** Compression shifts them,
and the drift is obvious next to the real color. Take them from the brand kit
or a clean logo export — a PDF, an SVG, an `.ase` file.

**The brand palette as the caption highlight.** Brand colors are chosen to sit
in a deck, not to pop off a moving video at arm's length. If the primary is a
mid-tone blue, the caption highlight in that blue is unreadable. Keep the
highlight loud and let the brand live in the accents.

Fonts: any Google font works by name (`--font "Montserrat"`), and the brand's
own file works too (`--font BrandSans.woff2`). If the brand font is licensed,
check whether the license covers embedding in video before you use the file —
many desktop licenses don't. A close Google Fonts substitute is a normal and
defensible choice for social video.

## Logos

- **At the end, small, on the CTA.** Not the opening frame.
- **A watermark is fine** — small, in the top-left corner, never in the bottom
  ~380px or the right ~160px where the platform UI lands.
- **SVG or a large clean PNG.** A logo pulled off the website is usually 200px
  wide and falls apart at 1080.
- **Someone else's logo needs written permission.** "They're our client" is not
  permission to put their mark in an ad.

## The approval round

Corporate video has one that consumer video doesn't, and it's where the format
pays off. The whole point of the kit is that a correction is cheap — so invite
corrections instead of defending the first cut.

Hand over three things:

1. The video, and how long it runs.
2. **The narration as plain text**, so it can be read and marked up. Most
   corrections are wording, and nobody wants to describe a wording change by
   timestamp.
3. The list of anything unverified.

When a line comes back changed: edit `script.json`, re-run `voice.py` and
`captions.py`, re-render. The scene re-times itself. That round takes minutes,
which is the argument for building it this way in the first place.

## The brief worth filling in first

Every project scaffolded by `new_project.py` gets a `BRAND.md`. Fill it in once
per company, not per video — then paste it at the start of any AI chat or agent
session and the script comes back sounding like the company instead of like a
press release.

If a video is being made from an existing conversation, a strategy deck or a
messaging doc, `BRAND.md` is where that context belongs. A brief that lives in
a chat window is a brief that gets re-explained every time.

## Platform, for a company account

| | Fits | Watch out |
|---|---|---|
| **LinkedIn** | explainers, hiring, customer stories, announcements | Sound-off rate is highest here. Captions are not optional |
| **Instagram Reels** | culture, product, behind-the-scenes | The band the UI covers is the worst of the three |
| **TikTok** | only if the brand can drop the register entirely | A corporate voice reads as an ad within two seconds |
| **YouTube Shorts** | explainers that can stand without context | Gets searched later, unlike the other three |

One 9:16 master covers all four. What changes is where the text sits, which is
what `SHOW_SAFE_AREAS` in `src/theme.ts` is for.

## Accessibility, which here is also reach

Captions are already generated word by word — that covers most of it. The two
remaining things:

**Contrast.** Brand colors that pass on a white website often fail as text on
a dark video. Check the actual pair, not the brand guideline.

**The audio has to carry the video on its own, and so does the screen.** Someone
listening without watching, and someone watching without sound, should both get
the message. If a scene only works with both, it works for neither.

## Music

Stock music libraries license "for social media" in ways that often exclude
paid promotion. If the video might ever be put behind ad spend, check the
license for that specifically — it is a different tier at most libraries, and
a takedown on a running campaign is expensive.

Trending audio from the platform is licensed for organic use on personal
accounts. Business accounts get a much smaller catalogue, and using the full
one is a policy violation, not a gray area.
