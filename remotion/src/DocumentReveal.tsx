import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { z } from "zod";
import { zColor } from "@remotion/zod-types";
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont();

export const documentRevealSchema = z.object({
  source: z.string(),       // e.g. "@sama · X · Nov 17, 2023"
  body: z.string(),         // the full text of the artifact
  highlight: z.string(),    // the phrase inside body to box
  accentColor: zColor(),
});

type DocumentRevealProps = z.infer<typeof documentRevealSchema>;

export const DocumentReveal: React.FC<DocumentRevealProps> = ({
  source,
  body,
  highlight,
  accentColor,
}) => {
  const frame = useCurrentFrame();

  // Card slides up + fades in.
  const cardY = interpolate(frame, [0, 18], [40, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });
  const cardOpacity = interpolate(frame, [0, 16], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // The highlight box strokes itself in (dashoffset) after the card settles.
  // perimeter ~ 2*(width+height); we animate strokeDashoffset from full->0.
  const PERIM = 1600;
  const dashOffset = interpolate(frame, [28, 52], [PERIM, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });
  // Faint fill behind the highlighted phrase, fades in as the box closes.
  const fillOpacity = interpolate(frame, [44, 58], [0, 0.16], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Split body around the highlight phrase.
  const idx = body ? body.indexOf(highlight) : -1;
  const before = idx >= 0 ? body.slice(0, idx) : body ?? "";
  const after = idx >= 0 ? body.slice(idx + highlight.length) : "";

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0f",
        justifyContent: "center",
        alignItems: "center",
        fontFamily,
      }}
    >
      <div
        style={{
          opacity: cardOpacity,
          transform: `translateY(${cardY}px)`,
          width: 1200,
          backgroundColor: "#15161c",
          border: "1px solid #2a2c36",
          borderRadius: 20,
          padding: "56px 64px",
          boxShadow: "0 30px 80px rgba(0,0,0,0.5)",
          position: "relative",
        }}
      >
        {/* source line / chrome */}
        <div
          style={{
            color: accentColor,
            fontSize: 30,
            fontWeight: 700,
            letterSpacing: "0.04em",
            marginBottom: 28,
          }}
        >
          {source}
        </div>

        {/* body, with the highlighted phrase wrapped + boxed */}
        <div
          style={{
            color: "#e8e8ec",
            fontSize: 52,
            fontWeight: 500,
            lineHeight: 1.45,
            position: "relative",
          }}
        >
          {before}
          {idx >= 0 && (
            <span style={{ position: "relative", whiteSpace: "nowrap" }}>
              {/* faint fill */}
              <span
                style={{
                  position: "absolute",
                  inset: "-4px -8px",
                  backgroundColor: accentColor,
                  opacity: fillOpacity,
                  borderRadius: 8,
                }}
              />
              {/* the stroking box, drawn with SVG over the phrase */}
              <svg
                style={{ position: "absolute", inset: "-10px -12px", width: "calc(100% + 24px)", height: "calc(100% + 20px)", overflow: "visible" }}
              >
                <rect
                  x="1"
                  y="1"
                  width="98%"
                  height="92%"
                  rx="10"
                  fill="none"
                  stroke={accentColor}
                  strokeWidth="3"
                  strokeDasharray={PERIM}
                  strokeDashoffset={dashOffset}
                />
              </svg>
              <span style={{ position: "relative" }}>{highlight}</span>
            </span>
          )}
          {after}
        </div>
      </div>
    </AbsoluteFill>
  );
};
