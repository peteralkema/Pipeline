import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { z } from "zod";
import { zColor } from "@remotion/zod-types";
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont();

export const quoteCardSchema = z.object({
  quote: z.string(),
  attribution: z.string(),   // e.g. "Mira Murati, former CTO, OpenAI"
  accentColor: zColor(),
});

type QuoteCardProps = z.infer<typeof quoteCardSchema>;

export const QuoteCard: React.FC<QuoteCardProps> = ({
  quote,
  attribution,
  accentColor,
}) => {
  const frame = useCurrentFrame();

  // Oversized quote mark scales + fades in first.
  const markOpacity = interpolate(frame, [0, 12], [0, 0.25], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  const markScale = interpolate(frame, [0, 16], [0.8, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });

  // Quote body rises + fades (starts after the mark).
  const quoteY = interpolate(frame, [10, 30], [30, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });
  const quoteOpacity = interpolate(frame, [10, 28], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Attribution arrives last, quietest. An accent dash draws in before it.
  const dashWidth = interpolate(frame, [34, 48], [0, 56], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });
  const attrOpacity = interpolate(frame, [40, 54], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0f",
        justifyContent: "center",
        alignItems: "flex-start",
        fontFamily,
        flexDirection: "column",
        padding: "0 200px",
      }}
    >
      {/* oversized decorative quotation mark */}
      <div
        style={{
          position: "absolute",
          top: 180,
          left: 150,
          fontSize: 360,
          lineHeight: 1,
          fontWeight: 800,
          color: accentColor,
          opacity: markOpacity,
          transform: `scale(${markScale})`,
          transformOrigin: "top left",
        }}
      >
        &ldquo;
      </div>

      {/* the quote itself */}
      <div
        style={{
          opacity: quoteOpacity,
          transform: `translateY(${quoteY}px)`,
          color: "#f5f5f5",
          fontSize: 76,
          fontWeight: 700,
          lineHeight: 1.3,
          letterSpacing: "-0.015em",
          maxWidth: 1300,
          zIndex: 1,
        }}
      >
        {quote}
      </div>

      {/* attribution: dash + name */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: 20,
          marginTop: 50,
          opacity: attrOpacity,
        }}
      >
        <div style={{ width: dashWidth, height: 3, backgroundColor: accentColor }} />
        <div
          style={{
            color: "#9aa0aa",
            fontSize: 38,
            fontWeight: 400,
            letterSpacing: "0.02em",
          }}
        >
          {attribution}
        </div>
      </div>
    </AbsoluteFill>
  );
};
