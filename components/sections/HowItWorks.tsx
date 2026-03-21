"use client";

import { motion } from "framer-motion";
import { fadeInUp, staggerContainer } from "@/lib/animations";
import { HOW_IT_WORKS_STEPS } from "@/lib/constants";
import SectionHeading from "@/components/ui/SectionHeading";

export default function HowItWorks() {
  return (
    <section className="relative z-10 py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <SectionHeading
          title="How It Works"
          subtitle="Three steps. One brief. Full episode."
        />

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-100px" }}
          className="relative"
        >
          {/* Connector line */}
          <div className="hidden md:block absolute top-1/2 left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo/30 to-transparent -translate-y-1/2" />

          <div className="grid md:grid-cols-3 gap-8">
            {HOW_IT_WORKS_STEPS.map((step) => (
              <motion.div
                key={step.step}
                variants={fadeInUp}
                className="relative text-center"
              >
                {/* Step number */}
                <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo/10 border border-indigo/20 mb-6">
                  <span className="text-2xl font-bold font-mono text-indigo-light">
                    {step.step}
                  </span>
                </div>

                <h3 className="text-xl font-bold mb-3">{step.title}</h3>
                <p className="text-text-secondary text-sm leading-relaxed">
                  {step.description}
                </p>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
