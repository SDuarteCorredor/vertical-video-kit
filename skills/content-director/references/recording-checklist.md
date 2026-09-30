# Recording checklist (phone-first)

Adapt to what the person owns (diagnosis round 4). Give it as a short list they
can read on the phone before hitting record.

## Before rolling

- **Mic:** receiver connected to the phone *before* opening the camera. Record
  5 s and listen with headphones. A second take once came back completely
  silent (−91 dB) because the mic never reached the phone. If the mic records
  internally, turn that on as a backup.
- **iPhone HDR off:** Settings → Camera → Record Video → HDR Video. HDR (HLG,
  BT.2020, 10-bit) looks washed out or clipped on Instagram unless it is
  tone-mapped. If footage arrives in HDR anyway, convert with Apple's own
  engine: `avconvert -s in.mov -p Preset3840x2160 -o out.mp4` (macOS), which
  keeps resolution and tone-maps correctly. Plain ffmpeg without zscale cannot.
- **4K 30 fps**, vertical (unless the series is cinematic horizontal).
- **Exposure/focus lock:** press and hold on the face until "AE/AF lock", so
  moving hands don't change the brightness.

## Light and place

- **Face the window** (window behind the phone) or to the side. Never window
  behind the person: face goes dark, sky blows out.
- Soft key (window or LED bounced off a wall) + **a warm practical lamp visible
  in frame**. Optional coloured light on the background.
- Quiet room, door closed, AC/fan off.

## Framing

- Phone on a tripod at eye level or slightly below (essays).
- Mid shot, chest up or seated wider; **head in the middle third** so the title
  overlay (top) and subtitles (bottom) don't cover the face.
- Nothing important in the bottom ~380 px or right ~160 px: the platform UI
  covers it.
- High resolution leaves room for a later digital punch-in (1440×2560 allows
  ~30% crop and still delivers 1080×1920).

## Performing

- **One continuous take, 2–3 full passes. No pauses between blocks**; spoken
  bridges carry the transitions. If you stumble, keep going with the next line.
- Memorise the first and last lines exactly; say the middle in your own words.
- Start mid-energy, no "hola". Give ~20% more energy than feels natural.
- Change pace per block (fast / lower / slower and warmer) instead of stopping.

## Support shots (B-roll)

- 5–8 s each, steady, each tied to a line of the script (the card lists them).
- Screens: no real names or faces of other people.

## Sending the files

Original files by AirDrop / as file — never WhatsApp (it recompresses).
