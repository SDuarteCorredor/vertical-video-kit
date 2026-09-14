/**
 * The building blocks every scene type is assembled from.
 *
 * If you need something new, add it here rather than styling inline inside a
 * scene — that is how a video ends up with four slightly different title
 * sizes that nobody notices until it is published.
 */
import React from "react";
import { spring, useCurrentFrame, useVideoConfig } from "remotion";
import { color, font, scale, space } from "../theme";

/** Entrance animation. `delay` is in frames; stagger items by 4-6. */
export const Reveal: React.FC<{
  delay?: number;
  shift?: number;
  children: React.ReactNode;
}> = ({ delay = 0, shift = 48, children }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const p = spring({
    frame: frame - delay,
    fps,
    config: { damping: 200, mass: 0.5 },
  });
  return (
    <div style={{ opacity: p, transform: `translateY(${(1 - p) * shift}px)` }}>
      {children}
    </div>
  );
};

export const Kicker: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <div
    style={{
      fontSize: scale.label,
      fontWeight: font.bold,
      letterSpacing: 4,
      textTransform: "uppercase",
      color: color.accent2,
    }}
  >
    {children}
  </div>
);

export const Hook: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      fontSize: scale.hook,
      fontWeight: font.black,
      lineHeight: 1.05,
      letterSpacing: -2,
      textWrap: "balance",
    }}
  >
    {children}
  </div>
);

export const Title: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => (
  <div
    style={{
      fontSize: scale.title,
      fontWeight: font.black,
      lineHeight: 1.1,
      letterSpacing: -1.5,
      textWrap: "balance",
    }}
  >
    {children}
  </div>
);

export const Body: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <div
    style={{
      fontSize: scale.body,
      fontWeight: font.regular,
      lineHeight: 1.35,
      color: color.textMuted,
    }}
  >
    {children}
  </div>
);

export const Bullet: React.FC<{ index: number; children: React.ReactNode }> = ({
  index,
  children,
}) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: space.gap,
      backgroundColor: color.surface,
      border: `2px solid ${color.surfaceEdge}`,
      borderRadius: space.radius,
      padding: space.pad,
    }}
  >
    <div
      style={{
        flexShrink: 0,
        width: 76,
        height: 76,
        borderRadius: 24,
        backgroundColor: color.accent,
        color: color.text,
        fontSize: 42,
        fontWeight: font.black,
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      {index}
    </div>
    <div style={{ fontSize: scale.body, fontWeight: font.medium, lineHeight: 1.25 }}>
      {children}
    </div>
  </div>
);

export const Stat: React.FC<{ value: string; label: string }> = ({
  value,
  label,
}) => (
  <div style={{ textAlign: "center" }}>
    <div
      style={{
        fontSize: scale.stat,
        fontWeight: font.black,
        lineHeight: 1,
        letterSpacing: -6,
        color: color.accent2,
      }}
    >
      {value}
    </div>
    <div
      style={{
        marginTop: space.gap,
        fontSize: scale.body,
        fontWeight: font.medium,
        color: color.text,
        lineHeight: 1.3,
      }}
    >
      {label}
    </div>
  </div>
);
