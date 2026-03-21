"use client";

import { motion } from "framer-motion";
import { fadeInUp, staggerContainer } from "@/lib/animations";
import GradientText from "@/components/ui/GradientText";

export default function Problem() {
  return (
    <section className="relative z-10 py-24 px-6">
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        className="max-w-5xl mx-auto"
      >
        <motion.div variants={fadeInUp} className="text-center mb-16">
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold font-display mb-6">
            Every AI video tool is a <span className="text-text-muted line-through">camera</span>.
            <br />
            You need a <GradientText>studio</GradientText>.
          </h2>
        </motion.div>

        <div className="grid md:grid-cols-2 gap-8">
          {/* The Problem */}
          <motion.div
            variants={fadeInUp}
            className="rounded-2xl p-8 bg-red-500/5 border border-red-500/10"
          >
            <h3 className="text-xl font-bold mb-4 text-red-400 font-mono">
              The Camera Problem
            </h3>
            <ul className="space-y-3 text-text-secondary">
              {[
                "Generate one clip at a time — no continuity",
                "Characters look different every generation",
                "No memory between sessions or episodes",
                "Manual work at every single step",
                "Zero anime-native capability",
                "No music, no series planning, no bible",
              ].map((item) => (
                <li key={item} className="flex items-start gap-3">
                  <span className="text-red-400 mt-0.5">✕</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </motion.div>

          {/* The Solution */}
          <motion.div
            variants={fadeInUp}
            className="rounded-2xl p-8 bg-indigo/5 border border-indigo/20"
          >
            <h3 className="text-xl font-bold mb-4 text-indigo-light font-mono">
              The SYNTHOS Studio
            </h3>
            <ul className="space-y-3 text-text-secondary">
              {[
                "One brief → full episode, autonomously",
                "Characters stay perfectly consistent forever",
                "Total Memory Architecture across episodes",
                "Six AI agents handle the entire pipeline",
                "Anime-native from day one",
                "AI music, production bible, series planning",
              ].map((item) => (
                <li key={item} className="flex items-start gap-3">
                  <span className="text-indigo-light mt-0.5">✓</span>
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </motion.div>
        </div>
      </motion.div>
    </section>
  );
}
