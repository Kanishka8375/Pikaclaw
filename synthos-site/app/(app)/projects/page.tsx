"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";
import { mockProjects } from "@/lib/mock-data";

const statusColors: Record<string, string> = {
  draft: "bg-[#64748B]/20 text-[#94A3B8] border border-[#64748B]/30",
  in_progress: "bg-[#4F46E5]/20 text-[#818CF8] border border-[#4F46E5]/30",
  rendering: "bg-[#EC4899]/20 text-[#F472B6] border border-[#EC4899]/30",
  completed: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
};

const statusLabels: Record<string, string> = {
  draft: "Draft",
  in_progress: "In Progress",
  rendering: "Rendering",
  completed: "Completed",
};

type Filter = "all" | "draft" | "in_progress" | "rendering" | "completed";

export default function ProjectsPage() {
  const [filter, setFilter] = useState<Filter>("all");
  const [view, setView] = useState<"grid" | "list">("grid");

  const filtered =
    filter === "all"
      ? mockProjects
      : mockProjects.filter((p) => p.status === filter);

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
            <GradientText>Projects</GradientText>
          </h1>
          <p className="mt-1 text-text-secondary">
            Manage your animation series and productions.
          </p>
        </div>
        <Button size="md">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Project
          </span>
        </Button>
      </motion.div>

      {/* Filters + View Toggle */}
      <motion.div
        variants={fadeInUp}
        className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div className="flex flex-wrap gap-2">
          {(["all", "draft", "in_progress", "rendering", "completed"] as Filter[]).map(
            (f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`cursor-pointer rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200 ${
                  filter === f
                    ? "bg-gradient-to-r from-[#4F46E5] to-[#EC4899] text-white shadow-lg shadow-[#4F46E5]/20"
                    : "bg-void-light border border-void-border text-text-secondary hover:border-[#4F46E5]/30 hover:text-text-primary"
                }`}
              >
                {f === "all" ? "All" : statusLabels[f]}
              </button>
            )
          )}
        </div>

        <div className="flex items-center gap-2 rounded-xl border border-void-border bg-void-light p-1">
          <button
            onClick={() => setView("grid")}
            className={`cursor-pointer rounded-lg p-2 transition-all ${
              view === "grid"
                ? "bg-[#4F46E5]/20 text-[#818CF8]"
                : "text-text-muted hover:text-text-secondary"
            }`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <rect x="3" y="3" width="7" height="7" rx="1" />
              <rect x="14" y="3" width="7" height="7" rx="1" />
              <rect x="3" y="14" width="7" height="7" rx="1" />
              <rect x="14" y="14" width="7" height="7" rx="1" />
            </svg>
          </button>
          <button
            onClick={() => setView("list")}
            className={`cursor-pointer rounded-lg p-2 transition-all ${
              view === "list"
                ? "bg-[#4F46E5]/20 text-[#818CF8]"
                : "text-text-muted hover:text-text-secondary"
            }`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
        </div>
      </motion.div>

      {/* Project Grid / List */}
      <AnimatePresence mode="popLayout">
        {view === "grid" ? (
          <motion.div
            key="grid"
            variants={staggerContainer}
            className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
          >
            {filtered.map((project) => (
              <Card key={project.id} className="relative overflow-hidden">
                {/* Thumbnail placeholder */}
                <div className="h-36 -mx-6 -mt-6 mb-4 bg-gradient-to-br from-[#1E1E2E] to-[#2A2A3E] flex items-center justify-center">
                  <svg className="w-12 h-12 text-[#4F46E5]/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
                  </svg>
                </div>

                <div className="flex items-start justify-between">
                  <div className="min-w-0 flex-1">
                    <h3 className="text-base font-semibold text-text-primary truncate">
                      {project.name}
                    </h3>
                    <p className="text-xs text-text-muted mt-1 line-clamp-2">
                      {project.description}
                    </p>
                  </div>
                  <span
                    className={`ml-3 shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColors[project.status]}`}
                  >
                    {statusLabels[project.status]}
                  </span>
                </div>

                <div className="flex items-center gap-4 mt-4 text-xs text-text-muted">
                  <span>{project.genre}</span>
                  <span>{project.style}</span>
                  <span>{project.episodes} ep{project.episodes !== 1 ? "s" : ""}</span>
                </div>
              </Card>
            ))}
          </motion.div>
        ) : (
          <motion.div key="list" variants={staggerContainer} className="space-y-3">
            {filtered.map((project) => (
              <motion.div
                key={project.id}
                variants={fadeInUp}
                className="rounded-2xl border border-void-border bg-void-light/50 backdrop-blur-sm p-5 hover:border-[#4F46E5]/20 transition-all duration-300"
              >
                <div className="flex items-center justify-between">
                  <div className="min-w-0 flex-1">
                    <h3 className="text-sm font-semibold text-text-primary">
                      {project.name}
                    </h3>
                    <p className="text-xs text-text-muted mt-0.5">
                      {project.description}
                    </p>
                  </div>
                  <div className="flex items-center gap-3 ml-4">
                    <span className="text-xs text-text-muted">{project.genre}</span>
                    <span className="text-xs text-text-muted">{project.episodes} eps</span>
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColors[project.status]}`}
                    >
                      {statusLabels[project.status]}
                    </span>
                  </div>
                </div>
              </motion.div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {filtered.length === 0 && (
        <p className="py-12 text-center text-sm text-text-muted">
          No projects match the selected filter.
        </p>
      )}
    </motion.div>
  );
}
