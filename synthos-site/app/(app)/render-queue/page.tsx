"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";
import { mockRenderJobs } from "@/lib/mock-data";
import type { RenderJob } from "@/lib/types";
import OpenClawBadge from "@/components/app/OpenClawBadge";
import { openClawAgents } from "@/lib/openclaw";

/* ------------------------------------------------------------------ */
/*  Constants                                                          */
/* ------------------------------------------------------------------ */

type FilterTab = "all" | "queued" | "rendering" | "completed" | "failed";

const filterTabs: { key: FilterTab; label: string }[] = [
  { key: "all", label: "All" },
  { key: "queued", label: "Queued" },
  { key: "rendering", label: "Rendering" },
  { key: "completed", label: "Completed" },
  { key: "failed", label: "Failed" },
];

const resolutionBadge: Record<string, string> = {
  "720p": "bg-[#64748B]/20 text-[#94A3B8] border border-[#64748B]/30",
  "1080p": "bg-[#4F46E5]/20 text-[#818CF8] border border-[#4F46E5]/30",
  "4K": "bg-[#EC4899]/20 text-[#F472B6] border border-[#EC4899]/30",
};

const statusBadge: Record<string, string> = {
  queued: "bg-amber-500/20 text-amber-400 border border-amber-500/30",
  rendering:
    "bg-[#4F46E5]/20 text-[#818CF8] border border-[#4F46E5]/30 animate-pulse",
  completed: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
  failed: "bg-red-500/20 text-red-400 border border-red-500/30",
};

