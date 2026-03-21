"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import Card from "@/components/ui/Card";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";
import {
  mockProjects,
  mockRenderJobs,
  mockNotifications,
  dashboardStats,
} from "@/lib/mock-data";

/* ------------------------------------------------------------------ */
/*  Helpers                                                            */
/* ------------------------------------------------------------------ */

function formatDate(date: Date) {
  return date.toLocaleDateString("en-US", {
    weekday: "long",
    year: "numeric",
    month: "long",
    day: "numeric",
  });
}

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

const notificationIcons: Record<string, React.ReactNode> = {
  success: (
    <svg className="w-5 h-5 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  info: (
    <svg className="w-5 h-5 text-[#818CF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
  warning: (
    <svg className="w-5 h-5 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
    </svg>
  ),
  error: (
    <svg className="w-5 h-5 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
};

function timeAgo(dateStr: string) {
  const now = new Date();
  const date = new Date(dateStr);
  const seconds = Math.floor((now.getTime() - date.getTime()) / 1000);
  if (seconds < 60) return "just now";
  const minutes = Math.floor(seconds / 60);
  if (minutes < 60) return `${minutes}m ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

/* ------------------------------------------------------------------ */
/*  Stats data                                                         */
/* ------------------------------------------------------------------ */

const stats = [
  {
    label: "Total Projects",
    value: dashboardStats.totalProjects,
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
      </svg>
    ),
    color: "from-[#4F46E5] to-[#818CF8]",
  },
  {
    label: "Active Renders",
    value: dashboardStats.activeRenders,
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
      </svg>
    ),
    color: "from-[#EC4899] to-[#F472B6]",
  },
  {
    label: "Episodes Created",
    value: dashboardStats.totalEpisodes,
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4M4 20h16a1 1 0 001-1V5a1 1 0 00-1-1H4a1 1 0 00-1 1v14a1 1 0 001 1z" />
      </svg>
    ),
    color: "from-[#4F46E5] to-[#EC4899]",
  },
  {
    label: "Characters",
    value: dashboardStats.totalCharacters,
    icon: (
      <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
      </svg>
    ),
    color: "from-[#818CF8] to-[#EC4899]",
  },
];

/* ------------------------------------------------------------------ */
/*  Page Component                                                     */
/* ------------------------------------------------------------------ */

export default function DashboardPage() {
  const { user } = useAuth();

  const recentProjects = mockProjects.slice(0, 3);
  const activeRenders = mockRenderJobs.filter(
    (j) => j.status === "queued" || j.status === "rendering",
  );
  const recentNotifications = mockNotifications.slice(0, 5);

  const renderPct =
    Math.round(
      (dashboardStats.renderHoursUsed / dashboardStats.renderHoursLimit) * 100,
    );
  const storagePct =
    Math.round(
      (dashboardStats.storageUsedGB / dashboardStats.storageLimitGB) * 100,
    );

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* ---- Welcome Header ---- */}
      <motion.div variants={fadeInUp} className="flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">
            Welcome back,{" "}
            <GradientText>{user?.name ?? "Creator"}</GradientText>
          </h1>
          <p className="mt-1 text-text-secondary">{formatDate(new Date())}</p>
        </div>
      </motion.div>

      {/* ---- Stats Grid ---- */}
      <motion.div
        variants={staggerContainer}
        className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4"
      >
        {stats.map((stat) => (
          <Card key={stat.label} className="relative overflow-hidden">
            {/* Faint gradient orb behind the card */}
            <div
              className={`pointer-events-none absolute -right-4 -top-4 h-24 w-24 rounded-full bg-gradient-to-br ${stat.color} opacity-10 blur-2xl`}
            />
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-text-muted">{stat.label}</p>
                <p className="mt-2 text-3xl font-bold text-text-primary">
                  {stat.value}
                </p>
              </div>
              <div
                className={`flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br ${stat.color} text-white`}
              >
                {stat.icon}
              </div>
            </div>
          </Card>
        ))}
      </motion.div>

      {/* ---- Usage Meters ---- */}
      <motion.div
        variants={staggerContainer}
        className="grid grid-cols-1 gap-4 md:grid-cols-2"
      >
        {/* Render Hours */}
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#4F46E5]/20">
                <svg className="h-5 w-5 text-[#818CF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-text-primary">Render Hours</p>
                <p className="text-xs text-text-muted">Monthly allocation</p>
              </div>
            </div>
            <p className="text-sm font-semibold text-text-secondary">
              {dashboardStats.renderHoursUsed}
              <span className="text-text-muted">
                {" "}/ {dashboardStats.renderHoursLimit} hrs
              </span>
            </p>
          </div>
          <div className="h-3 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
              initial={{ width: 0 }}
              animate={{ width: `${renderPct}%` }}
              transition={{ duration: 1, ease: "easeOut", delay: 0.4 }}
            />
          </div>
          <p className="mt-2 text-right text-xs text-text-muted">{renderPct}% used</p>
        </Card>

        {/* Storage */}
        <Card>
          <div className="mb-4 flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-[#EC4899]/20">
                <svg className="h-5 w-5 text-[#F472B6]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4m0 5c0 2.21-3.582 4-8 4s-8-1.79-8-4" />
                </svg>
              </div>
              <div>
                <p className="text-sm font-medium text-text-primary">Storage</p>
                <p className="text-xs text-text-muted">Cloud storage</p>
              </div>
            </div>
            <p className="text-sm font-semibold text-text-secondary">
              {dashboardStats.storageUsedGB}
              <span className="text-text-muted">
                {" "}/ {dashboardStats.storageLimitGB} GB
              </span>
            </p>
          </div>
          <div className="h-3 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
              initial={{ width: 0 }}
              animate={{ width: `${storagePct}%` }}
              transition={{ duration: 1, ease: "easeOut", delay: 0.5 }}
            />
          </div>
          <p className="mt-2 text-right text-xs text-text-muted">{storagePct}% used</p>
        </Card>
      </motion.div>

      {/* ---- Recent Projects + Active Renders ---- */}
      <motion.div
        variants={staggerContainer}
        className="grid grid-cols-1 gap-6 lg:grid-cols-2"
      >
        {/* Recent Projects */}
        <Card hover={false} className="!p-0 overflow-hidden">
          <div className="border-b border-void-border px-6 py-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-text-primary">Recent Projects</h2>
              <Link
                href="/projects"
                className="text-sm text-[#818CF8] hover:text-[#4F46E5] transition-colors"
              >
                View all
              </Link>
            </div>
          </div>
          <div className="divide-y divide-void-border">
            {recentProjects.map((project) => (
              <motion.div
                key={project.id}
                variants={fadeInUp}
                className="flex items-center justify-between px-6 py-4 hover:bg-void-lighter/50 transition-colors"
              >
                <div className="min-w-0 flex-1">
                  <p className="truncate text-sm font-medium text-text-primary">
                    {project.name}
                  </p>
                  <p className="mt-0.5 text-xs text-text-muted">
                    {project.genre} &middot; {project.episodes} episode{project.episodes !== 1 ? "s" : ""}
                  </p>
                </div>
                <span
                  className={`ml-3 shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${statusColors[project.status]}`}
                >
                  {statusLabels[project.status]}
                </span>
              </motion.div>
            ))}
            {recentProjects.length === 0 && (
              <p className="px-6 py-8 text-center text-sm text-text-muted">
                No projects yet. Create your first one!
              </p>
            )}
          </div>
        </Card>

        {/* Active Renders */}
        <Card hover={false} className="!p-0 overflow-hidden">
          <div className="border-b border-void-border px-6 py-4">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-text-primary">Active Renders</h2>
              <Link
                href="/render-queue"
                className="text-sm text-[#818CF8] hover:text-[#4F46E5] transition-colors"
              >
                View queue
              </Link>
            </div>
          </div>
          <div className="divide-y divide-void-border">
            {activeRenders.length > 0 ? (
              activeRenders.map((job) => (
                <motion.div
                  key={job.id}
                  variants={fadeInUp}
                  className="px-6 py-4 space-y-3"
                >
                  <div className="flex items-center justify-between">
                    <div className="min-w-0 flex-1">
                      <p className="truncate text-sm font-medium text-text-primary">
                        {job.episodeName}
                      </p>
                      <p className="mt-0.5 text-xs text-text-muted">
                        {job.gpu} &middot; {job.resolution}
                      </p>
                    </div>
                    <span
                      className={`ml-3 shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium ${
                        job.status === "rendering"
                          ? "bg-[#EC4899]/20 text-[#F472B6] border border-[#EC4899]/30"
                          : "bg-[#4F46E5]/20 text-[#818CF8] border border-[#4F46E5]/30"
                      }`}
                    >
                      {job.status === "rendering" ? "Rendering" : "Queued"}
                    </span>
                  </div>
                  <div>
                    <div className="mb-1 flex items-center justify-between text-xs text-text-muted">
                      <span>Progress</span>
                      <span>{job.progress}%</span>
                    </div>
                    <div className="h-2 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
                      <motion.div
                        className="h-full rounded-full bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
                        initial={{ width: 0 }}
                        animate={{ width: `${job.progress}%` }}
                        transition={{ duration: 1, ease: "easeOut", delay: 0.6 }}
                      />
                    </div>
                    <p className="mt-1 text-right text-xs text-text-muted">
                      ETA: {job.estimatedTime}
                    </p>
                  </div>
                </motion.div>
              ))
            ) : (
              <p className="px-6 py-8 text-center text-sm text-text-muted">
                No active renders at the moment.
              </p>
            )}
          </div>
        </Card>
      </motion.div>

      {/* ---- Recent Activity ---- */}
      <Card hover={false} className="!p-0 overflow-hidden">
        <div className="border-b border-void-border px-6 py-4">
          <h2 className="text-lg font-semibold text-text-primary">Recent Activity</h2>
        </div>
        <div className="divide-y divide-void-border">
          {recentNotifications.map((notif) => (
            <motion.div
              key={notif.id}
              variants={fadeInUp}
              className="flex items-start gap-3 px-6 py-4 hover:bg-void-lighter/50 transition-colors"
            >
              <div className="mt-0.5 shrink-0">
                {notificationIcons[notif.type]}
              </div>
              <div className="min-w-0 flex-1">
                <p className="text-sm font-medium text-text-primary">{notif.title}</p>
                <p className="mt-0.5 text-xs text-text-muted leading-relaxed">
                  {notif.message}
                </p>
              </div>
              <span className="shrink-0 text-xs text-text-muted">
                {timeAgo(notif.createdAt)}
              </span>
            </motion.div>
          ))}
          {recentNotifications.length === 0 && (
            <p className="px-6 py-8 text-center text-sm text-text-muted">
              No recent activity.
            </p>
          )}
        </div>
      </Card>

      {/* ---- Quick Actions ---- */}
      <motion.div variants={fadeInUp} className="flex flex-wrap items-center gap-3">
        <Link
          href="/projects?new=true"
          className="group inline-flex items-center gap-2 rounded-xl bg-gradient-to-r from-[#4F46E5] to-[#EC4899] px-5 py-2.5 text-sm font-semibold text-white shadow-lg shadow-[#4F46E5]/20 transition-all hover:shadow-[#4F46E5]/40 hover:brightness-110"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
          </svg>
          New Project
        </Link>
        <Link
          href="/pipeline"
          className="inline-flex items-center gap-2 rounded-xl border border-void-border bg-void-light px-5 py-2.5 text-sm font-semibold text-text-primary transition-all hover:border-[#4F46E5]/40 hover:bg-void-lighter"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 4v16M17 4v16M3 8h4m10 0h4M3 12h18M3 16h4m10 0h4" />
          </svg>
          Create Episode
        </Link>
        <Link
          href="/marketplace"
          className="inline-flex items-center gap-2 rounded-xl border border-void-border bg-void-light px-5 py-2.5 text-sm font-semibold text-text-primary transition-all hover:border-[#EC4899]/40 hover:bg-void-lighter"
        >
          <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 3h2l.4 2M7 13h10l4-8H5.4M7 13L5.4 5M7 13l-2.293 2.293c-.63.63-.184 1.707.707 1.707H17m0 0a2 2 0 100 4 2 2 0 000-4zm-8 2a2 2 0 100 4 2 2 0 000-4z" />
          </svg>
          Open Marketplace
        </Link>
      </motion.div>
    </motion.div>
  );
}
