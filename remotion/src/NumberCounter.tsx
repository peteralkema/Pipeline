import { AbsoluteFill, interpolate, useCurrentFrame } from "remotion";
import { z } from "zod";
import { zColor } from "@remotion/zod-types";
import { loadFont } from "@remotion/google-fonts/Inter";

const { fontFamily } = loadFont();

export const numberCounterSchema = z.object({
  endValue: z.number(),
  prefix: z.string(),       // e.g. "$"  (use "" for none)
  suffix: z.string(),       // e.g. "B" or " dead" (use "" for none)
  label: z.string(),        // caption under the number
  accentColor: zColor(),
});

type NumberCounterProps = z.infer<typeof numberCounterSchema>;

export const NumberCounter: React.FC<NumberCounterProps> = ({
  endValue,
  prefix,
  suffix,
  label,
  accentColor,
}) => {
  const frame = useCurrentFrame();

  // THE NEW IDEA: the frame drives the NUMBER, not just a style.
  // Count from 0 -> endValue over frames 10..55, eased so it decelerates
  // into the final value (fast then settling — feels weighty, not linear).
  const current = interpolate(frame, [10, 55], [0, endValue], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: (t) => 1 - Math.pow(1 - t, 3), // ease-out cubic
  });
  const display = Math.round(current).toLocaleString("en-US");

  // Label fades in after the count is basically done.
  const labelOpacity = interpolate(frame, [50, 65], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
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
      <div
        style={{
          color: "#f5f5f5",
          fontSize: 200,
          fontWeight: 800,
          letterSpacing: "-0.03em",
          lineHeight: 1,
          display: "flex",
          alignItems: "baseline",
        }}
      >
        <span style={{ color: accentColor }}>{prefix}</span>
        <span>{display}</span>
        <span style={{ color: accentColor, fontSize: 120, marginLeft: 6 }}>{suffix}</span>
      </div>
      <div
        style={{
          opacity: labelOpacity,
          color: "#9aa0aa",
          fontSize: 40,
          fontWeight: 400,
          marginTop: 30,
          letterSpacing: "0.02em",
        }}
      >
        {label}
      </div>
    </AbsoluteFill>
  );
};
