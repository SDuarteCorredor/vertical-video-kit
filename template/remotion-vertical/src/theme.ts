/**
 * Design system. You should not need to edit this file.
 *
 * The look comes from src/brand.json: a "style" to start from (styles.ts),
 * plus whatever the brand has already decided — colors, fonts, logo. Change
 * that file, or run scripts/brand.py, and the whole video follows.
 *
 * Take colors from a brand kit or a clean logo export, never from a video
 * frame or a screenshot: compression shifts them, and the drift is visible
 * once the color sits next to the real one.
 */
import {
  cancelRender,
  continueRender,
  delayRender,
  getInputProps,
  staticFile,
} from "remotion";
import brandFile from "./brand.json";
import { GOOGLE_FONTS } from "./fonts.generated";
import { STYLES, type CaptionStyle, type Motion, type Style, type StyleName } from "./styles";

type Brand = {
  style?: string;
  colors?: Partial<Record<"bg" | "text" | "accent" | "accent2" | "captionActive", string>>;
  fonts?: {
    heading?: string;
    body?: string;
    headingWeight?: number;
    bodyWeight?: number;
    uppercaseHeadings?: boolean;
  };
  radius?: number;
  captions?: CaptionStyle;
  motion?: Motion;
  background?: "gradient" | "solid";
  transition?: "cut" | "depth";
  logo?: string | null;
  logoPlacement?: "corner" | "end" | "both" | "none";
};

const brand = brandFile as Brand;

function pick<T>(value: T | null | undefined, fallback: T): T {
  return value === undefined || value === null || value === "" ? fallback : value;
}

// `--props '{"style":"clean"}'` overrides the style for one render, which is
// how scripts/brand.py --compare shows the same video in every style.
const override = (getInputProps() as { style?: string }).style;
const styleName = (override ?? brand.style ?? "bold") as StyleName;
const base: Style = STYLES[styleName] ?? STYLES.bold;
// A style preview shows the style itself, not the brand painted over it.
const own = override ? ({} as Brand) : brand;

// --------------------------------------------------------------------------
// color

