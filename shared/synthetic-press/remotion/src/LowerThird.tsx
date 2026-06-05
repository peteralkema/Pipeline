import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { z } from "zod";
import { zColor } from "@remotion/zod-types";
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont();

export const lowerThirdSchema = z.object({
  primary: z.string(),
  secondary: z.string(),
  accentColor: zColor(),
});

type LowerThirdProps = z.infer<typeof lowerThirdSchema>;

export const LowerThird: React.FC<LowerThirdProps> = ({
  primary,
  secondary,
  accentColor,
}) => {
  const frame = useCurrentFrame();

  // Slide in from the left over 18 frames, eased.
  const slideX = interpolate(frame, [6, 24], [-120, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => t * t * (3 - 2 * t),
  });

  // Fade in alongside the slide.
  const opacity = interpolate(frame, [6, 20], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // The accent bar "grows" in height first, then the text rides in.
  const barHeight = interpolate(frame, [0, 14], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => t * t * (3 - 2 * t),
  });

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0f", fontFamily }}>
      {/* Positioned near the lower-left, not centered. */}
      <div
        style={{
          position: "absolute",
          left: 120,
          bottom: 140,
          display: "flex",
          alignItems: "stretch",
          gap: 22,
          opacity,
          transform: `translateX(${slideX}px)`,
        }}
      >
        {/* Accent bar — grows in height */}
        <div
          style={{
            width: 8,
            height: `${barHeight}%`,
            alignSelf: "center",
            minHeight: 10,
            backgroundColor: accentColor,
            borderRadius: 4,
          }}
        />
        {/* Text stack */}
        <div style={{ display: "flex", flexDirection: "column", justifyContent: "center" }}>
          <div
            style={{
              color: "#f5f5f5",
              fontSize: 64,
              fontWeight: 800,
              letterSpacing: "-0.02em",
              lineHeight: 1.05,
            }}
          >
            {primary}
          </div>
          <div
            style={{
              color: "#9aa0aa",
              fontSize: 34,
              fontWeight: 400,
              marginTop: 8,
              letterSpacing: "0.01em",
            }}
          >
            {secondary}
          </div>
        </div>
      </div>
    </AbsoluteFill>
  );
};
