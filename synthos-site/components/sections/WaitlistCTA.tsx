"use client";

import { motion } from "framer-motion";
import { fadeInUp, staggerContainer } from "@/lib/animations";
import GradientText from "@/components/ui/GradientText";
import WaitlistForm from "@/components/WaitlistForm";

export default function WaitlistCTA() {
  return (
    <section id="waitlist-cta" className="relative z-10 py-32 px-6">
      <motion.div
        variants={staggerContainer}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, margin: "-100px" }}
        className="max-w-3xl mx-auto text-center"
      >
        {/* Glow effect behind */}
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="w-[400px] h-[400px] rounded-full bg-indigo/10 blur-[120px]" />
        </div>

        <motion.h2
          variants={fadeInUp}
          className="relative text-3xl md:text-4xl lg:text-5xl font-bold font-display mb-6"
        >
          Ready to build your <GradientText>AI studio</GradientText>?
        </motion.h2>

        <motion.p
          variants={fadeInUp}
          className="relative text-text-secondary text-lg mb-10 max-w-xl mx-auto"
        >
          Join the waitlist for early access. Be among the first to create
          autonomous AI-produced series with total character consistency.
        </motion.p>

        <motion.div variants={fadeInUp} className="relative">
          <WaitlistForm source="bottom-cta" />
        </motion.div>

        <motion.p
          variants={fadeInUp}
          className="relative text-text-muted text-xs mt-6"
        >
          No spam. No credit card. Just early access when we launch.
        </motion.p>
      </motion.div>
    </section>
  );
}
