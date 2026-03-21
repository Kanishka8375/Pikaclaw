"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";
import { mockLocations } from "@/lib/mock-data";
import type { Location } from "@/lib/types";

const typeColors: Record<Location["type"], string> = {
  interior: "bg-amber-500/20 text-amber-400 border border-amber-500/30",
  exterior: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
  fantasy: "bg-violet-500/20 text-violet-400 border border-violet-500/30",
  urban: "bg-[#4F46E5]/20 text-[#818CF8] border border-[#4F46E5]/30",
  nature: "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30",
};

const timeIcons: Record<Location["timeOfDay"], string> = {
  dawn: "Dawn",
  day: "Day",
  dusk: "Dusk",
  night: "Night",
};

export default function WorldAtlasPage() {
  const [selected, setSelected] = useState<Location | null>(null);

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Header */}
      <motion.div
        variants={fadeInUp}
        className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-text-primary">
            World <GradientText>Atlas</GradientText>
          </h1>
          <p className="mt-1 text-text-secondary">
            Explore and manage locations across your productions.
          </p>
        </div>
        <Button size="md">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add Location
          </span>
        </Button>
      </motion.div>

      {/* Locations Grid */}
      <motion.div
        variants={staggerContainer}
        className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
      >
        {mockLocations.map((loc) => (
          <motion.div key={loc.id} variants={fadeInUp}>
            <Card className="cursor-pointer" >
              {/* Thumbnail placeholder */}
              <div className="h-32 -mx-6 -mt-6 mb-4 bg-gradient-to-br from-[#1E1E2E] to-[#2A2A3E] flex items-center justify-center relative overflow-hidden">
                <svg className="w-10 h-10 text-[#4F46E5]/20" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <circle cx="12" cy="12" r="9" strokeWidth={1} />
                  <path d="M3.6 9h16.8M3.6 15h16.8" strokeWidth={1} />
                  <ellipse cx="12" cy="12" rx="4" ry="9" strokeWidth={1} />
                </svg>
                {/* Time badge */}
                <span className="absolute top-3 right-3 rounded-full bg-void/80 backdrop-blur-sm border border-void-border px-2.5 py-0.5 text-[10px] font-medium text-text-secondary">
                  {timeIcons[loc.timeOfDay]}
                </span>
              </div>

              <div className="flex items-start justify-between">
                <div className="min-w-0 flex-1">
                  <h3 className="text-base font-semibold text-text-primary truncate">
                    {loc.name}
                  </h3>
                  <p className="text-xs text-text-muted mt-1 line-clamp-2">
                    {loc.description}
                  </p>
                </div>
                <span
                  className={`ml-3 shrink-0 rounded-full px-2.5 py-0.5 text-[10px] font-medium capitalize ${
                    typeColors[loc.type]
                  }`}
                >
                  {loc.type}
                </span>
              </div>

              <div className="mt-4 flex items-center gap-4 text-xs text-text-muted">
                <span>Mood: {loc.mood}</span>
                <span>Eps: {loc.usedInEpisodes.join(", ")}</span>
              </div>

              {/* Expand */}
              <button
                onClick={() => setSelected(selected?.id === loc.id ? null : loc)}
                className="mt-3 text-xs text-[#818CF8] hover:text-[#4F46E5] transition-colors cursor-pointer"
              >
                {selected?.id === loc.id ? "Collapse" : "View Details"}
              </button>

              <AnimatePresence>
                {selected?.id === loc.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="mt-4 pt-4 border-t border-void-border space-y-3">
                      <div>
                        <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">Lighting</p>
                        <p className="text-sm text-text-secondary mt-1">{loc.lighting}</p>
                      </div>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </Card>
          </motion.div>
        ))}
      </motion.div>
    </motion.div>
  );
}
