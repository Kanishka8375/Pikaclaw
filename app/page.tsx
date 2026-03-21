import BackgroundEffects from "@/components/BackgroundEffects";
import Hero from "@/components/sections/Hero";
import Problem from "@/components/sections/Problem";
import Differentiators from "@/components/sections/Differentiators";
import Features from "@/components/sections/Features";
import HowItWorks from "@/components/sections/HowItWorks";
import Comparison from "@/components/sections/Comparison";
import Pricing from "@/components/sections/Pricing";
import WaitlistCTA from "@/components/sections/WaitlistCTA";
import Footer from "@/components/sections/Footer";

export default function Home() {
  return (
    <main className="relative overflow-hidden">
      <BackgroundEffects />
      <Hero />
      <Problem />
      <Differentiators />
      <Features />
      <HowItWorks />
      <Comparison />
      <Pricing />
      <WaitlistCTA />
      <Footer />
    </main>
  );
}
