/**
 * One component per scene type. You declare content in content.ts and the
 * layout comes out of here — that is what makes a text change cost one line
 * instead of an afternoon of nudging boxes around.
 *
 * Only write a new scene type when none of these can carry the idea.
 */
import React from "react";
import type { Scene as SceneData } from "../content";
import { color, font, scale, space } from "../theme";
import { Body, Bullet, Hook, Kicker, Reveal, Stat, Title } from "../components/Pieces";

/**
 * A plain block, not an AbsoluteFill: an absolutely positioned child would
 * fill the padding box and quietly ignore the safe-area padding its parent
 * set — which is how text ends up underneath the platform UI.
 */
const Column: React.FC<{
  justify?: React.CSSProperties["justifyContent"];
  align?: React.CSSProperties["alignItems"];
  children: React.ReactNode;
}> = ({ justify = "center", align = "flex-start", children }) => (
  <div
    style={{
      width: "100%",
      height: "100%",
      display: "flex",
      flexDirection: "column",
      justifyContent: justify,
      alignItems: align,
      gap: space.gap,
    }}
  >
    {children}
  </div>
);

export const Scene: React.FC<{ scene: SceneData }> = ({ scene }) => {
  switch (scene.type) {
    case "hook":
      return (
        <Column justify="center">
          {scene.kicker ? (
            <Reveal>
              <Kicker>{scene.kicker}</Kicker>
            </Reveal>
          ) : null}
          <Reveal delay={4}>
            <Hook>{scene.text}</Hook>
          </Reveal>
        </Column>
      );

    case "point":
      return (
        <Column justify="center">
          <Reveal>
            <Title>{scene.title}</Title>
          </Reveal>
          {scene.body ? (
            <Reveal delay={6}>
              <Body>{scene.body}</Body>
            </Reveal>
          ) : null}
        </Column>
      );

    case "list":
      return (
        <Column justify="center">
          {scene.title ? (
            <Reveal>
              <Title>{scene.title}</Title>
            </Reveal>
          ) : null}
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              gap: space.gap,
              width: "100%",
              marginTop: space.gap,
            }}
          >
            {scene.items.map((item, i) => (
              <Reveal key={item} delay={8 + i * 6}>
                <Bullet index={i + 1}>{item}</Bullet>
              </Reveal>
            ))}
          </div>
        </Column>
      );

    case "stat":
      return (
        <Column justify="center" align="center">
          <Reveal shift={24}>
            <Stat value={scene.value} label={scene.label} />
          </Reveal>
        </Column>
      );

    case "quote":
      return (
        <Column justify="center">
          <Reveal>
            <div
              style={{
                fontSize: scale.title,
                fontWeight: font.bold,
                lineHeight: 1.2,
                fontStyle: "italic",
              }}
            >
              &ldquo;{scene.text}&rdquo;
            </div>
          </Reveal>
          {scene.author ? (
            <Reveal delay={6}>
              <Body>— {scene.author}</Body>
            </Reveal>
          ) : null}
        </Column>
      );

    case "cta":
      return (
        <Column justify="center" align="center">
          <Reveal>
            <div style={{ textAlign: "center" }}>
              <Title>{scene.text}</Title>
            </div>
          </Reveal>
          {scene.handle ? (
            <Reveal delay={6}>
              <div
                style={{
                  fontSize: scale.body,
                  fontWeight: font.bold,
                  color: color.accent2,
                }}
              >
                @{scene.handle}
              </div>
            </Reveal>
          ) : null}
        </Column>
      );
  }
};
