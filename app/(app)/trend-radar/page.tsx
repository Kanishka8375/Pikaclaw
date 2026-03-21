"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";
import { mockTrends } from "@/lib/mock-data";

const platformColors: Record<string, string> = {
  tiktok: "bg-[#EC4899]/20 text-[#F472B6] border border-[#EC4899]/30",
  youtube: "bg-red-500/20 text-red-400 border border-red-500/30",
  douyin: "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30",
  instagram: "bg-violet-500/20 text-violet-400 border border-violet-500/30",
};

type PlatformFilter = "all" | "tiktok" | "youtube" | "douyin" | "instagram";

export default function TrendRadarPage() {
  const [platform, setPlatform] = useState<PlatformFilter>("all");

  const filtered =
    platform === "all"
      ? mockTrends
      : mockTrends.filter((t) => t.platform === platform);

  const sorted = [...filtered].sort((a, b) => b.relevance - a.relevance);

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
            Trend <GradientText>Radar</GradientText>
          </h1>
          <p className="mt-1 text-text-secondary">
            Track viral trends across platforms and generate matching content.
          </p>
        </div>
        <Button variant="secondary" size="md">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Refresh Data
          </span>
        </Button>
      </motion.div>

      {/* Platform Filters */}
      <motion.div variants={fadeInUp} className="flex flex-wrap gap-2">
        {(["all", "tiktok", "youtube", "douyin", "instagram"] as PlatformFilter[]).map(
          (p) => (
            <button
              key={p}
              onClick={() => setPlatform(p)}
              className={`cursor-pointer rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200 capitalize ${
                platform === p
                  ? "bg-gradient-to-r from-[#4F46E5] to-[#EC4899] text-white shadow-lg shadow-[#4F46E5]/20"
                  : "bg-void-light border border-void-border text-text-secondary hover:border-[#4F46E5]/30 hover:text-text-primary"
              }`}
            >
              {p === "all" ? "All Platforms" : p}
            </button>
          )
        )}
      </motion.div>

      {/* Trend Cards */}
      <motion.div variants={staggerContainer} className="space-y-4">
        {sorted.map((trend, idx) => (
          <motion.div
            key={trend.id}
            variants={fadeInUp}
            className="rounded-2xl border border-void-border bg-void-light/50 backdrop-blur-sm p-5 hover:border-[#4F46E5]/20 transition-all duration-300"
          >
            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
              <div className="flex items-start gap-4 flex-1 min-w-0">
                {/* Rank */}
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#4F46E5] to-[#EC4899] flex items-center justify-center shrink-0">
                  <span className="text-white text-xs font-bold">{idx + 1}</span>
                </div>

                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <h3 className="text-sm font-semibold text-text-primary truncate">
                      {trend.title}
                    </h3>
                    <span
                      className={`shrink-0 rounded-full px-2.5 py-0.5 text-[10px] font-medium capitalize ${
                        platformColors[trend.platform]
                      }`}
                    >
                      {trend.platform}
                    </span>
                  </div>
                  <p className="text-xs text-text-muted">{trend.category}</p>
                </div>
              </div>

              {/* Stats */}
              <div className="flex items-center gap-6 text-xs">
                <div className="text-center">
                  <p className="text-text-muted">Growth</p>
                  <p className="text-sm font-bold text-emerald-400">+{trend.growth}%</p>
                </div>
                <div className="text-center">
                  <p className="text-text-muted">Views</p>
                  <p className="text-sm font-bold text-text-primary">{trend.views}</p>
                </div>
                <div className="text-center">
                  <p className="text-text-muted">Relevance</p>
                  <div className="flex items-center gap-1.5 mt-0.5">
                    <div className="w-16 h-2 rounded-full bg-[#1E1E2E] overflow-hidden">
                      <div
                        className="h-full rounded-full bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
                        style={{ width: `${trend.relevance}%` }}
                      />
                    </div>
                    <span className="text-xs font-mono text-text-primary">{trend.relevance}</span>
                  </div>
                </div>
              </div>

              {/* Action */}
              <div className="shrink-0">
                {trend.suggestedTemplate ? (
                  <Button variant="secondary" size="sm">
                    Use Template
                  </Button>
                ) : (
                  <Button variant="secondary" size="sm">
                    Create Content
                  </Button>
                )}
              </div>
            </div>

            {trend.suggestedTemplate && (
              <div className="mt-3 flex items-center gap-2">
                <span className="text-[10px] text-text-muted uppercase tracking-wider">
                  Suggested:
                </span>
                <span className="text-xs text-[#818CF8] font-medium">
                  {trend.suggestedTemplate}
                </span>
              </div>
            )}
          </motion.div>
        ))}
      </motion.div>

      {sorted.length === 0 && (
        <p className="py-12 text-center text-sm text-text-muted">
          No trends found for the selected platform.
        </p>
      )}
    </motion.div>
  );
}
