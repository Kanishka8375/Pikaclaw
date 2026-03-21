"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";

interface WorkflowNode {
  id: string;
  type: "input" | "agent" | "model" | "output" | "condition";
  name: string;
  status: "idle" | "running" | "complete";
  x: number;
  y: number;
}

const nodeTypeColors: Record<WorkflowNode["type"], string> = {
  input: "border-emerald-500/50 bg-emerald-500/10",
  agent: "border-[#4F46E5]/50 bg-[#4F46E5]/10",
  model: "border-[#EC4899]/50 bg-[#EC4899]/10",
  output: "border-amber-500/50 bg-amber-500/10",
  condition: "border-violet-500/50 bg-violet-500/10",
};

const nodeTypeIcons: Record<WorkflowNode["type"], React.ReactNode> = {
  input: (
    <svg className="w-4 h-4 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
    </svg>
  ),
  agent: (
    <svg className="w-4 h-4 text-[#818CF8]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
  ),
  model: (
    <svg className="w-4 h-4 text-[#F472B6]" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 7v10c0 2.21 3.582 4 8 4s8-1.79 8-4V7M4 7c0 2.21 3.582 4 8 4s8-1.79 8-4M4 7c0-2.21 3.582-4 8-4s8 1.79 8 4" />
    </svg>
  ),
  output: (
    <svg className="w-4 h-4 text-amber-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
    </svg>
  ),
  condition: (
    <svg className="w-4 h-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  ),
};

const initialNodes: WorkflowNode[] = [
  { id: "n1", type: "input", name: "Story Brief", status: "complete", x: 80, y: 50 },
  { id: "n2", type: "agent", name: "Script Writer", status: "complete", x: 280, y: 50 },
  { id: "n3", type: "agent", name: "Storyboard Agent", status: "running", x: 480, y: 20 },
  { id: "n4", type: "model", name: "AnimeDiffusion v3", status: "idle", x: 480, y: 100 },
  { id: "n5", type: "condition", name: "Quality Gate", status: "idle", x: 680, y: 50 },
  { id: "n6", type: "agent", name: "Voice Sync", status: "idle", x: 880, y: 20 },
  { id: "n7", type: "agent", name: "Music Composer", status: "idle", x: 880, y: 100 },
  { id: "n8", type: "agent", name: "Editor", status: "idle", x: 1080, y: 50 },
  { id: "n9", type: "output", name: "Final Render", status: "idle", x: 1280, y: 50 },
];

const connections = [
  ["n1", "n2"],
  ["n2", "n3"],
  ["n2", "n4"],
  ["n3", "n5"],
  ["n4", "n5"],
  ["n5", "n6"],
  ["n5", "n7"],
  ["n6", "n8"],
  ["n7", "n8"],
  ["n8", "n9"],
];

export default function WorkflowPage() {
  const [nodes] = useState(initialNodes);

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
            Workflow <GradientText>Canvas</GradientText>
          </h1>
          <p className="mt-1 text-text-secondary">
            Design and orchestrate your AI agent pipeline visually.
          </p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" size="md">
            Load Template
          </Button>
          <Button size="md">
            <span className="flex items-center gap-2">
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Run Pipeline
            </span>
          </Button>
        </div>
      </motion.div>

      {/* Canvas */}
      <motion.div variants={fadeInUp}>
        <Card hover={false} className="!p-0 overflow-hidden">
          <div className="overflow-x-auto">
            <svg
              width="1400"
              height="180"
              className="min-w-[1400px]"
              viewBox="0 0 1400 180"
            >
              {/* Grid pattern */}
              <defs>
                <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
                  <path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" strokeWidth="1" />
                </pattern>
              </defs>
              <rect width="1400" height="180" fill="url(#grid)" />

              {/* Connections */}
              {connections.map(([fromId, toId]) => {
                const from = nodes.find((n) => n.id === fromId)!;
                const to = nodes.find((n) => n.id === toId)!;
                const fromX = from.x + 70;
                const fromY = from.y + 30;
                const toX = to.x;
                const toY = to.y + 30;
                const midX = (fromX + toX) / 2;
                return (
                  <path
                    key={`${fromId}-${toId}`}
                    d={`M ${fromX} ${fromY} C ${midX} ${fromY}, ${midX} ${toY}, ${toX} ${toY}`}
                    fill="none"
                    stroke={
                      from.status === "complete" && to.status !== "idle"
                        ? "rgba(79,70,229,0.5)"
                        : "rgba(100,116,139,0.2)"
                    }
                    strokeWidth="2"
                    strokeDasharray={from.status === "complete" ? "0" : "6 4"}
                  />
                );
              })}

              {/* Nodes */}
              {nodes.map((node) => (
                <g key={node.id} transform={`translate(${node.x}, ${node.y})`}>
                  <rect
                    width="140"
                    height="60"
                    rx="12"
                    className={`fill-[#141420] stroke-current ${
                      node.status === "running"
                        ? "stroke-[#4F46E5]"
                        : node.status === "complete"
                        ? "stroke-emerald-500/50"
                        : "stroke-[#2A2A3E]"
                    }`}
                    strokeWidth="1.5"
                  />
                  {node.status === "running" && (
                    <rect
                      width="140"
                      height="60"
                      rx="12"
                      fill="none"
                      stroke="rgba(79,70,229,0.3)"
                      strokeWidth="3"
                      className="animate-pulse"
                    />
                  )}
                  <foreignObject x="10" y="8" width="120" height="44">
                    <div className="flex flex-col items-start gap-1">
                      <span className="text-[10px] text-text-muted uppercase tracking-wider">
                        {node.type}
                      </span>
                      <span className="text-xs font-medium text-text-primary truncate w-full">
                        {node.name}
                      </span>
                    </div>
                  </foreignObject>
                  {/* Status indicator */}
                  <circle
                    cx="125"
                    cy="14"
                    r="5"
                    className={
                      node.status === "complete"
                        ? "fill-emerald-400"
                        : node.status === "running"
                        ? "fill-[#818CF8] animate-pulse"
                        : "fill-[#64748B]/40"
                    }
                  />
                </g>
              ))}
            </svg>
          </div>
        </Card>
      </motion.div>

      {/* Node Palette */}
      <motion.div variants={fadeInUp}>
        <h2 className="text-sm font-semibold text-text-primary tracking-wide uppercase mb-4">
          Node Palette
        </h2>
        <div className="flex flex-wrap gap-3">
          {(["input", "agent", "model", "condition", "output"] as const).map((type) => (
            <div
              key={type}
              className={`flex items-center gap-2.5 rounded-xl border px-4 py-3 transition-all cursor-grab ${nodeTypeColors[type]}`}
            >
              {nodeTypeIcons[type]}
              <span className="text-sm font-medium text-text-primary capitalize">
                {type}
              </span>
            </div>
          ))}
        </div>
      </motion.div>

      {/* Pipeline Stats */}
      <motion.div variants={staggerContainer} className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        {[
          { label: "Total Nodes", value: nodes.length, color: "from-[#4F46E5] to-[#818CF8]" },
          { label: "Running", value: nodes.filter((n) => n.status === "running").length, color: "from-[#4F46E5] to-[#EC4899]" },
          { label: "Completed", value: nodes.filter((n) => n.status === "complete").length, color: "from-emerald-500 to-emerald-400" },
          { label: "Idle", value: nodes.filter((n) => n.status === "idle").length, color: "from-[#64748B] to-[#94A3B8]" },
        ].map((stat) => (
          <Card key={stat.label} className="relative overflow-hidden">
            <div className={`pointer-events-none absolute -right-4 -top-4 h-20 w-20 rounded-full bg-gradient-to-br ${stat.color} opacity-10 blur-2xl`} />
            <p className="text-xs text-text-muted uppercase tracking-wider">{stat.label}</p>
            <p className="mt-1 text-2xl font-bold text-text-primary">{stat.value}</p>
          </Card>
        ))}
      </motion.div>
    </motion.div>
  );
}
