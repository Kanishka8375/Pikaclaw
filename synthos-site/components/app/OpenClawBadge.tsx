"use client";

import { motion } from "framer-motion";
import { openClawStatus } from "@/lib/openclaw";

interface OpenClawBadgeProps {
  size?: "sm" | "md" | "lg";
  showVersion?: boolean;
  className?: string;
}

export default function OpenClawBadge({
  size = "sm",
  showVersion = false,
  className = "",
}: OpenClawBadgeProps) {
  const sizeClasses = {
    sm: "px-2.5 py-1 text-[10px] gap-1.5",
    md: "px-3 py-1.5 text-xs gap-2",
    lg: "px-4 py-2 text-sm gap-2.5",
  };

  const dotSizes = {
    sm: "w-1.5 h-1.5",
    md: "w-2 h-2",
    lg: "w-2.5 h-2.5",
  };

  return (
    <div
      className={`inline-flex items-center rounded-full bg-emerald-500/10 border border-emerald-500/20 font-medium text-emerald-400 ${sizeClasses[size]} ${className}`}
    >
      <motion.span
        className={`${dotSizes[size]} rounded-full bg-emerald-400`}
        animate={{ opacity: [1, 0.4, 1] }}
        transition={{ duration: 2, repeat: Infinity, ease: "easeInOut" }}
      />
      <svg className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2L2 7l10 5 10-5-10-5z" />
        <path d="M2 17l10 5 10-5" />
        <path d="M2 12l10 5 10-5" />
      </svg>
      <span>OpenClaw</span>
      {showVersion && (
        <span className="text-emerald-400/60">v{openClawStatus.version}</span>
      )}
    </div>
  );
}
