"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";
import { mockBibleEntries } from "@/lib/mock-data";
import type { BibleEntry } from "@/lib/types";
import OpenClawBadge from "@/components/app/OpenClawBadge";
import { openClawAgents } from "@/lib/openclaw";

type Category = BibleEntry["category"] | "all";

const categoryColors: Record<BibleEntry["category"], string> = {
  character: "bg-[#4F46E5]/20 text-[#818CF8] border border-[#4F46E5]/30",
  location: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
  lore: "bg-violet-500/20 text-violet-400 border border-violet-500/30",
  rules: "bg-amber-500/20 text-amber-400 border border-amber-500/30",
  timeline: "bg-cyan-500/20 text-cyan-400 border border-cyan-500/30",
  palette: "bg-[#EC4899]/20 text-[#F472B6] border border-[#EC4899]/30",
};

const categoryIcons: Record<BibleEntry["category"], React.ReactNode> = {
  character: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <circle cx="12" cy="8" r="4" /><path d="M6 21v-2a4 4 0 014-4h4a4 4 0 014 4v2" />
    </svg>
  ),
  location: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
      <path d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
    </svg>
  ),
  lore: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
    </svg>
  ),
  rules: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
    </svg>
  ),
  timeline: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  palette: (
    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path d="M7 21a4 4 0 01-4-4V5a2 2 0 012-2h4a2 2 0 012 2v12a4 4 0 01-4 4zm0 0h12a2 2 0 002-2v-4a2 2 0 00-2-2h-2.343M11 7.343l1.657-1.657a2 2 0 012.828 0l2.829 2.829a2 2 0 010 2.828l-8.486 8.485M7 17h.01" />
    </svg>
  ),
};

export default function BiblePage() {
  const [activeCategory, setActiveCategory] = useState<Category>("all");
  const [expandedId, setExpandedId] = useState<string | null>(null);

  const filtered =
    activeCategory === "all"
      ? mockBibleEntries
      : mockBibleEntries.filter((e) => e.category === activeCategory);

  const categories: Category[] = [
    "all",
    "character",
    "location",
    "lore",
    "rules",
    "timeline",
    "palette",
  ];

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
            Production <GradientText>Bible</GradientText>
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-text-secondary">
              The canonical source of truth for your series.
            </p>
            <OpenClawBadge size="sm" />
          </div>
        </div>
        <Button size="md">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Entry
          </span>
        </Button>
      </motion.div>

      {/* OpenClaw Bible Keeper */}
      <motion.div variants={fadeInUp}>
        <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
            </svg>
            <div>
              <p className="text-sm font-medium text-emerald-400">OpenClaw Bible Keeper Agent</p>
              <p className="text-[10px] text-text-muted">Auto-generates &amp; enforces series canon &middot; cross-episode consistency</p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="text-text-muted">Accuracy <span className="text-emerald-400 font-mono font-bold">{openClawAgents.find(a => a.name === "Bible Keeper")?.accuracy}%</span></span>
            <span className="text-text-muted">Consistency <span className="text-[#818CF8] font-mono font-bold">{openClawAgents.find(a => a.name === "Bible Keeper")?.consistency}%</span></span>
          </div>
        </div>
      </motion.div>

      {/* Category Filters */}
      <motion.div variants={fadeInUp} className="flex flex-wrap gap-2">
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`cursor-pointer rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200 capitalize ${
              activeCategory === cat
                ? "bg-gradient-to-r from-[#4F46E5] to-[#EC4899] text-white shadow-lg shadow-[#4F46E5]/20"
                : "bg-void-light border border-void-border text-text-secondary hover:border-[#4F46E5]/30 hover:text-text-primary"
            }`}
          >
            {cat}
          </button>
        ))}
      </motion.div>

      {/* Entries */}
      <motion.div variants={staggerContainer} className="space-y-4">
        {filtered.map((entry) => (
          <motion.div key={entry.id} variants={fadeInUp}>
            <Card hover={false} className="!p-0 overflow-hidden">
              <button
                onClick={() =>
                  setExpandedId(expandedId === entry.id ? null : entry.id)
                }
                className="w-full text-left px-6 py-5 cursor-pointer hover:bg-void-lighter/30 transition-colors"
              >
                <div className="flex items-start gap-4">
                  <div
                    className={`flex h-9 w-9 items-center justify-center rounded-lg shrink-0 ${
                      categoryColors[entry.category]
                    }`}
                  >
                    {categoryIcons[entry.category]}
                  </div>
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="text-sm font-semibold text-text-primary truncate">
                        {entry.title}
                      </h3>
                      {entry.autoGenerated && (
                        <span className="shrink-0 rounded-full bg-[#EC4899]/10 border border-[#EC4899]/20 px-2 py-0.5 text-[9px] font-medium text-[#F472B6]">
                          AI
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-text-muted mt-0.5">
                      Updated {new Date(entry.updatedAt).toLocaleDateString()}
                    </p>
                  </div>
                  <span
                    className={`shrink-0 rounded-full px-2.5 py-0.5 text-[10px] font-medium capitalize ${
                      categoryColors[entry.category]
                    }`}
                  >
                    {entry.category}
                  </span>
                </div>
              </button>

              <AnimatePresence>
                {expandedId === entry.id && (
                  <motion.div
                    initial={{ height: 0, opacity: 0 }}
                    animate={{ height: "auto", opacity: 1 }}
                    exit={{ height: 0, opacity: 0 }}
                    transition={{ duration: 0.3 }}
                    className="overflow-hidden"
                  >
                    <div className="px-6 pb-5 pt-0 border-t border-void-border">
                      <p className="text-sm text-text-secondary leading-relaxed mt-4 whitespace-pre-line">
                        {entry.content}
                      </p>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </Card>
          </motion.div>
        ))}
      </motion.div>

      {filtered.length === 0 && (
        <p className="py-12 text-center text-sm text-text-muted">
          No entries match the selected category.
        </p>
      )}
    </motion.div>
  );
}
