"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";
import { mockCharacters } from "@/lib/mock-data";
import type { Character } from "@/lib/types";
import OpenClawBadge from "@/components/app/OpenClawBadge";
import { openClawAgents } from "@/lib/openclaw";

const roleColors: Record<Character["role"], string> = {
  protagonist: "bg-[#4F46E5]/20 text-[#818CF8] border border-[#4F46E5]/30",
  antagonist: "bg-red-500/20 text-red-400 border border-red-500/30",
  supporting: "bg-amber-500/20 text-amber-400 border border-amber-500/30",
  background: "bg-[#64748B]/20 text-[#94A3B8] border border-[#64748B]/30",
};

export default function CharactersPage() {
  const [selected, setSelected] = useState<Character | null>(null);

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
            Character <GradientText>DNA Vault</GradientText>
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-text-secondary">
              Manage persistent character identities across episodes.
            </p>
            <OpenClawBadge size="sm" />
          </div>
        </div>
        <Button size="md">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Create Character
          </span>
        </Button>
      </motion.div>

      {/* Character Grid */}
      <motion.div
        variants={staggerContainer}
        className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
      >
        {mockCharacters.map((char) => (
          <motion.div key={char.id} variants={fadeInUp}>
            <Card
              className="cursor-pointer"
            >
              <div className="flex items-start gap-4">
                {/* Avatar */}
                <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-[#4F46E5] to-[#EC4899] flex items-center justify-center shrink-0">
                  <span className="text-white text-xl font-bold">
                    {char.name.charAt(0)}
                  </span>
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <h3 className="text-base font-semibold text-text-primary truncate">
                      {char.name}
                    </h3>
                    <span
                      className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium capitalize ${
                        roleColors[char.role]
                      }`}
                    >
                      {char.role}
                    </span>
                  </div>
                  <p className="text-xs text-text-muted mt-1 line-clamp-2">
                    {char.description}
                  </p>
                </div>
              </div>

              {/* Emotion Profile */}
              <div className="mt-4 space-y-2">
                <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">
                  Emotion Profile
                </p>
                <div className="flex gap-2">
                  {Object.entries(char.emotionProfile).map(([emotion, value]) => (
                    <div key={emotion} className="flex-1">
                      <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
                        <div
                          className="h-full rounded-full bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
                          style={{ width: `${value * 100}%` }}
                        />
                      </div>
                      <p className="text-[9px] text-text-muted mt-0.5 capitalize text-center">
                        {emotion}
                      </p>
                    </div>
                  ))}
                </div>
              </div>

              {/* Meta */}
              <div className="mt-4 flex items-center gap-4 text-xs text-text-muted">
                <span>{char.voiceType}</span>
                <span>{char.memoryEntries} memories</span>
              </div>

              {/* OpenClaw consistency */}
              <div className="mt-3 pt-3 border-t border-void-border flex items-center justify-between">
                <div className="flex items-center gap-1.5">
                  <svg className="w-3 h-3 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                    <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
                  </svg>
                  <span className="text-[10px] text-emerald-400 font-medium">OpenClaw DNA Lock</span>
                </div>
                <div className="flex items-center gap-3 text-[10px]">
                  <span className="text-text-muted">Consistency <span className="text-emerald-400 font-mono">{openClawAgents[0].consistency}%</span></span>
                </div>
              </div>

              {/* Expand Button */}
              <button
                onClick={() => setSelected(selected?.id === char.id ? null : char)}
                className="mt-3 text-xs text-[#818CF8] hover:text-[#4F46E5] transition-colors cursor-pointer"
              >
                {selected?.id === char.id ? "Collapse" : "View Details"}
              </button>

              {/* Expanded Details */}
              <AnimatePresence>
                {selected?.id === char.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="mt-4 pt-4 border-t border-void-border space-y-3">
                      <div>
                        <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">Appearance</p>
                        <p className="text-sm text-text-secondary mt-1">{char.appearance}</p>
                      </div>
                      <div>
                        <p className="text-[10px] text-text-muted uppercase tracking-wider font-semibold">Personality</p>
                        <p className="text-sm text-text-secondary mt-1">{char.personality}</p>
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
