/**
 * Assembles the scenes in order, each with its own narration.
 *
 * Scene length comes from src/timings.json, which scripts/voice.py writes by
 * measuring the audio it just generated. That is the whole trick: you never
 * guess how long a scene should be. Change the script, re-run the script, and
 * every animation re-syncs itself.
 */
import React from "react";
import { AbsoluteFill, Audio, Sequence, staticFile } from "remotion";
import { SCENES } from "./content";
import timings from "./timings.json";
import { Scene } from "./scenes/Scene";
import { Captions } from "./components/Captions";
import { ProgressBar, SafeAreaOverlay, SceneShell } from "./components/Chrome";
import { SHOW_SAFE_AREAS, color } from "./theme";

type Timing = { id: string; audio: number; frames: number };

// The explicit type matters: on a fresh project timings.json holds an empty
// list, which TypeScript infers as never[] and `npm run check` then rejects.
const byId = new Map<string, Timing>(
  (timings.scenes as Timing[]).map((t) => [t.id, t]),
);

/** Used until a scene has real audio, so the studio is usable from minute one. */
const FALLBACK_FRAMES = 90;

/**
 * Background music: drop a file in public/ and put its name here.
 * Keep it quiet — at anything above ~0.1 it competes with the voice, and on
 * phone speakers the voice is what loses.
 */
const MUSIC: string | null = null;

export const TOTAL_FRAMES =
  SCENES.reduce((n, s) => n + (byId.get(s.id)?.frames ?? FALLBACK_FRAMES), 0) ||
  FALLBACK_FRAMES;

export const Short: React.FC = () => {
  let cursor = 0;
  return (
    <AbsoluteFill style={{ backgroundColor: color.bg }}>
      {SCENES.map((scene) => {
        const timing = byId.get(scene.id);
        const duration = timing?.frames ?? FALLBACK_FRAMES;
        const from = cursor;
        cursor += duration;
        return (
          <Sequence
            key={scene.id}
            from={from}
            durationInFrames={duration}
            name={scene.id}
          >
            <SceneShell durationInFrames={duration} media={scene.media}>
              <Scene scene={scene} />
            </SceneShell>
            {timing ? <Audio src={staticFile(`audio/${scene.id}.mp3`)} /> : null}
          </Sequence>
        );
      })}

      {MUSIC ? <Audio src={staticFile(MUSIC)} volume={0.08} loop /> : null}

      {/* Both of these live outside the sequences on purpose: inside one, the
          frame counter restarts at zero for every scene. */}
      <ProgressBar totalFrames={TOTAL_FRAMES} />
      <Captions />

      {SHOW_SAFE_AREAS ? <SafeAreaOverlay /> : null}
    </AbsoluteFill>
  );
};
