import { AbsoluteFill, Sequence } from "remotion";
import { ChapterCard } from "./ChapterCard";
import { HighlightedHeadline } from "./HighlightedHeadline";
import { NumberCounter } from "./NumberCounter";
import { LowerThird } from "./LowerThird";
import { QuoteCard } from "./QuoteCard";
import { DocumentReveal } from "./DocumentReveal";
import beatsData from "../beats.json";

// REGISTRY: maps the "component" string in beats.json to the real component.
// This is how the pipeline picks a component per beat by name.
const REGISTRY: Record<string, React.FC<any>> = {
  ChapterCard,
  HighlightedHeadline,
  NumberCounter,
  LowerThird,
  QuoteCard,
  DocumentReveal,
};

type Beat = {
  component: string;
  from: number;
  durationInFrames?: number;
  [key: string]: any; // the rest are the component's own props
};

export const SyntheticSequence: React.FC = () => {
  const beats = beatsData.beats as Beat[];

  return (
    <AbsoluteFill style={{ backgroundColor: "#0a0a0f" }}>
      {beats.map((beat, i) => {
        const Comp = REGISTRY[beat.component];
        if (!Comp) {
          // unknown component name in the JSON — skip rather than crash
          return null;
        }
        // pass every field except the orchestration ones as props
        const { component, from, durationInFrames, ...props } = beat;
        return (
          <Sequence
            key={i}
            from={from}
            durationInFrames={durationInFrames ?? 120}
          >
            <Comp {...props} />
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
