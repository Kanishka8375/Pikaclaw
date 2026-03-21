"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";

interface LanguageOption {
  code: string;
  name: string;
  flag: string;
  status: "available" | "generating" | "complete";
  progress: number;
  voiceMatch: number;
  lipSync: number;
}

const languages: LanguageOption[] = [
  { code: "ja", name: "Japanese", flag: "JP", status: "complete", progress: 100, voiceMatch: 96, lipSync: 94 },
  { code: "ko", name: "Korean", flag: "KR", status: "complete", progress: 100, voiceMatch: 93, lipSync: 91 },
  { code: "zh", name: "Chinese (Mandarin)", flag: "CN", status: "generating", progress: 67, voiceMatch: 89, lipSync: 85 },
  { code: "es", name: "Spanish", flag: "ES", status: "available", progress: 0, voiceMatch: 0, lipSync: 0 },
  { code: "fr", name: "French", flag: "FR", status: "available", progress: 0, voiceMatch: 0, lipSync: 0 },
  { code: "de", name: "German", flag: "DE", status: "available", progress: 0, voiceMatch: 0, lipSync: 0 },
  { code: "pt", name: "Portuguese", flag: "BR", status: "available", progress: 0, voiceMatch: 0, lipSync: 0 },
  { code: "hi", name: "Hindi", flag: "IN", status: "available", progress: 0, voiceMatch: 0, lipSync: 0 },
];

const statusColors: Record<string, string> = {
  available: "bg-[#64748B]/20 text-[#94A3B8] border border-[#64748B]/30",
  generating: "bg-[#EC4899]/20 text-[#F472B6] border border-[#EC4899]/30 animate-pulse",
  complete: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
};

export default function MultilingualPage() {
  const [selectedProject] = useState("Neon Ronin");
  const [selectedEpisode] = useState("Ep 7: Blade Rain");

  const completed = languages.filter((l) => l.status === "complete").length;
  const generating = languages.filter((l) => l.status === "generating").length;

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
            Multilingual <GradientText>Engine</GradientText>
          </h1>
          <p className="mt-1 text-text-secondary">
            Auto-dub and lip-sync your episodes into any language.
          </p>
        </div>
        <Button size="md">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Start Dubbing
          </span>
        </Button>
      </motion.div>

      {/* Source Selector */}
      <motion.div variants={fadeInUp}>
        <Card>
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm font-medium text-text-primary">Source</p>
              <p className="text-xs text-text-muted mt-0.5">
                {selectedProject} &middot; {selectedEpisode}
              </p>
            </div>
            <div className="flex items-center gap-4 text-xs text-text-muted">
              <span>{completed} languages complete</span>
              <span>{generating} generating</span>
              <span>{languages.length - completed - generating} available</span>
            </div>
          </div>
        </Card>
      </motion.div>

      {/* Stats */}
      <motion.div variants={staggerContainer} className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Languages", value: languages.length, color: "from-[#4F46E5] to-[#818CF8]" },
          { label: "Complete", value: completed, color: "from-emerald-500 to-emerald-400" },
          { label: "Generating", value: generating, color: "from-[#EC4899] to-[#F472B6]" },
          { label: "Avg Voice Match", value: "93%", color: "from-[#4F46E5] to-[#EC4899]" },
        ].map((s) => (
          <Card key={s.label} className="relative overflow-hidden">
            <div className={`pointer-events-none absolute -right-4 -top-4 h-20 w-20 rounded-full bg-gradient-to-br ${s.color} opacity-10 blur-2xl`} />
            <p className="text-xs text-text-muted uppercase tracking-wider">{s.label}</p>
            <p className="mt-1 text-2xl font-bold text-text-primary">{s.value}</p>
          </Card>
        ))}
      </motion.div>

      {/* Language Grid */}
      <motion.div
        variants={staggerContainer}
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3"
      >
        {languages.map((lang) => (
          <Card key={lang.code}>
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-lg bg-void-lighter border border-void-border flex items-center justify-center">
                  <span className="text-xs font-bold text-text-primary">{lang.flag}</span>
                </div>
                <div>
                  <h3 className="text-sm font-semibold text-text-primary">{lang.name}</h3>
                  <span className="text-xs text-text-muted uppercase">{lang.code}</span>
                </div>
              </div>
              <span
                className={`rounded-full px-2.5 py-0.5 text-[10px] font-medium capitalize ${
                  statusColors[lang.status]
                }`}
              >
                {lang.status}
              </span>
            </div>

            {lang.status !== "available" ? (
              <div className="space-y-3">
                {/* Progress */}
                <div>
                  <div className="flex items-center justify-between text-xs text-text-muted mb-1">
                    <span>Progress</span>
                    <span>{lang.progress}%</span>
                  </div>
                  <div className="h-2 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
                    <motion.div
                      className="h-full rounded-full bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
                      initial={{ width: 0 }}
                      animate={{ width: `${lang.progress}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                    />
                  </div>
                </div>

                {/* Quality Metrics */}
                <div className="flex items-center gap-4 text-xs">
                  <div>
                    <span className="text-text-muted">Voice Match</span>
                    <span className="ml-1 font-mono text-text-primary">{lang.voiceMatch}%</span>
                  </div>
                  <div>
                    <span className="text-text-muted">Lip Sync</span>
                    <span className="ml-1 font-mono text-text-primary">{lang.lipSync}%</span>
                  </div>
                </div>
              </div>
            ) : (
              <div className="flex items-center justify-center h-16">
                <Button variant="secondary" size="sm">
                  Generate
                </Button>
              </div>
            )}
          </Card>
        ))}
      </motion.div>
    </motion.div>
  );
}
