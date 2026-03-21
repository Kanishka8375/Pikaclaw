"use client";

import { motion } from "framer-motion";
import { fadeInUp, staggerContainer } from "@/lib/animations";
import { SITE } from "@/lib/constants";
import GradientText from "@/components/ui/GradientText";
import WaitlistForm from "@/components/WaitlistForm";

export default function Hero() {
  return (
    <section className="relative z-10 min-h-screen flex items-center justify-center px-6 pt-20 pb-32">
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        animate="visible"
        className="max-w-4xl mx-auto text-center"
      >
        {/* Badge */}
        <motion.div variants={fadeInUp} className="mb-8">
          <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo/10 border border-indigo/20 text-sm text-indigo-light font-mono">
            <span className="w-2 h-2 rounded-full bg-indigo animate-pulse" />
            Coming Soon — Join the Waitlist
          </span>
        </motion.div>

        {/* Headline */}
        <motion.h1
          variants={fadeInUp}
          className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold font-display leading-tight mb-6"
        >
          <GradientText>{SITE.tagline}</GradientText>
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          variants={fadeInUp}
          className="text-lg md:text-xl text-text-secondary max-w-2xl mx-auto mb-4"
        >
          {SITE.description}
        </motion.p>

        {/* Positioning line */}
        <motion.p
          variants={fadeInUp}
          className="text-sm font-mono text-text-muted mb-10"
        >
          {SITE.positioning}
        </motion.p>

        {/* Waitlist form */}
        <motion.div variants={fadeInUp}>
          <WaitlistForm source="hero" />
        </motion.div>

        {/* Stats */}
        <motion.div
          variants={fadeInUp}
          className="mt-16 grid grid-cols-3 gap-8 max-w-lg mx-auto"
        >
          {[
            { value: "12", label: "Unique Features" },
            { value: "6", label: "AI Agents" },
            { value: "5", label: "Memory Pillars" },
          ].map((stat) => (
            <div key={stat.label}>
              <div className="text-2xl md:text-3xl font-bold font-mono text-indigo-light">
                {stat.value}
              </div>
              <div className="text-xs text-text-muted mt-1">{stat.label}</div>
            </div>
          ))}
        </motion.div>
      </motion.div>
    </section>
  );
}
