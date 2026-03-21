"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Card from "@/components/ui/Card";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";
import { mockEpisodes } from "@/lib/mock-data";
import type { Episode, AgentStatus } from "@/lib/types";

const agentStatusColors: Record<AgentStatus["status"], string> = {
  waiting: "bg-[#64748B]/20 text-[#94A3B8]",
  active: "bg-[#4F46E5]/20 text-[#818CF8] animate-pulse",
  completed: "bg-emerald-500/20 text-emerald-400",
  error: "bg-red-500/20 text-red-400",
};

const episodeStatusColors: Record<string, string> = {
  draft: "border-[#64748B]/30 text-[#94A3B8]",
  scripting: "border-[#4F46E5]/30 text-[#818CF8]",
  storyboarding: "border-[#4F46E5]/30 text-[#818CF8]",
  animating: "border-[#EC4899]/30 text-[#F472B6]",
  voice: "border-amber-500/30 text-amber-400",
  music: "border-violet-500/30 text-violet-400",
  editing: "border-cyan-500/30 text-cyan-400",
  rendering: "border-[#EC4899]/30 text-[#F472B6]",
  completed: "border-emerald-500/30 text-emerald-400",
};

export default function PipelinePage() {
  const [selectedEpisode, setSelectedEpisode] = useState<Episode | null>(
    mockEpisodes[0]
  );

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={fadeInUp}>
        <h1 className="text-3xl font-bold text-text-primary">
          Episode <GradientText>Pipeline</GradientText>
        </h1>
        <p className="mt-1 text-text-secondary">
          Track agent progress across your production pipeline.
        </p>
      </motion.div>

      {/* Episodes List */}
      <motion.div variants={staggerContainer} className="grid grid-cols-1 gap-4 lg:grid-cols-3">
        {/* Episode Sidebar */}
        <div className="space-y-3 lg:col-span-1">
          <h2 className="text-sm font-semibold text-text-primary tracking-wide uppercase mb-3">
            Episodes
          </h2>
          {mockEpisodes.map((ep) => (
            <motion.button
              key={ep.id}
              variants={fadeInUp}
              onClick={() => setSelectedEpisode(ep)}
              className={`w-full text-left rounded-xl border p-4 transition-all cursor-pointer ${
                selectedEpisode?.id === ep.id
                  ? "border-[#4F46E5]/50 bg-[#4F46E5]/10"
                  : "border-void-border bg-void-light/50 hover:border-[#4F46E5]/20"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-semibold text-text-primary">
                  Ep {ep.number}: {ep.title}
                </span>
                <span
                  className={`rounded-full border px-2 py-0.5 text-[10px] font-medium capitalize ${
                    episodeStatusColors[ep.status]
                  }`}
                >
                  {ep.status}
                </span>
              </div>
              <div className="flex items-center gap-3 text-xs text-text-muted">
                <span>{ep.scenes} scenes</span>
                <span>{ep.duration}</span>
              </div>
              {/* Mini progress */}
              <div className="mt-2 h-1.5 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
                  style={{ width: `${ep.progress}%` }}
                />
              </div>
            </motion.button>
          ))}
        </div>

        {/* Detail Panel */}
        <div className="lg:col-span-2">
          {selectedEpisode ? (
            <Card hover={false} className="!p-0 overflow-hidden">
              {/* Episode Header */}
              <div className="border-b border-void-border px-6 py-5">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-xl font-bold text-text-primary">
                      Episode {selectedEpisode.number}: {selectedEpisode.title}
                    </h2>
                    <p className="text-sm text-text-muted mt-1">
                      {selectedEpisode.brief}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="text-2xl font-bold text-text-primary">
                      {selectedEpisode.progress}%
                    </p>
                    <p className="text-xs text-text-muted">complete</p>
                  </div>
                </div>
                {/* Progress bar */}
                <div className="mt-4 h-3 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
                  <motion.div
                    className="h-full rounded-full bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
                    initial={{ width: 0 }}
                    animate={{ width: `${selectedEpisode.progress}%` }}
                    transition={{ duration: 1, ease: "easeOut" }}
                  />
                </div>
              </div>

              {/* Agent Pipeline */}
              <div className="px-6 py-5 space-y-4">
                <h3 className="text-sm font-semibold text-text-primary tracking-wide uppercase">
                  Agent Pipeline
                </h3>
                {selectedEpisode.agents.map((agent, idx) => (
                  <div
                    key={agent.name}
                    className="flex items-center gap-4"
                  >
                    {/* Step Number */}
                    <div
                      className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-bold shrink-0 ${
                        agent.status === "completed"
                          ? "bg-emerald-500/20 text-emerald-400"
                          : agent.status === "active"
                          ? "bg-[#4F46E5]/20 text-[#818CF8]"
                          : "bg-[#1E1E2E] text-text-muted"
                      }`}
                    >
                      {idx + 1}
                    </div>

                    {/* Agent Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-sm font-medium text-text-primary">
                          {agent.name}
                        </span>
                        <span
                          className={`rounded-full px-2.5 py-0.5 text-[10px] font-medium capitalize ${
                            agentStatusColors[agent.status]
                          }`}
                        >
                          {agent.status}
                        </span>
                      </div>
                      <div className="h-2 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
                        <motion.div
                          className={`h-full rounded-full ${
                            agent.status === "completed"
                              ? "bg-emerald-500/60"
                              : agent.status === "error"
                              ? "bg-red-500/60"
                              : "bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
                          }`}
                          initial={{ width: 0 }}
                          animate={{ width: `${agent.progress}%` }}
                          transition={{ duration: 0.8, ease: "easeOut" }}
                        />
                      </div>
                    </div>

                    {/* Progress % */}
                    <span className="text-xs font-mono text-text-muted w-10 text-right">
                      {agent.progress}%
                    </span>
                  </div>
                ))}
              </div>

              {/* Meta */}
              <div className="border-t border-void-border px-6 py-4 flex items-center gap-6 text-xs text-text-muted">
                <span>{selectedEpisode.scenes} scenes</span>
                <span>{selectedEpisode.duration}</span>
                <span className="capitalize">{selectedEpisode.status}</span>
              </div>
            </Card>
          ) : (
            <div className="flex items-center justify-center h-64 text-text-muted text-sm">
              Select an episode to view its pipeline.
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
