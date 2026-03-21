"use client";

import { motion } from "framer-motion";
import { fadeInUp, staggerContainer } from "@/lib/animations";
import SectionHeading from "@/components/ui/SectionHeading";
import Card from "@/components/ui/Card";

const DIFFERENTIATORS = [
  {
    icon: "🧠",
    title: "Total Memory Architecture",
    description:
      "Five memory pillars — Character DNA Vault, World Atlas, Style Genome, Story Graph, and Production State — ensure every frame knows what came before. Characters age, get scars, change outfits — all tracked automatically across episodes and seasons.",
    highlight: "Characters remember their past. Across episodes.",
  },
  {
    icon: "🤖",
    title: "Agentic Episode Pipeline",
    description:
      "Six autonomous AI agents cascade: Script Writer → Storyboard → Animator → Voice → Music → Editor. Submit a brief, receive a complete episode. No human loop required.",
    highlight: "One brief → full episode. No manual steps.",
  },
  {
    icon: "🎨",
    title: "Anime-Native Engine",
    description:
      "Not a filter on photorealism. Built for anime from the ground up: Illustrious-SDXL, cel-shading pipelines, manga panel layouts, JJK/Chainsaw Man/Frieren aesthetic presets with chiaroscuro lighting.",
    highlight: "Built for anime creators, not adapted from live-action.",
  },
];

export default function Differentiators() {
  return (
    <section className="relative z-10 py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionHeading
          title="What Makes SYNTHOS Different"
          subtitle="Three core innovations that no competitor offers."
        />

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="grid md:grid-cols-3 gap-6"
        >
          {DIFFERENTIATORS.map((item) => (
            <Card key={item.title} className="flex flex-col">
              <div className="text-4xl mb-4">{item.icon}</div>
              <h3 className="text-xl font-bold mb-2">{item.title}</h3>
              <p className="text-sm text-indigo-light font-mono mb-3">
                {item.highlight}
              </p>
              <p className="text-text-secondary text-sm flex-1">
                {item.description}
              </p>
            </Card>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
