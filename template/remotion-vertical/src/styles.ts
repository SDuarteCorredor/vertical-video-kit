/**
 * The looks a video can start from. They are defined in styles.json, which
 * scripts/brand.py reads too; src/brand.json picks one with "style" and
 * overrides whatever the brand already has decided — colors, fonts, logo.
 *
 * A style is a starting point, not a brand. Only the base colors live there;
 * the in-between tones (surfaces, borders, muted text, caption stroke) are
 * derived from them in theme.ts, so a brand that sets just three colors still
 * gets a coherent palette.
 */
import styles from "./styles.json";

export type CaptionStyle = "stroke" | "box" | "pill";
export type Motion = "snappy" | "calm" | "bouncy";

export type Style = {
  label: string;
  /** One line, in words a non-designer would use to choose. */
  looksLike: string;
  color: {
    bg: string;
    text: string;
    accent: string;
    accent2: string;
    /** Caption highlight. Falls back to accent. */
    captionActive?: string;
  };
  font: {
    heading: string;
    body: string;
    headingWeight: number;
    bodyWeight: number;
    uppercaseHeadings: boolean;
  };
  radius: number;
  caption: CaptionStyle;
  motion: Motion;
  background: "gradient" | "solid";
  transition: "cut" | "depth";
};

export const STYLES = styles as Record<keyof typeof styles, Style>;

export type StyleName = keyof typeof styles;
