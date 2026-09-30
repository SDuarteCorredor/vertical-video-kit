# Researching Instagram accounts without burning the person's account

## Downloading reels and metadata

`scripts/fetch_refs.py` wraps yt-dlp. Anonymous access works for most public
reels. Notes:

- Strip the `?stkn=` / `?igsh=` tails; the script does it.
- `/p/<id>` posts can be **carousels of several videos** — each slide lands as
  its own file (`<id>_00001.mp4`, `_00002`…). Analyse them as one piece.
- "This content isn't available to everyone" = age/audience restricted. It will
  not download or play in an embedded browser. Say so and ask the person for a
  screen recording. Do not pull cookies from their personal browser to force it.
- `--meta-only` fetches caption, likes, comments and duration without the video
  — use it for scanning dozens of outliers, then download only the ones worth
  breaking down, **after telling the person what and how much**.
- Space requests out (the script sleeps 2 s). Timeouts: retry once with a longer
  socket timeout.

## Finding what overperformed in an account (outliers)

Raw views lie. What matters is a reel's views **against that account's own
median**. A 5K-follower account with a 2.7M reel (×600) teaches more than a 1M
account with a 1.2M reel.

If a browser with the person's Instagram session is available, read the
**reels grid**, which shows view counts, from the page itself:

1. Navigate to `https://www.instagram.com/<account>/reels/`.
2. Wait ~6 s, then do a **real scroll** (mouse wheel). The grid often does not
   render until a human-like scroll happens.
3. Run `scripts/ig_grid.js` in the page. It scrolls a few more times, reads each
   reel's code and view count, and returns the header (followers, bio), the
   median and the top reels as multiples of the median.
4. Pass the codes of the top 3–5 to `fetch_refs.py --meta-only` to learn what
   they are about; download and break down the ones that fit the brand.

**Never call Instagram's private API endpoints** (`/api/v1/...`) in bulk from the
person's session: it returned 429 (rate limit) after a handful of calls, and
automated access on a personal account can get it restricted. Read the page like
a person would, one account at a time, with pauses. Only read — never follow,
like, comment or message.

## Similar accounts

On a profile page, Instagram's "Similar accounts" button (the person-plus icon
next to Message) opens a list of suggested accounts. Clicking it and reading the
links gives 10–15 candidates per profile. Suggestions are noisy: filter by
niche, then scan each candidate's reels grid the same way. Keep only accounts
whose median is healthy and whose outliers fit the brand's topics.

## Without a browser session

Ask the person for the links of the accounts' most-viewed reels, or for
screenshots of their reels grids. For breadth at scale (hundreds of posts),
paid data providers exist (see `reference-research`); suggest them only when the
question is about many accounts.

## What to write down

`contenido/referentes/cuentas.md`: one row per account — handle, followers,
median views, top reels with multiple, what each outlier is about (from its
caption and breakdown), and whether it fits.
