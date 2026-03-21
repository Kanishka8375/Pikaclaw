"use client";

import { motion } from "framer-motion";
import { fadeInUp, staggerContainer } from "@/lib/animations";
import { PRICING_TIERS } from "@/lib/constants";
import SectionHeading from "@/components/ui/SectionHeading";
import Button from "@/components/ui/Button";

export default function Pricing() {
  return (
    <section className="relative z-10 py-24 px-6">
      <div className="max-w-6xl mx-auto">
        <SectionHeading
          title="Simple, Transparent Pricing"
          subtitle="Start free. Scale as you grow. No surprises."
        />

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
          className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {PRICING_TIERS.map((tier) => (
            <motion.div
              key={tier.name}
              variants={fadeInUp}
              className={`rounded-2xl p-6 flex flex-col ${
                tier.highlighted
                  ? "bg-gradient-to-b from-indigo/10 to-pink/5 border-2 border-indigo/40 relative"
                  : "bg-void-light/50 border border-void-border"
              }`}
            >
              {tier.highlighted && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 rounded-full bg-gradient-to-r from-indigo to-pink text-xs font-bold text-white">
                  Most Popular
                </div>
              )}

              <h3 className="text-lg font-bold mb-1">{tier.name}</h3>
              <p className="text-text-muted text-sm mb-4">{tier.description}</p>

              <div className="mb-6">
                <span className="text-3xl font-bold font-mono">
                  {tier.price}
                </span>
                <span className="text-text-muted text-sm">{tier.period}</span>
              </div>

              <ul className="space-y-2 mb-6 flex-1">
                {tier.features.map((feature) => (
                  <li
                    key={feature}
                    className="flex items-start gap-2 text-sm text-text-secondary"
                  >
                    <span className="text-indigo-light mt-0.5">✓</span>
                    <span>{feature}</span>
                  </li>
                ))}
              </ul>

              <Button
                variant={tier.highlighted ? "primary" : "secondary"}
                size="sm"
                className="w-full"
                onClick={() => {
                  document
                    .getElementById("waitlist-cta")
                    ?.scrollIntoView({ behavior: "smooth" });
                }}
              >
                {tier.cta}
              </Button>
            </motion.div>
          ))}
        </motion.div>
      </div>
    </section>
  );
}
