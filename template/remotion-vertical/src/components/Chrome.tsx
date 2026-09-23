/**
 * Everything that frames a scene: background, legibility scrim, transitions,
 * progress bar, and the platform-UI overlay you check your layout against.
 */
import React from "react";
import {
  AbsoluteFill,
  Easing,
  Img,
  OffthreadVideo,
  interpolate,
  staticFile,
  useCurrentFrame,
} from "remotion";
import { TRANSITION, captionBand, color, font, safe, space } from "../theme";

const isVideo = (file: string) => /\.(mp4|webm|mov|mkv)$/i.test(file);

/**
 * Background media must be at least as long as the scene it sits behind.
 * A clip that runs out mid-scene freezes on its last frame, which reads as a
 * bug to the viewer even though nothing crashed.
 */
const Background: React.FC<{ media?: string }> = ({ media }) => {
  if (!media) {
    return (
      <AbsoluteFill
        style={{
          background: `radial-gradient(120% 70% at 50% 0%, ${color.surface} 0%, ${color.bg} 55%, ${color.bgDeep} 100%)`,
        }}
      />
    );
  }

  const src = staticFile(`media/${media}`);
  return (
    <AbsoluteFill style={{ backgroundColor: color.bgDeep }}>
      {isVideo(media) ? (
        <OffthreadVideo
          src={src}
          muted
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      ) : (
        <Img
          src={src}
          style={{ width: "100%", height: "100%", objectFit: "cover" }}
        />
      )}
      {/* Without this, white text over bright footage is unreadable for a
          third of the shot and nobody can tell you exactly when. */}
      <AbsoluteFill
        style={{
          background: `linear-gradient(180deg, rgba(5,7,11,0.72) 0%, rgba(5,7,11,0.35) 35%, rgba(5,7,11,0.82) 100%)`,
        }}
      />
    </AbsoluteFill>
  );
};

/**
 * Cuts, not crossfades. Short-form is watched at arm's length on a phone —
 * a half-second dissolve reads as lag, not as polish. The only fade here is
 * a 4-frame edge that hides the hard seam between two backgrounds.
 *
 * TRANSITION = "depth" in theme.ts swaps that edge for a short change of
 * focus: the outgoing scene recedes and blurs, the incoming one arrives from
 * slightly too close. No edge travels across the screen, so it reads as the
 * surface settling rather than a slide being pushed. It stays inside each
 * scene's own frames — nothing overlaps, so narration and captions keep
 * their timing.
 */
const depthStyle = (frame: number, duration: number): React.CSSProperties => {
  const IN = 9;
  const OUT = 6;
  const settle = Easing.bezier(0.33, 0, 0.1, 1);
  const enter = interpolate(frame, [0, IN], [0, 1], {
    easing: settle,
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const exit = interpolate(frame, [duration - OUT, duration], [0, 1], {
    easing: Easing.bezier(0.5, 0, 1, 1),
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const blur = (1 - enter) * 7 + exit * 7;
  return {
    opacity: Math.min(interpolate(enter, [0, 0.55, 1], [0, 0.85, 1]), 1 - exit),
    transform: `scale(${(1 + 0.055 * (1 - enter)) * (1 - 0.05 * exit)})`,
    filter: blur > 0.2 ? `blur(${blur}px)` : undefined,
  };
};

export const SceneShell: React.FC<{
  durationInFrames: number;
  media?: string;
  children: React.ReactNode;
}> = ({ durationInFrames, media, children }) => {
  const frame = useCurrentFrame();
  const cut = {
    opacity: interpolate(
      frame,
      [0, 4, durationInFrames - 4, durationInFrames],
      [0, 1, 1, 0],
      { extrapolateLeft: "clamp", extrapolateRight: "clamp" },
    ),
  };
  const style = TRANSITION === "depth" ? depthStyle(frame, durationInFrames) : cut;

  return (
    <AbsoluteFill style={style}>
      <Background media={media} />
      <AbsoluteFill
        style={{
          paddingTop: safe.top,
          paddingBottom: safe.bottom + captionBand,
          paddingLeft: space.margin,
          paddingRight: space.margin,
          fontFamily: font.family,
          color: color.text,
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Sits above every scene so the viewer can see how much is left. */
export const ProgressBar: React.FC<{ totalFrames: number }> = ({
  totalFrames,
}) => {
  const frame = useCurrentFrame();
  const pct = totalFrames > 0 ? Math.min(frame / totalFrames, 1) : 0;
  return (
    <AbsoluteFill style={{ justifyContent: "flex-start" }}>
      <div
        style={{
          height: 8,
          width: `${pct * 100}%`,
          backgroundColor: color.accent,
        }}
      />
    </AbsoluteFill>
  );
};

/**
 * Turn on with SHOW_SAFE_AREAS in theme.ts while you lay a scene out.
 * The red bands are where TikTok and Reels put their own interface.
 */
export const SafeAreaOverlay: React.FC = () => {
  const band: React.CSSProperties = {
    position: "absolute",
    backgroundColor: "rgba(255, 0, 64, 0.22)",
  };
  return (
    <AbsoluteFill>
      <div style={{ ...band, top: 0, left: 0, right: 0, height: safe.top }} />
      <div
        style={{ ...band, bottom: 0, left: 0, right: 0, height: safe.bottom }}
      />
      <div style={{ ...band, top: 0, bottom: 0, right: 0, width: safe.right }} />
      <div
        style={{
          position: "absolute",
          bottom: safe.bottom + 12,
          left: 16,
          fontFamily: font.family,
          fontSize: 28,
          color: "#fff",
        }}
      >
        platform UI — keep text out
      </div>
    </AbsoluteFill>
  );
};
