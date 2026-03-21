"use client";

import { motion } from "framer-motion";
import { fadeInUp, staggerContainer } from "@/lib/animations";
import { COMPARISON } from "@/lib/constants";
import SectionHeading from "@/components/ui/SectionHeading";

const competitors = Object.keys(COMPARISON.competitors) as Array<
  keyof typeof COMPARISON.competitors
>;

export default function Comparison() {
  return (
    <section className="relative z-10 py-24 px-6">
      <div className="max-w-5xl mx-auto">
        <SectionHeading
          title="SYNTHOS vs The Rest"
          subtitle="Feature-by-feature comparison with leading AI video tools."
        />

        <motion.div
          variants={staggerContainer}
          initial="hidden"
          whileInView="visible"
          viewport={{ once: true, margin: "-50px" }}
        >
          <motion.div
            variants={fadeInUp}
            className="overflow-x-auto rounded-2xl border border-void-border"
          >
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-void-border bg-void-light/50">
                  <th className="text-left p-4 text-text-muted font-mono font-normal">
                    Feature
                  </th>
                  {competitors.map((name) => (
                    <th
                      key={name}
                      className={`p-4 text-center font-mono font-bold ${
                        name === "SYNTHOS"
                          ? "text-indigo-light bg-indigo/5"
                          : "text-text-secondary"
                      }`}
                    >
                      {name}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {COMPARISON.categories.map((category, i) => (
                  <tr
                    key={category}
                    className={`border-b border-void-border/50 ${
                      i % 2 === 0 ? "bg-void/50" : "bg-void-light/20"
                    }`}
                  >
                    <td className="p-4 text-text-primary">{category}</td>
                    {competitors.map((name) => (
                      <td
                        key={name}
                        className={`p-4 text-center ${
                          name === "SYNTHOS" ? "bg-indigo/5" : ""
                        }`}
                      >
                        {COMPARISON.competitors[name][i] ? (
                          <span className="text-green-400 text-lg">✓</span>
                        ) : (
                          <span className="text-text-muted text-lg">—</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </motion.div>
        </motion.div>
      </div>
    </section>
  );
}
