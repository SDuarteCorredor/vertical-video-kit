// Written by scripts/brand.py — do not edit by hand.
// The Google fonts this project can load: the five the styles use, plus any
// the brand asked for. Importing one costs nothing; only the fonts theme.ts
// actually loads are downloaded.
import * as F0 from "@remotion/google-fonts/Inter";
import * as F1 from "@remotion/google-fonts/DMSans";
import * as F2 from "@remotion/google-fonts/PlayfairDisplay";
import * as F3 from "@remotion/google-fonts/Poppins";
import * as F4 from "@remotion/google-fonts/Montserrat";

export const GOOGLE_FONTS: Record<string, unknown> = {
  "Inter": F0,
  "DM Sans": F1,
  "Playfair Display": F2,
  "Poppins": F3,
  "Montserrat": F4,
};
