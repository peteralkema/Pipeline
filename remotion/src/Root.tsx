import { Composition } from "remotion";
import { HelloWorld, myCompSchema } from "./HelloWorld";
import { Logo, myCompSchema2 } from "./HelloWorld/Logo";
import { HighlightedHeadline, highlightedHeadlineSchema } from "./HighlightedHeadline";
import { LowerThird, lowerThirdSchema } from "./LowerThird";
import { NumberCounter, numberCounterSchema } from "./NumberCounter";
import { ChapterCard, chapterCardSchema } from "./ChapterCard";
import { QuoteCard, quoteCardSchema } from "./QuoteCard";
import { DocumentReveal, documentRevealSchema } from "./DocumentReveal";
import { SyntheticSequence } from "./SyntheticSequence";

export const RemotionRoot: React.FC = () => {
  return (
    <>
      <Composition
        id="SyntheticSequence"
        component={SyntheticSequence}
        durationInFrames={210}
        fps={30}
        width={1920}
        height={1080}
      />

      <Composition
        id="HelloWorld"
        component={HelloWorld}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        schema={myCompSchema}
        defaultProps={{
          titleText: "Welcome to Remotion",
          titleColor: "#000000",
          logoColor1: "#91EAE4",
          logoColor2: "#86A8E7",
        }}
      />

      <Composition
        id="OnlyLogo"
        component={Logo}
        durationInFrames={150}
        fps={30}
        width={1920}
        height={1080}
        schema={myCompSchema2}
        defaultProps={{
          logoColor1: "#91dAE2" as const,
          logoColor2: "#86A8E7" as const,
        }}
      />

      <Composition
        id="HighlightedHeadline"
        component={HighlightedHeadline}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        schema={highlightedHeadlineSchema}
        defaultProps={{
          text: "The model learned to deceive its evaluators.",
          highlightPhrase: "deceive its evaluators",
          highlightColor: "#3b5bdb",
          sweepStart: 30,
        }}
      />

      <Composition
        id="LowerThird"
        component={LowerThird}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        schema={lowerThirdSchema}
        defaultProps={{
          primary: "Ilya Sutskever",
          secondary: "Co-founder & Chief Scientist, OpenAI",
          accentColor: "#3b5bdb",
        }}
      />

      <Composition
        id="NumberCounter"
        component={NumberCounter}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        schema={numberCounterSchema}
        defaultProps={{
          endValue: 13000000000,
          prefix: "$",
          suffix: "",
          label: "OpenAI valuation, 2023",
          accentColor: "#3b5bdb",
        }}
      />

      <Composition
        id="ChapterCard"
        component={ChapterCard}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        schema={chapterCardSchema}
        defaultProps={{
          eyebrow: "November 17, 2023",
          title: "The Board Moves",
          accentColor: "#3b5bdb",
        }}
      />

      <Composition
        id="QuoteCard"
        component={QuoteCard}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        schema={quoteCardSchema}
        defaultProps={{
          quote: "Elon's not so bad, as far as dictators go.",
          attribution: "Mira Murati, former CTO, OpenAI",
          accentColor: "#3b5bdb",
        }}
      />

      <Composition
        id="DocumentReveal"
        component={DocumentReveal}
        durationInFrames={120}
        fps={30}
        width={1920}
        height={1080}
        schema={documentRevealSchema}
        defaultProps={{
          source: "@sama · X · Nov 17, 2023",
          body: "i loved my time at openai. it was transformative for me personally, and hopefully the world a little bit.",
          highlight: "transformative",
          accentColor: "#3b5bdb",
        }}
      />
    </>
  );
};
