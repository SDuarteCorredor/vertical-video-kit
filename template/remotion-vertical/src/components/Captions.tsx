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
import { captionBaseline, color, font, scale, space } from "../theme";

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
          gap: 18,
          fontFamily: font.family,
          fontSize: scale.caption,
          fontWeight: font.black,
          lineHeight: 1.15,
          textAlign: "center",
          // A stroke, not a drop shadow: captions have to survive landing on a
          // white wall in the background footage.
          WebkitTextStroke: `10px ${color.bgDeep}`,
          paintOrder: "stroke fill",
        }}
      >
        {line.words.map((w, i) => {
          const active = t >= w.start && t <= w.end;
          return (
            <span
              key={`${w.start}-${i}`}
              style={{
                color: active ? color.captionActive : color.text,
                transform: active ? "scale(1.08)" : "scale(1)",
                display: "inline-block",
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
