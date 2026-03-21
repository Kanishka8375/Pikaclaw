"use client";

import { motion } from "framer-motion";
import { fadeInUp, staggerContainer } from "@/lib/animations";
import { FEATURES } from "@/lib/constants";
import SectionHeading from "@/components/ui/SectionHeading";
import Card from "@/components/ui/Card";

export default function Features() {
  return (
    <section className="relative z-10 py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionHeading
          title="12 Features No One Else Has"
          subtitle="Every feature built to solve a real gap in AI video production."
        />

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5"
        >
          {FEATURES.map((feature) => (
            <Card key={feature.title}>
              <div className="text-3xl mb-3">{feature.icon}</div>
              <h3 className="text-base font-bold mb-2">{feature.title}</h3>
              <p className="text-text-secondary text-sm leading-relaxed">
                {feature.description}
              </p>
            </Card>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