const rgb = (hex: string): [number, number, number] => {
  const h = hex.replace("#", "");
  const full = h.length === 3 ? h.split("").map((c) => c + c).join("") : h;
  const n = parseInt(full.slice(0, 6), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
};

const hex = ([r, g, b]: number[]) =>
  "#" + [r, g, b].map((v) => Math.round(v).toString(16).padStart(2, "0")).join("");

/** `a` moved toward `b` by `t` (0..1). */
const mix = (a: string, b: string, t: number) => {
  const x = rgb(a);
  const y = rgb(b);
  return hex(x.map((v, i) => v + (y[i] - v) * t));
};

const luminance = (c: string) => {
  const [r, g, b] = rgb(c).map((v) => {
    const s = v / 255;
    return s <= 0.03928 ? s / 12.92 : ((s + 0.055) / 1.055) ** 2.4;
  });
  return 0.2126 * r + 0.7152 * g + 0.0722 * b;
};

export const contrast = (a: string, b: string) => {
  const [hi, lo] = [luminance(a), luminance(b)].sort((x, y) => y - x);
  return (hi + 0.05) / (lo + 0.05);
};

const rgba = (c: string, alpha: number) => `rgba(${rgb(c).join(", ")}, ${alpha})`;

const bg = pick(own.colors?.bg, base.color.bg);
const text = pick(own.colors?.text, base.color.text);
const accent = pick(own.colors?.accent, base.color.accent);
// A brand that names one color gets it everywhere, not the style's second
// accent next to it.
const accent2 = pick(own.colors?.accent2, own.colors?.accent ? accent : base.color.accent2);
export const IS_DARK = luminance(bg) < 0.35;

export const color = {
  bg,
  bgDeep: IS_DARK ? mix(bg, "#000000", 0.45) : mix(bg, text, 0.05),
  surface: mix(bg, text, IS_DARK ? 0.07 : 0.04),
  surfaceEdge: mix(bg, text, IS_DARK ? 0.16 : 0.12),

  text,
  textMuted: mix(text, bg, 0.36),

  accent,
  accent2,
  /** Whichever of near-white or near-black reads best on the accent. */
  onAccent: contrast("#FFFFFF", accent) >= contrast("#111111", accent) ? "#FFFFFF" : "#111111",

  /** Caption highlight. High contrast on any background, which is the point. */
  captionActive: pick(own.colors?.captionActive, base.color.captionActive ?? accent),
  /** Outline behind stroke captions: dark on dark styles, the page on light. */
  captionStroke: IS_DARK ? mix(bg, "#000000", 0.6) : bg,

  /** Laid over background footage so text stays readable on it. */
  scrimTop: rgba(bg, 0.72),
  scrimMid: rgba(bg, 0.35),
  scrimBottom: rgba(bg, 0.82),

  shadow: "rgba(0, 0, 0, 0.45)",
} as const;

// --------------------------------------------------------------------------
// type

type FontModule = {
  getInfo: () => { fonts: Record<string, Record<string, unknown>>; unicodeRanges: Record<string, string> };
  loadFont: (style: string, options: { weights: string[]; subsets: string[] }) => { fontFamily: string };
};

const nearest = (available: number[], wanted: number) =>
  available.reduce((best, w) => (Math.abs(w - wanted) < Math.abs(best - wanted) ? w : best));

const loaded = new Map<string, string>();

/**
 * "Inter", "DM Sans"... load from Google Fonts (any family the registry in
 * fonts.generated.ts knows — scripts/brand.py adds the brand's).
 * "file:brand/Heading.woff2" loads a font file from public/.
 * Anything else is used as a system font name.
 *
 * Only the weights and subsets actually used are loaded. The unrestricted
 * call fetches well over a hundred files on every render worker, which slows
 * the render down and makes it fail outright on a bad connection.
 */
const loadFamily = (name: string, weights: number[]): string => {
  const key = `${name}|${weights.join(",")}`;
  const done = loaded.get(key);
  if (done) return done;

  let family = name;
  if (name.startsWith("file:")) {
    const file = name.slice(5);
    family = `Brand ${file.replace(/^.*\//, "").replace(/\.\w+$/, "")}`;
    const handle = delayRender(`Loading font ${file}`);
    new FontFace(family, `url('${staticFile(file)}')`)
      .load()
      .then((face) => {
        // lib.dom leaves add() off FontFaceSet; every browser has it.
        (document.fonts as unknown as { add: (f: FontFace) => void }).add(face);
        continueRender(handle);
      })
      .catch((err) => cancelRender(err));
  } else {
    const mod = GOOGLE_FONTS[name] as FontModule | undefined;
    if (mod) {
      const info = mod.getInfo();
      const available = Object.keys(info.fonts.normal ?? {}).map(Number);
      const use = [...new Set(weights.map((w) => nearest(available, w)))];
      const subsets = ["latin", "latin-ext"].filter((s) => s in info.unicodeRanges);
      family = mod.loadFont("normal", { weights: use.map(String), subsets }).fontFamily;
    }
  }
  loaded.set(key, family);
  return family;
};

const headingWeight = pick(own.fonts?.headingWeight, base.font.headingWeight);
const bodyWeight = pick(own.fonts?.bodyWeight, base.font.bodyWeight);
const strong = Math.min(Math.max(headingWeight - 100, 600), 800);
const medium = Math.min(bodyWeight + 100, 600);

const FALLBACK = `"Segoe UI", system-ui, -apple-system, sans-serif`;
const headingFamily = loadFamily(pick(own.fonts?.heading, base.font.heading), [headingWeight, strong]);
const bodyFamily = loadFamily(pick(own.fonts?.body, base.font.body), [bodyWeight, medium]);

export const font = {
  heading: `"${headingFamily}", ${FALLBACK}`,
  family: `"${bodyFamily}", ${FALLBACK}`,
  regular: bodyWeight,
  medium,
  bold: strong,
  black: headingWeight,
  uppercaseHeadings: pick(own.fonts?.uppercaseHeadings, base.font.uppercaseHeadings),
} as const;

/** Type scale in px, sized for a 1080x1920 canvas viewed on a phone. */
export const scale = {
  hook: 108,
  title: 82,
  body: 46,
  label: 32,
  stat: 200,
  caption: 64,
} as const;

export const space = {
  margin: 72,
  gap: 28,
  pad: 40,
  radius: pick(own.radius, base.radius),
} as const;

// --------------------------------------------------------------------------
// behaviour

export const CAPTIONS: CaptionStyle = pick(own.captions, base.caption);
export const BACKGROUND: "gradient" | "solid" = pick(own.background, base.background);

/** Spring settings for every entrance. */
export const MOTION = {
  snappy: { damping: 200, mass: 0.5, shift: 48 },
  calm: { damping: 200, mass: 1.1, shift: 28 },
  bouncy: { damping: 11, mass: 0.6, shift: 64 },
}[pick(own.motion, base.motion)];

export const LOGO = {
  /** A file in public/, e.g. "brand/logo.svg". */
  src: own.logo || null,
  placement: own.logo ? pick(own.logoPlacement, "corner") : "none",
  /** Height of the corner logo. It sits just below the platform's top UI. */
  cornerHeight: 72,
  endHeight: 180,
} as const;

export const STYLE_NAME = styleName;

/**
 * Space the platform UI covers. Keep anything that must be read outside of it.
 *
 * Bottom is the expensive one: TikTok stacks the username, the description and
 * the music ticker there, and Reels puts its own caption in roughly the same
 * band. Text that lands inside it is not "a bit tight" — it is unreadable for
 * most of the audience.
 */
export const safe = {
  top: 140,
  bottom: 380,
  right: 160,
  left: 40,
} as const;

/**
 * The band the captions own. Scenes are padded out of it, so a long line of
 * caption text can never land on top of a scene's own text — the two are
 * generated by different scripts and you would only find the collision by
 * watching the finished render.
 */
export const captionBand = 180;

/** Where the karaoke captions sit — just above the platform UI. */
export const captionBaseline = 1920 - safe.bottom - captionBand + 60;

/** Turn on in Remotion Studio to see the platform-UI overlay. Never render with it on. */
export const SHOW_SAFE_AREAS = false;

/**
 * How one scene hands over to the next, from the style or brand.json.
 * "cut"   — a 4-frame edge; right for most short-form.
 * "depth" — a quick change of focus (recede + blur, arrive from close). Suits
 *           corporate and product pieces, where hard cuts can feel abrupt.
 */
export const TRANSITION: "cut" | "depth" = pick(own.transition, base.transition);
