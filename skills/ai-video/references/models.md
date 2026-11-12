# Models and what they are good at

Snapshot from **November 2026**. The model names, limits and modes below were
read from Higgsfield's live catalog through its connector (`models_list`); the
"good at" notes come from Higgsfield's own posts and creators who compare
models side by side. Models change monthly; check the date before trusting a
row, and re-read the catalog when the connector is available.

## Images (character sheets, start frames, fixes)

| Need | Model | Notes |
|---|---|---|
| All iteration on stills | Seedream 5.0 Lite · Seedream 5.0 Pro | Both unlimited on paid plans: iterate here. Pro edits up to 2K, can remove background, inpaint. |
| Fast edits on a still | Seedream 5.0 Flash · Nano Banana 2 | Instruction edits; Nano Banana 2 takes a mask. |
| Text, logos, diagrams in the image | Nano Banana Pro · GPT Image 2.6 · Ideogram 4.5 | Never for real UI screenshots (see SKILL.md). |
| Realistic people, UGC look | Higgsfield Soul 2.0 | Soul-ID keeps one person consistent. Unlimited. |
| Same character from new angles | 3D Jutsu Angles | Built on Seedream 5.0 Pro. |

## Video

| Need | Model | Limits that matter |
|---|---|---|
| Most cinematic image → video, references | **Seedance 2.5** | 4–30 s · modes `t2v`, `omni_reference`, `video_edit`, `video_extension` · **`draft`: 480p preview, finalize at 1080p within 7 days** — the cheapest way to test a shot. |
| Same, cheaper / unlimited | Seedance 2.0 · Seedance 2.0 Mini | 2.0 is unlimited on plans that include it; 4K needs `std` mode. Mini is 480–720p. |
| Long consistent takes, keyframes | **Kling 4.0** | 3–30 s · start/end frames, up to 7 saved elements, `video-edit`. Kling 4.0 Flash: 720p, cheaper. |
| Multi-shot in one generation | Kling 3.0 Omni · Cinema Studio 3.5 | Up to 6 shots with their own prompts. Kling 3.0 is unlimited. |
| Director controls (lens, light, era, pacing) | Cinema Studio 4.0 | 4–30 s, same four modes as Seedance 2.5. |
| Cheapest, animation styles | Wan 3.0 / Wan 3.0 Prime | 2–30 s, `enable_thinking` for prompt adherence. Wan 2.7 is unlimited. |
| Ultra-realistic close-ups with sound | Veo 3.1 · Veo 3.1 Lite | 4/6/8 s only. Lite for batches. |
| A person talking (lip-sync from a recording) | **Higgsfield Intone** | 1–2 characters, 1–6 voice files, 2–30 s total. Sync Lipsync 3 re-syncs an existing clip. |
| Replace a person or object in real footage | **Genjutsu** (Replace Object) | Lite version runs on Kling 4.0, 720p/1080p. |
| Move a still character like a real clip | Genjutsu (Motion Control) | Lite version runs on Wan 3.0, up to 15 s. Kling 3.0 Motion Control is unlimited. |
| Edit an existing clip with words | FLUX 3 Video Edit · Kling 3.0 Omni Edit · Gemini Omni Flash 1.1 (`edit`) | FLUX bills 1 credit per second, first 15 s only. |
| New hook or CTA on an ad that already exists | Ad Multiplier Recreate (`sections`) | Regenerates only the hook (4–15 s) and/or CTA and stitches it back in. |

## Finishing (after the cut is locked, never before)

| Need | Tool |
|---|---|
| 16:9 → 9:16 with generated edges | Reframe |
| Upscale | Topaz (to 2160p) · Bytedance Video Upscale (preset `ugc`, `aigc`, `old_film`) · Video Upscale |
| Smoother motion | FPS Boost (Bytedance or Topaz) |
| Flicker in AI clips | Video Deflicker |
| Cut the subject out | Video Background Remover · Remove Background (SAM 3) |
| Another language | Dubbing (18 languages, Spanish included) |

## What the connector can and cannot do

The Higgsfield connector reads: workspaces, credit balance and plan, the model
catalog, past generations; and imports a Claude Motion MP4. **It cannot
generate, upload files or buy credits.** The person runs the generations in
their own account; the agent prepares prompts, frames and the plan.

Before planning any generated shot, check `private/` for which projects the
account is meant for: some people keep a paid AI-video account for work only,
not for their personal brand. If the project falls outside it, plan the video
with real footage and the rest of the kit instead, and ask when in doubt.

## Comparing before committing

Run the **same prompt and start frame** through two models on the hardest
shot, at the lowest resolution (or Seedance 2.5 `draft`), and keep the winner
for the whole video. Mixing models shot to shot changes the look between cuts.

## What the creators who do this well share

From 52 Instagram posts (Higgsfield's account and creators with 13K–65K likes
per post), October 2026:

- Flow: reference image → video model → upscale → small fixes in the edit.
- One protagonist, a strong visual in the first second, vertical 9:16.
- The prompt is shared as a fixed template with brackets for the variable parts.
- Swapping the person in a real clip is the technique growing fastest, because
  it keeps real camera work and real physics (liquids, cloth, money in hands).
