import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { z } from "zod";
import { zColor } from "@remotion/zod-types";
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont();

export const chapterCardSchema = z.object({
  eyebrow: z.string(),   // small line above, e.g. a date or place
  title: z.string(),     // the big chapter title
  accentColor: zColor(),
});

type ChapterCardProps = z.infer<typeof chapterCardSchema>;

// A masked line: the text wipes up from behind a clean edge.
// The outer div clips (overflow hidden); the inner div slides from below.
const MaskedLine: React.FC<{
  children: React.ReactNode;
  delay: number;
  style?: React.CSSProperties;
}> = ({ children, delay, style }) => {
  const frame = useCurrentFrame();
  const y = interpolate(frame, [delay, delay + 16], [110, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });
  return (
    <div style={{ overflow: "hidden", paddingBottom: "0.1em" }}>
      <div style={{ transform: `translateY(${y}%)`, ...style }}>{children}</div>
    </div>
  );
};

export const ChapterCard: React.FC<ChapterCardProps> = ({
  eyebrow,
  title,
  accentColor,
}) => {
  const frame = useCurrentFrame();

  // The accent rule draws across, from 0 to its full width.
  const ruleWidth = interpolate(frame, [4, 24], [0, 420], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3),
  });

  return (
    <AbsoluteFill
      style={{
        backgroundColor: "#0a0a0f",
        justifyContent: "center",
        alignItems: "center",
        fontFamily,
        flexDirection: "column",
      }}
    >
      {/* eyebrow — date/place, masked wipe-up first */}
      <MaskedLine
        delay={0}
        style={{
          color: accentColor,
          fontSize: 38,
          fontWeight: 700,
          letterSpacing: "0.18em",
          textTransform: "uppercase",
        }}
      >
        {eyebrow}
      </MaskedLine>

      {/* the accent rule draws across */}
      <div
        style={{
          width: ruleWidth,
          height: 4,
          backgroundColor: accentColor,
          margin: "34px 0",
          borderRadius: 2,
        }}
      />

      {/* title — masked wipe-up, slightly later */}
      <MaskedLine
        delay={10}
        style={{
          color: "#f5f5f5",
          fontSize: 130,
          fontWeight: 800,
          letterSpacing: "-0.03em",
          lineHeight: 1.05,
          textAlign: "center",
        }}
      >
        {title}
      </MaskedLine>
    </AbsoluteFill>
  );
};