const statusLabel: Record<string, string> = {
  queued: "Queued",
  rendering: "Rendering",
  completed: "Completed",
  failed: "Failed",
};

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function formatTime(dateStr?: string) {
  if (!dateStr) return "—";
  const d = new Date(dateStr);
  return d.toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

/* ------------------------------------------------------------------ */
/*  Page                                                               */
/* ------------------------------------------------------------------ */

export default function RenderQueuePage() {
  const [activeTab, setActiveTab] = useState<FilterTab>("all");
  const [jobs, setJobs] = useState<RenderJob[]>(mockRenderJobs);
  const [cloudLocal, setCloudLocal] = useState<"cloud" | "local">("cloud");

  /* derived stats */
  const totalJobs = jobs.length;
  const renderingNow = jobs.filter((j) => j.status === "rendering").length;
  const completedJobs = jobs.filter((j) => j.status === "completed").length;
  const failedJobs = jobs.filter((j) => j.status === "failed").length;

  const filteredJobs =
    activeTab === "all" ? jobs : jobs.filter((j) => j.status === activeTab);

  /* estimated cost (decorative) */
  const estimatedCost =
    jobs.reduce((acc, j) => {
      if (j.resolution === "4K") return acc + 4.8;
      if (j.resolution === "1080p") return acc + 2.4;
      return acc + 1.2;
    }, 0);

  const gpuUtilization = 67;

  /* ---- action stubs ---- */
  const handleCancel = (id: string) => {
    setJobs((prev) =>
      prev.map((j) =>
        j.id === id ? { ...j, status: "failed" as const, progress: j.progress } : j,
      ),
    );
  };
  const handleRetry = (id: string) => {
    setJobs((prev) =>
      prev.map((j) =>
        j.id === id
          ? { ...j, status: "queued" as const, progress: 0 }
          : j,
      ),
    );
  };
  const handlePriorityUp = (id: string) => {
    setJobs((prev) => {
      const idx = prev.findIndex((j) => j.id === id);
      if (idx <= 0) return prev;
      const next = [...prev];
      [next[idx - 1], next[idx]] = [next[idx], next[idx - 1]];
      return next;
    });
  };
  const handlePriorityDown = (id: string) => {
    setJobs((prev) => {
      const idx = prev.findIndex((j) => j.id === id);
      if (idx < 0 || idx >= prev.length - 1) return prev;
      const next = [...prev];
      [next[idx], next[idx + 1]] = [next[idx + 1], next[idx]];
      return next;
    });
  };

  /* ---- stats cards ---- */
  const statCards = [
    {
      label: "Total Jobs",
      value: totalJobs,
      color: "from-[#4F46E5] to-[#818CF8]",
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
        </svg>
      ),
    },
    {
      label: "Rendering Now",
      value: renderingNow,
      color: "from-[#4F46E5] to-[#EC4899]",
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
        </svg>
      ),
    },
    {
      label: "Completed",
      value: completedJobs,
      color: "from-emerald-500 to-emerald-400",
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
    {
      label: "Failed",
      value: failedJobs,
      color: "from-red-500 to-red-400",
      icon: (
        <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
    },
  ];

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* ---- Header ---- */}
      <motion.div
        variants={fadeInUp}
        className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        <div>
          <h1 className="text-3xl font-bold text-text-primary">
            <GradientText>Render Queue</GradientText>
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-text-secondary">
              Manage and monitor all rendering jobs across your projects.
            </p>
            <OpenClawBadge size="sm" />
          </div>
        </div>
        <Button size="md">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            Add to Queue
          </span>
        </Button>
      </motion.div>

      {/* ---- Stats Bar ---- */}
      <motion.div
        variants={staggerContainer}
        className="grid grid-cols-2 gap-4 lg:grid-cols-4"
      >
        {statCards.map((s) => (
          <Card key={s.label} className="relative overflow-hidden">
            <div className={`pointer-events-none absolute -right-4 -top-4 h-20 w-20 rounded-full bg-gradient-to-br ${s.color} opacity-10 blur-2xl`} />
            <div className="flex items-start justify-between">
              <div>
                <p className="text-xs text-text-muted uppercase tracking-wider">
                  {s.label}
                </p>
                <p className="mt-1 text-2xl font-bold text-text-primary">
                  {s.value}
                </p>
              </div>
              <div className={`flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br ${s.color} text-white`}>
                {s.icon}
              </div>
            </div>
          </Card>
        ))}
      </motion.div>

      {/* ---- GPU Utilization Meter ---- */}
      <motion.div variants={fadeInUp}>
        <Card>
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#4F46E5]/20">
                <svg className="h-5 w-5 text-[#818CF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-text-primary">
                  GPU Cluster Utilization
                </p>
                <p className="text-xs text-text-muted">
                  {renderingNow} active job{renderingNow !== 1 ? "s" : ""} across A100 nodes
                </p>
              </div>
            </div>
            <p className="text-lg font-bold text-text-primary">
              {gpuUtilization}%
            </p>
          </div>
          <div className="h-4 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
              initial={{ width: 0 }}
              animate={{ width: `${gpuUtilization}%` }}
              transition={{ duration: 1.2, ease: "easeOut", delay: 0.3 }}
            />
          </div>
          <div className="mt-2 flex items-center justify-between text-xs text-text-muted">
            <span>0%</span>
            <span>50%</span>
            <span>100%</span>
          </div>
        </Card>
      </motion.div>

      {/* ---- OpenClaw Render Optimizer ---- */}
      <motion.div variants={fadeInUp}>
        <div className="rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
            </svg>
            <div>
              <p className="text-sm font-medium text-emerald-400">OpenClaw Render Optimizer</p>
              <p className="text-[10px] text-text-muted">Intelligent GPU routing &middot; priority scheduling &middot; cost optimization</p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs">
            <span className="text-text-muted">Accuracy <span className="text-emerald-400 font-mono font-bold">{openClawAgents.find(a => a.name === "Render Optimizer")?.accuracy}%</span></span>
            <span className="text-text-muted">Speed <span className="text-[#F472B6] font-mono font-bold">{openClawAgents.find(a => a.name === "Render Optimizer")?.speed}%</span></span>
          </div>
        </div>
      </motion.div>

      {/* ---- Filters + Cloud/Local Toggle ---- */}
      <motion.div
        variants={fadeInUp}
        className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between"
      >
        {/* Filter Tabs */}
        <div className="flex flex-wrap gap-2">
          {filterTabs.map((tab) => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              className={`cursor-pointer rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200 ${
                activeTab === tab.key
                  ? "bg-gradient-to-r from-[#4F46E5] to-[#EC4899] text-white shadow-lg shadow-[#4F46E5]/20"
                  : "bg-void-light border border-void-border text-text-secondary hover:border-[#4F46E5]/30 hover:text-text-primary"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Cloud + Local toggle */}
        <div className="flex items-center gap-2 rounded-xl border border-void-border bg-void-light p-1">
          <button
            onClick={() => setCloudLocal("cloud")}
            className={`cursor-pointer rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200 flex items-center gap-2 ${
              cloudLocal === "cloud"
                ? "bg-[#4F46E5]/20 text-[#818CF8] border border-[#4F46E5]/30"
                : "text-text-muted hover:text-text-secondary"
            }`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 15a4 4 0 004 4h9a5 5 0 10-.1-9.999 5.002 5.002 0 10-9.78 2.096A4.001 4.001 0 003 15z" />
            </svg>
            Cloud
          </button>
          <button
            onClick={() => setCloudLocal("local")}
            className={`cursor-pointer rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200 flex items-center gap-2 ${
              cloudLocal === "local"
                ? "bg-[#EC4899]/20 text-[#F472B6] border border-[#EC4899]/30"
                : "text-text-muted hover:text-text-secondary"
            }`}
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            Local
          </button>
        </div>
      </motion.div>

      {/* ---- Render Jobs List ---- */}
      <motion.div variants={staggerContainer} className="space-y-3">
        <AnimatePresence mode="popLayout">
          {filteredJobs.map((job) => (
            <motion.div
              key={job.id}
              variants={fadeInUp}
              initial="hidden"
              animate="visible"
              exit={{ opacity: 0, y: -10, transition: { duration: 0.2 } }}
              layout
              className="rounded-2xl border border-void-border bg-void-light/50 backdrop-blur-sm p-5 hover:border-[#4F46E5]/20 transition-all duration-300"
            >
              {/* Top row */}
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div className="flex-1 min-w-0 space-y-1">
                  <p className="text-sm font-semibold text-text-primary truncate">
                    {job.episodeName}
                  </p>
                  <div className="flex flex-wrap items-center gap-2">
                    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${resolutionBadge[job.resolution]}`}>
                      {job.resolution}
                    </span>
                    <span className={`inline-flex rounded-full px-2.5 py-0.5 text-xs font-medium ${statusBadge[job.status]}`}>
                      {statusLabel[job.status]}
                    </span>
                  </div>
                </div>

                {/* Meta */}
                <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-xs text-text-muted">
                  <span className="flex items-center gap-1.5">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    ETA: {job.estimatedTime}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                    </svg>
                    {job.gpu}
                  </span>
                  <span className="flex items-center gap-1.5">
                    <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    {formatTime(job.startedAt)}
                  </span>
                </div>

                {/* Actions */}
                <div className="flex items-center gap-1.5 shrink-0">
                  {(job.status === "queued" || job.status === "rendering") && (
                    <button
                      onClick={() => handleCancel(job.id)}
                      className="cursor-pointer rounded-lg p-2 text-text-muted hover:bg-red-500/10 hover:text-red-400 transition-colors"
                      title="Cancel"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  )}
                  {job.status === "failed" && (
                    <button
                      onClick={() => handleRetry(job.id)}
                      className="cursor-pointer rounded-lg p-2 text-text-muted hover:bg-amber-500/10 hover:text-amber-400 transition-colors"
                      title="Retry"
                    >
                      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                      </svg>
                    </button>
                  )}
                  <button
                    onClick={() => handlePriorityUp(job.id)}
                    className="cursor-pointer rounded-lg p-2 text-text-muted hover:bg-[#4F46E5]/10 hover:text-[#818CF8] transition-colors"
                    title="Priority Up"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handlePriorityDown(job.id)}
                    className="cursor-pointer rounded-lg p-2 text-text-muted hover:bg-[#4F46E5]/10 hover:text-[#818CF8] transition-colors"
                    title="Priority Down"
                  >
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </div>
              </div>

              {/* Progress bar */}
              {(job.status === "rendering" || job.status === "queued") && (
                <div className="mt-4">
                  <div className="flex items-center justify-between text-xs text-text-muted mb-1.5">
                    <span>Progress</span>
                    <span>{job.progress}%</span>
                  </div>
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
                    <motion.div
                      className="h-full rounded-full bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
                      initial={{ width: 0 }}
                      animate={{ width: `${job.progress}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                    />
                  </div>
                </div>
              )}
              {job.status === "completed" && (
                <div className="mt-4">
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
                    <div className="h-full w-full rounded-full bg-emerald-500/60" />
                  </div>
                </div>
              )}
              {job.status === "failed" && (
                <div className="mt-4">
                  <div className="flex items-center justify-between text-xs text-text-muted mb-1.5">
                    <span>Failed at {job.progress}%</span>
                  </div>
                  <div className="h-2.5 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
                    <div
                      className="h-full rounded-full bg-red-500/60"
                      style={{ width: `${job.progress}%` }}
                    />
                  </div>
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>

        {filteredJobs.length === 0 && (
          <motion.p
            variants={fadeInUp}
            className="py-12 text-center text-sm text-text-muted"
          >
            No jobs match the selected filter.
          </motion.p>
        )}
      </motion.div>

      {/* ---- Cost Optimization Panel ---- */}
      <motion.div variants={fadeInUp}>
        <Card className="relative overflow-hidden">
          <div className="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full bg-gradient-to-br from-[#4F46E5] to-[#EC4899] opacity-10 blur-3xl" />
          <div className="flex flex-col gap-6 md:flex-row md:items-start md:justify-between">
            <div>
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#EC4899]/20">
                  <svg className="h-5 w-5 text-[#F472B6]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <p className="text-sm font-semibold text-text-primary">
                    Cost Optimization
                  </p>
                  <p className="text-xs text-text-muted">
                    Estimated rendering costs for current queue
                  </p>
                </div>
              </div>
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                <div>
                  <p className="text-xs text-text-muted">4K Jobs</p>
                  <p className="text-lg font-bold text-text-primary">
                    {jobs.filter((j) => j.resolution === "4K").length}
                  </p>
                  <p className="text-xs text-[#F472B6]">$4.80/hr</p>
                </div>
                <div>
                  <p className="text-xs text-text-muted">1080p Jobs</p>
                  <p className="text-lg font-bold text-text-primary">
                    {jobs.filter((j) => j.resolution === "1080p").length}
                  </p>
                  <p className="text-xs text-[#818CF8]">$2.40/hr</p>
                </div>
                <div>
                  <p className="text-xs text-text-muted">720p Jobs</p>
                  <p className="text-lg font-bold text-text-primary">
                    {jobs.filter((j) => j.resolution === "720p").length}
                  </p>
                  <p className="text-xs text-[#94A3B8]">$1.20/hr</p>
                </div>
                <div>
                  <p className="text-xs text-text-muted">Est. Total</p>
                  <p className="text-lg font-bold">
                    <GradientText>${estimatedCost.toFixed(2)}</GradientText>
                  </p>
                  <p className="text-xs text-text-muted">this session</p>
                </div>
              </div>
            </div>
            <div className="shrink-0">
              <Button variant="secondary" size="sm">
                <span className="flex items-center gap-2">
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                  </svg>
                  View Cost Report
                </span>
              </Button>
            </div>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
}
