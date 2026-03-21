"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";
import { mockTracks } from "@/lib/mock-data";

const statusColors: Record<string, string> = {
  generating: "bg-[#EC4899]/20 text-[#F472B6] border border-[#EC4899]/30 animate-pulse",
  ready: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
  assigned: "bg-[#4F46E5]/20 text-[#818CF8] border border-[#4F46E5]/30",
};

const moodColors: Record<string, string> = {
  Intense: "text-red-400",
  Melancholy: "text-violet-400",
  Peaceful: "text-sky-400",
  Epic: "text-[#F472B6]",
  Mysterious: "text-emerald-400",
  Romantic: "text-pink-400",
  Comedic: "text-amber-400",
};

export default function SoundtrackPage() {
  const [filter, setFilter] = useState<"all" | "generating" | "ready" | "assigned">("all");

  const filtered = filter === "all" ? mockTracks : mockTracks.filter((t) => t.status === filter);

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
            Soundtrack <GradientText>Forge</GradientText>
          </h1>
          <p className="mt-1 text-text-secondary">
            Generate, preview, and assign AI-composed music to episodes.
          </p>
        </div>
        <Button size="md">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Generate Track
          </span>
        </Button>
      </motion.div>

      {/* Stats */}
      <motion.div variants={staggerContainer} className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Total Tracks", value: mockTracks.length, color: "from-[#4F46E5] to-[#818CF8]" },
          { label: "Generating", value: mockTracks.filter((t) => t.status === "generating").length, color: "from-[#EC4899] to-[#F472B6]" },
          { label: "Ready", value: mockTracks.filter((t) => t.status === "ready").length, color: "from-emerald-500 to-emerald-400" },
          { label: "Assigned", value: mockTracks.filter((t) => t.status === "assigned").length, color: "from-[#4F46E5] to-[#EC4899]" },
        ].map((s) => (
          <Card key={s.label} className="relative overflow-hidden">
            <div className={`pointer-events-none absolute -right-4 -top-4 h-20 w-20 rounded-full bg-gradient-to-br ${s.color} opacity-10 blur-2xl`} />
            <p className="text-xs text-text-muted uppercase tracking-wider">{s.label}</p>
            <p className="mt-1 text-2xl font-bold text-text-primary">{s.value}</p>
          </Card>
        ))}
      </motion.div>

      {/* Filters */}
      <motion.div variants={fadeInUp} className="flex flex-wrap gap-2">
        {(["all", "generating", "ready", "assigned"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`cursor-pointer rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200 capitalize ${
              filter === f
                ? "bg-gradient-to-r from-[#4F46E5] to-[#EC4899] text-white shadow-lg shadow-[#4F46E5]/20"
                : "bg-void-light border border-void-border text-text-secondary hover:border-[#4F46E5]/30 hover:text-text-primary"
            }`}
          >
            {f}
          </button>
        ))}
      </motion.div>

      {/* Track List */}
      <motion.div variants={staggerContainer} className="space-y-3">
        {filtered.map((track) => (
          <motion.div
            key={track.id}
            variants={fadeInUp}
            className="rounded-2xl border border-void-border bg-void-light/50 backdrop-blur-sm p-5 hover:border-[#4F46E5]/20 transition-all duration-300"
          >
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <div className="flex items-center gap-4">
                {/* Play button placeholder */}
                <button className="w-10 h-10 rounded-full bg-[#4F46E5]/20 border border-[#4F46E5]/30 flex items-center justify-center shrink-0 cursor-pointer hover:bg-[#4F46E5]/30 transition-colors">
                  <svg className="w-4 h-4 text-[#818CF8] ml-0.5" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </button>

                <div className="min-w-0">
                  <h3 className="text-sm font-semibold text-text-primary truncate">
                    {track.name}
                  </h3>
                  <div className="flex items-center gap-3 mt-0.5 text-xs text-text-muted">
                    <span className={moodColors[track.mood] || "text-text-muted"}>
                      {track.mood}
                    </span>
                    <span>{track.genre}</span>
                    <span>{track.duration}</span>
                    <span>{track.bpm} BPM</span>
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-3">
                {track.assignedTo && (
                  <span className="text-xs text-text-muted truncate max-w-[200px]">
                    {track.assignedTo}
                  </span>
                )}
                <span
                  className={`rounded-full px-2.5 py-0.5 text-xs font-medium capitalize ${
                    statusColors[track.status]
                  }`}
                >
                  {track.status}
                </span>
              </div>
            </div>

            {/* Waveform placeholder */}
            <div className="mt-3 h-8 rounded-lg bg-[#1E1E2E] overflow-hidden flex items-end gap-px px-1">
              {Array.from({ length: 60 }, (_, i) => (
                <div
                  key={i}
                  className="flex-1 rounded-t-sm bg-gradient-to-t from-[#4F46E5]/40 to-[#EC4899]/40"
                  style={{
                    height: `${20 + Math.sin(i * 0.3 + Number(track.id.split("-")[1])) * 40 + Math.random() * 20}%`,
                  }}
                />
              ))}
            </div>
          </motion.div>
        ))}
      </motion.div>

      {filtered.length === 0 && (
        <p className="py-12 text-center text-sm text-text-muted">
          No tracks match the selected filter.
        </p>
      )}
    </motion.div>
  );
}
