/**
 * Everything that appears ON SCREEN.
 *
 * What is SAID out loud lives in script.json instead. They are two different
 * texts on purpose: the screen can carry fragments, the voice-over needs whole
 * sentences. Writing one and reusing it for the other is the single most
 * common reason a short sounds robotic.
 *
 * Scene ids must match the ids in script.json — that is how narration,
 * timings and captions find each other.
 */

export type Scene =
  | { id: string; type: "hook"; text: string; kicker?: string; media?: string }
  | { id: string; type: "point"; title: string; body?: string; media?: string }
  | { id: string; type: "list"; title?: string; items: string[]; media?: string }
  | { id: string; type: "stat"; value: string; label: string; media?: string }
  | { id: string; type: "quote"; text: string; author?: string; media?: string }
  | { id: string; type: "cta"; text: string; handle?: string; media?: string };

/**
 * `media` is an optional file in public/media/ (mp4, webm, jpg, png) used as
 * the scene background. Leave it out for a plain gradient background.
 */
export const SCENES: Scene[] = [
  {
    id: "01-hook",
    type: "hook",
    kicker: "60 SECONDS",
    text: "Most vertical videos lose the viewer in the first two seconds",
  },
  {
    id: "02-point",
    type: "point",
    title: "The hook is the whole job",
    body: "If the first sentence does not create a question, nothing after it gets watched.",
  },
  {
    id: "03-list",
    type: "list",
    title: "Three that work",
    items: [
      "Name the mistake out loud",
      "Promise one specific outcome",
      "Start mid-story, explain later",
    ],
  },
  {
    id: "04-stat",
    type: "stat",
    value: "80%",
    label: "of viewers watch with the sound off",
  },
  {
    id: "05-cta",
    type: "cta",
    text: "Build it in code, change it in seconds",
    handle: "vertical-video-kit",
  },
];
