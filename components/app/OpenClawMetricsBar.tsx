"use client";

import { motion } from "framer-motion";

interface OpenClawMetricsBarProps {
  accuracy: number;
  consistency: number;
  speed: number;
  compact?: boolean;
  className?: string;
}

export default function OpenClawMetricsBar({
  accuracy,
  consistency,
  speed,
  compact = false,
  className = "",
}: OpenClawMetricsBarProps) {
  const metrics = [
    { label: "Accuracy", value: accuracy, color: "from-emerald-500 to-emerald-400", text: "text-emerald-400" },
    { label: "Consistency", value: consistency, color: "from-[#4F46E5] to-[#818CF8]", text: "text-[#818CF8]" },
    { label: "Speed", value: speed, color: "from-[#EC4899] to-[#F472B6]", text: "text-[#F472B6]" },
  ];

  if (compact) {
    return (
      <div className={`flex items-center gap-4 ${className}`}>
        {metrics.map((m) => (
          <div key={m.label} className="flex items-center gap-1.5">
            <span className="text-[10px] text-text-muted uppercase tracking-wider">{m.label}</span>
            <span className={`text-xs font-mono font-bold ${m.text}`}>{m.value}%</span>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className={`space-y-2.5 ${className}`}>
      {metrics.map((m) => (
        <div key={m.label}>
          <div className="flex items-center justify-between mb-1">
            <span className="text-xs text-text-muted">{m.label}</span>
            <span className={`text-xs font-mono font-bold ${m.text}`}>{m.value}%</span>
          </div>
          <div className="h-1.5 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
            <motion.div
              className={`h-full rounded-full bg-gradient-to-r ${m.color}`}
              initial={{ width: 0 }}
              animate={{ width: `${m.value}%` }}
              transition={{ duration: 1, ease: "easeOut", delay: 0.2 }}
            />
          </div>
        </div>
      ))}
    </div>
  );
}
