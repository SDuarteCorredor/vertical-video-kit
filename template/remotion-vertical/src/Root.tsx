import React from "react";
import { Composition } from "remotion";
import { Short, TOTAL_FRAMES } from "./Video";

/**
 * 1080x1920 at 30fps — what TikTok, Reels and Shorts all accept natively.
 * Rendering at 60fps doubles the render time and the platforms re-encode it
 * back down anyway.
 */
export const RemotionRoot: React.FC = () => (
  <Composition
    id="Short"
    component={Short}
    durationInFrames={TOTAL_FRAMES}
    fps={30}
    width={1080}
    height={1920}
  />
);
