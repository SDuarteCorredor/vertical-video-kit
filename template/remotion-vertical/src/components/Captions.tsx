/**
 * Word-by-word captions, the kind every short-form platform trained people to
 * expect. Generated from the narration audio by scripts/captions.py, so they
 * are always in sync with what is actually said — not with what the script
 * said before someone edited it.
 *
 * This is not decoration. Most of the feed is watched muted; a short without
 * captions is a silent film with no title cards.
 */
import React from "react";
import { AbsoluteFill, useCurrentFrame, useVideoConfig } from "remotion";
import captionsFile from "../captions.json";
import { CAPTIONS, captionBaseline, color, contrast, font, scale, space } from "../theme";

type Word = { start: number; end: number; text: string };

const WORDS = captionsFile.words as Word[];

/** Words per line. Two to four reads well; more and the eye has to scan. */
const PER_LINE = 3;
/** A line never stays up longer than this, even if the speaker pauses. */
const MAX_LINE_SECONDS = 1.6;

type Line = { start: number; end: number; words: Word[] };

const buildLines = (words: Word[]): Line[] => {
  const lines: Line[] = [];
  let current: Word[] = [];

  const flush = () => {
    if (current.length === 0) return;
    lines.push({
      start: current[0].start,
      end: current[current.length - 1].end,
      words: current,
    });
    current = [];
  };

  for (const word of words) {
    if (
      current.length >= PER_LINE ||
      (current.length > 0 && word.end - current[0].start > MAX_LINE_SECONDS)
    ) {
      flush();
    }
    current.push(word);
  }
  flush();
  return lines;
};

const LINES = buildLines(WORDS);

/**
 * Three looks, picked by the style or brand.json "captions":
 *   stroke — outlined words, the active one recolored. Survives any footage.
 *   box    — the line sits on a solid block. Calm; reads on light styles.
 *   pill   — the active word gets its own filled pill. Loud; creator style.
 */
const LINE_STYLE: Record<typeof CAPTIONS, React.CSSProperties> = {
  // A stroke, not a drop shadow: captions have to survive landing on a
  // white wall in the background footage.
  stroke: { WebkitTextStroke: `10px ${color.captionStroke}`, paintOrder: "stroke fill" },
  box: {
    backgroundColor: color.text,
    padding: "14px 28px",
    borderRadius: Math.min(space.radius, 24),
  },
  pill: {},
};

/** On a box the words sit on the text color, so the highlight must read there. */
const BOX_ACTIVE = [color.captionActive, color.accent, color.accent2].reduce(
  (best, c) => (contrast(c, color.text) > contrast(best, color.text) * 1.4 ? c : best),
);

const wordStyle = (active: boolean): React.CSSProperties => {
  if (CAPTIONS === "box") {
    return { color: active ? BOX_ACTIVE : color.bg };
  }
  if (CAPTIONS === "pill") {
    return {
      color: active ? color.onAccent : color.text,
      backgroundColor: active ? color.accent : "transparent",
      padding: "4px 18px",
      borderRadius: 999,
      WebkitTextStroke: active ? undefined : `8px ${color.captionStroke}`,
      paintOrder: "stroke fill",
    };
  }
  return { color: active ? color.captionActive : color.text };
};

export const Captions: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;

  const line = LINES.find((l) => t >= l.start && t <= l.end);
  if (!line) return null;

  return (
    <AbsoluteFill
      style={{
        justifyContent: "flex-start",
        alignItems: "center",
        paddingLeft: space.margin,
        paddingRight: space.margin,
      }}
    >
      <div
        style={{
          position: "absolute",
          top: captionBaseline,
          display: "flex",
          flexWrap: "wrap",
          justifyContent: "center",
          alignItems: "center",
          gap: CAPTIONS === "stroke" ? 18 : 12,
          fontFamily: font.heading,
          fontSize: scale.caption,
          fontWeight: font.black,
          lineHeight: 1.15,
          textAlign: "center",
          ...LINE_STYLE[CAPTIONS],
        }}
      >
        {line.words.map((w, i) => {
          const active = t >= w.start && t <= w.end;
          return (
            <span
              key={`${w.start}-${i}`}
              style={{
                display: "inline-block",
                transform: active ? "scale(1.08)" : "scale(1)",
                ...wordStyle(active),
              }}
            >
              {w.text}
            </span>
          );
        })}
      </div>
    </AbsoluteFill>
  );
};
