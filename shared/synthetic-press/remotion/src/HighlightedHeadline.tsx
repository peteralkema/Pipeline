import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { z } from "zod";
import { zColor } from "@remotion/zod-types";
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont();

export const highlightedHeadlineSchema = z.object({
  text: z.string(),
  highlightPhrase: z.string(),
  highlightColor: zColor(),
  sweepStart: z.number().optional(), // frame the highlight begins; defaults to 30
});

type HighlightedHeadlineProps = z.infer<typeof highlightedHeadlineSchema>;

export const HighlightedHeadline: React.FC<HighlightedHeadlineProps> = ({
  text,
  highlightPhrase,
  highlightColor,
  sweepStart = 30,
}) => {
  const frame = useCurrentFrame();

  const opacity = interpolate(frame, [0, 15], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  const rise = interpolate(frame, [0, 15], [20, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

  // Sweep now starts at the prop-driven frame (this is the voice-sync hook).
  const sweep = interpolate(frame, [sweepStart, sweepStart + 20], [0, 100], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => t * t * (3 - 2 * t),
  });

  const idx = text ? text.indexOf(highlightPhrase) : -1;
  const before = idx >= 0 ? text.slice(0, idx) : text ?? "";
  const after = idx >= 0 ? text.slice(idx + highlightPhrase.length) : "";

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
          opacity,
          transform: `translateY(${rise}px)`,
          color: "#f5f5f5",
          fontSize: 90,
          fontWeight: 400,
          maxWidth: 1400,
          textAlign: "center",
          lineHeight: 1.4,
          letterSpacing: "-0.02em",
        }}
      >
        {before}
        {idx >= 0 && (
          <span
            style={{
              fontWeight: 800,
              backgroundImage: `linear-gradient(to right, ${highlightColor} ${sweep}%, transparent ${sweep}%)`,
              backgroundSize: "100% 60%",
              backgroundPosition: "0 85%",
              backgroundRepeat: "no-repeat",
              padding: "0 6px",
              boxDecorationBreak: "clone",
            }}
          >
            {highlightPhrase}
          </span>
        )}
        {after}
      </div>
    </AbsoluteFill>
  );
};
