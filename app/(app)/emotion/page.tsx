"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import GradientText from "@/components/ui/GradientText";
import { fadeInUp, staggerContainer } from "@/lib/animations";
import OpenClawBadge from "@/components/app/OpenClawBadge";
import OpenClawMetricsBar from "@/components/app/OpenClawMetricsBar";
import { openClawAgents } from "@/lib/openclaw";

/* ------------------------------------------------------------------ */
/*  Types & Data                                                       */
/* ------------------------------------------------------------------ */

interface ChannelData {
  name: string;
  value: number;
  color: string;
  gradient: string;
}

interface Preset {
  name: string;
  values: [number, number, number, number];
}

interface Shot {
  id: number;
  character: string;
  emotion: string;
  intensity: number;
  duration: string;
}

const scenes = [
  "Battle at Shadow Gate",
  "First Meeting",
  "Betrayal Reveal",
  "Peaceful Morning",
  "Final Confrontation",
];

const presets: Preset[] = [
  { name: "Calm", values: [20, 15, 10, 5] },
  { name: "Tense", values: [65, 70, 75, 60] },
  { name: "Explosive", values: [95, 90, 100, 85] },
  { name: "Melancholy", values: [40, 55, 45, 20] },
  { name: "Comedic", values: [70, 60, 30, 45] },
  { name: "Epic", values: [85, 80, 95, 90] },
];

const presetColors: Record<string, string> = {
  Calm: "border-sky-500/40 text-sky-400 hover:bg-sky-500/10",
  Tense: "border-amber-500/40 text-amber-400 hover:bg-amber-500/10",
  Explosive: "border-red-500/40 text-red-400 hover:bg-red-500/10",
  Melancholy: "border-violet-500/40 text-violet-400 hover:bg-violet-500/10",
  Comedic: "border-emerald-500/40 text-emerald-400 hover:bg-emerald-500/10",
  Epic: "border-pink/40 text-pink hover:bg-pink/10",
};

const sceneMarkers = [
  { position: 0, label: "Intro" },
  { position: 20, label: "Build" },
  { position: 45, label: "Climax" },
  { position: 70, label: "Fall" },
  { position: 90, label: "Resolve" },
];

const characters = ["Kael", "Lyra", "Morrow", "Seraph", "Narrator"];
const emotions = ["Neutral", "Joy", "Anger", "Fear", "Sadness", "Surprise", "Determination"];

const initialShots: Shot[] = [
  { id: 1, character: "Kael", emotion: "Determination", intensity: 72, duration: "3.2s" },
  { id: 2, character: "Lyra", emotion: "Fear", intensity: 58, duration: "2.8s" },
  { id: 3, character: "Morrow", emotion: "Anger", intensity: 85, duration: "4.1s" },
];

/* ------------------------------------------------------------------ */
/*  Icons                                                              */
/* ------------------------------------------------------------------ */

function FaceIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
  );
}

function VoiceIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
    </svg>
  );
}

function MusicIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 19V6l12-3v13M9 19c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zm12-3c0 1.105-1.343 2-3 2s-3-.895-3-2 1.343-2 3-2 3 .895 3 2zM9 10l12-3" />
    </svg>
  );
}

function CameraIcon() {
  return (
    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
    </svg>
  );
}

/* ------------------------------------------------------------------ */
/*  Component                                                          */
/* ------------------------------------------------------------------ */

export default function EmotionChoreographyPage() {
  const [selectedScene, setSelectedScene] = useState(scenes[0]);
  const [channels, setChannels] = useState<ChannelData[]>([
    { name: "Facial Expression", value: 45, color: "text-indigo", gradient: "from-indigo/20 via-indigo/60 to-indigo" },
    { name: "Voice Tone", value: 60, color: "text-pink", gradient: "from-pink/20 via-pink/60 to-pink" },
    { name: "Music Intensity", value: 35, color: "text-amber-400", gradient: "from-amber-400/20 via-amber-400/60 to-amber-400" },
    { name: "Camera Movement", value: 25, color: "text-emerald-400", gradient: "from-emerald-400/20 via-emerald-400/60 to-emerald-400" },
  ]);
  const [activePreset, setActivePreset] = useState<string | null>(null);
  const [shots, setShots] = useState<Shot[]>(initialShots);
  const [timelinePosition, setTimelinePosition] = useState(45);

  const channelIcons = [<FaceIcon key="f" />, <VoiceIcon key="v" />, <MusicIcon key="m" />, <CameraIcon key="c" />];

  function applyPreset(preset: Preset) {
    setActivePreset(preset.name);
    setChannels((prev) =>
      prev.map((ch, i) => ({ ...ch, value: preset.values[i] }))
    );
  }

  function updateShotIntensity(shotId: number, intensity: number) {
    setShots((prev) =>
      prev.map((s) => (s.id === shotId ? { ...s, intensity } : s))
    );
  }

  function updateShotEmotion(shotId: number, emotion: string) {
    setShots((prev) =>
      prev.map((s) => (s.id === shotId ? { ...s, emotion } : s))
    );
  }

  function updateShotCharacter(shotId: number, character: string) {
    setShots((prev) =>
      prev.map((s) => (s.id === shotId ? { ...s, character } : s))
    );
  }

  /* overall average for heat strip */
  const overallIntensity = Math.round(
    channels.reduce((sum, c) => sum + c.value, 0) / channels.length
  );

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-8"
    >
      {/* Header */}
      <motion.div variants={fadeInUp} className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-text-primary">
            Emotion <GradientText>Choreography</GradientText>
          </h1>
          <div className="flex items-center gap-2 mt-1">
            <p className="text-text-secondary">Direct emotional arcs across every scene channel</p>
            <OpenClawBadge size="sm" />
          </div>
        </div>

        {/* Scene selector */}
        <div className="flex items-center gap-3">
          <label className="text-text-muted text-sm">Scene</label>
          <select
            value={selectedScene}
            onChange={(e) => setSelectedScene(e.target.value)}
            className="px-4 py-2.5 rounded-xl bg-void-light border border-void-border text-text-primary focus:outline-none focus:border-indigo focus:ring-1 focus:ring-indigo/50 transition-all text-sm min-w-[220px]"
          >
            {scenes.map((s) => (
              <option key={s} value={s} className="bg-void-light">{s}</option>
            ))}
          </select>
        </div>
      </motion.div>

      {/* Timeline */}
      <Card>
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-text-primary tracking-wide uppercase">Scene Timeline</h2>
          <span className="text-xs text-text-muted">{selectedScene}</span>
        </div>

        <div className="relative h-12 mt-2">
          {/* Track */}
          <div className="absolute inset-x-0 top-1/2 -translate-y-1/2 h-2 rounded-full bg-void-lighter overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-indigo to-pink"
              animate={{ width: `${timelinePosition}%` }}
              transition={{ type: "spring", stiffness: 120, damping: 20 }}
            />
          </div>

          {/* Markers */}
          {sceneMarkers.map((m) => (
            <button
              key={m.label}
              onClick={() => setTimelinePosition(m.position)}
              className="absolute top-1/2 -translate-y-1/2 -translate-x-1/2 flex flex-col items-center group cursor-pointer"
              style={{ left: `${m.position}%` }}
            >
              <span className="w-3.5 h-3.5 rounded-full border-2 border-indigo bg-void-light group-hover:bg-indigo transition-colors" />
              <span className="text-[10px] text-text-muted mt-3 group-hover:text-text-primary transition-colors">{m.label}</span>
            </button>
          ))}

          {/* Playhead */}
          <motion.div
            className="absolute top-0 bottom-0 w-0.5 bg-pink"
            animate={{ left: `${timelinePosition}%` }}
            transition={{ type: "spring", stiffness: 120, damping: 20 }}
          >
            <div className="absolute -top-1 left-1/2 -translate-x-1/2 w-3 h-3 rounded-full bg-pink shadow-[0_0_10px_rgba(236,72,153,0.6)]" />
          </motion.div>
        </div>
      </Card>

      {/* Emotion Channels */}
      <motion.div variants={fadeInUp}>
        <h2 className="text-sm font-semibold text-text-primary tracking-wide uppercase mb-4">Emotion Channels</h2>
        <div className="space-y-3">
          {channels.map((channel, idx) => (
            <Card key={channel.name} className="!p-4" hover={false}>
              <div className="flex items-center gap-4">
                {/* Icon + Name */}
                <div className={`flex items-center gap-2.5 min-w-[180px] ${channel.color}`}>
                  {channelIcons[idx]}
                  <span className="text-sm font-medium">{channel.name}</span>
                </div>

                {/* Min */}
                <span className="text-[10px] text-text-muted w-6 text-right">0</span>

                {/* Bar */}
                <div className="flex-1 h-8 rounded-lg bg-void-lighter overflow-hidden relative">
                  <motion.div
                    className={`h-full rounded-lg bg-gradient-to-r ${channel.gradient}`}
                    animate={{ width: `${channel.value}%` }}
                    transition={{ type: "spring", stiffness: 100, damping: 18 }}
                  />
                  {/* curve decoration */}
                  <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 100">
                    <motion.path
                      d={`M0,${100 - channel.value * 0.6} Q25,${100 - channel.value * 0.9} 50,${100 - channel.value * 0.5} T100,${100 - channel.value * 0.7}`}
                      fill="none"
                      stroke="rgba(255,255,255,0.15)"
                      strokeWidth="2"
                      vectorEffect="non-scaling-stroke"
                    />
                  </svg>
                </div>

                {/* Max */}
                <span className="text-[10px] text-text-muted w-8">100</span>

                {/* Value */}
                <motion.span
                  key={channel.value}
                  initial={{ scale: 1.3, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  className={`text-lg font-bold w-12 text-right tabular-nums ${channel.color}`}
                >
                  {channel.value}
                </motion.span>
              </div>
            </Card>
          ))}
        </div>
      </motion.div>

      {/* Emotion Presets */}
      <motion.div variants={fadeInUp}>
        <h2 className="text-sm font-semibold text-text-primary tracking-wide uppercase mb-4">Emotion Presets</h2>
        <div className="flex flex-wrap gap-3">
          {presets.map((p) => (
            <motion.button
              key={p.name}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={() => applyPreset(p)}
              className={`
                px-5 py-2.5 rounded-xl border text-sm font-medium transition-all cursor-pointer
                ${activePreset === p.name ? "ring-1 ring-offset-1 ring-offset-void bg-void-lighter" : "bg-void-light/50"}
                ${presetColors[p.name]}
              `}
            >
              {p.name}
            </motion.button>
          ))}
        </div>
      </motion.div>

      {/* Per-Shot Controls */}
      <motion.div variants={fadeInUp}>
        <h2 className="text-sm font-semibold text-text-primary tracking-wide uppercase mb-4">Per-Shot Controls</h2>
        <div className="space-y-3">
          <AnimatePresence>
            {shots.map((shot) => (
              <motion.div
                key={shot.id}
                layout
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
              >
                <Card className="!p-4" hover={false}>
                  <div className="flex flex-col lg:flex-row lg:items-center gap-4">
                    {/* Shot number */}
                    <div className="flex items-center gap-2 min-w-[80px]">
                      <span className="w-8 h-8 rounded-lg bg-indigo/20 text-indigo flex items-center justify-center text-sm font-bold">
                        {shot.id}
                      </span>
                      <span className="text-xs text-text-muted uppercase tracking-wider">Shot</span>
                    </div>

                    {/* Character */}
                    <div className="flex flex-col gap-1 min-w-[140px]">
                      <label className="text-[10px] text-text-muted uppercase tracking-wider">Character</label>
                      <select
                        value={shot.character}
                        onChange={(e) => updateShotCharacter(shot.id, e.target.value)}
                        className="px-3 py-1.5 rounded-lg bg-void-lighter border border-void-border text-text-primary text-sm focus:outline-none focus:border-indigo transition-all"
                      >
                        {characters.map((c) => (
                          <option key={c} value={c} className="bg-void-light">{c}</option>
                        ))}
                      </select>
                    </div>

                    {/* Emotion */}
                    <div className="flex flex-col gap-1 min-w-[140px]">
                      <label className="text-[10px] text-text-muted uppercase tracking-wider">Emotion</label>
                      <select
                        value={shot.emotion}
                        onChange={(e) => updateShotEmotion(shot.id, e.target.value)}
                        className="px-3 py-1.5 rounded-lg bg-void-lighter border border-void-border text-text-primary text-sm focus:outline-none focus:border-indigo transition-all"
                      >
                        {emotions.map((e) => (
                          <option key={e} value={e} className="bg-void-light">{e}</option>
                        ))}
                      </select>
                    </div>

                    {/* Intensity slider */}
                    <div className="flex flex-col gap-1 flex-1 min-w-[180px]">
                      <div className="flex items-center justify-between">
                        <label className="text-[10px] text-text-muted uppercase tracking-wider">Intensity</label>
                        <span className="text-xs font-mono text-indigo">{shot.intensity}%</span>
                      </div>
                      <input
                        type="range"
                        min={0}
                        max={100}
                        value={shot.intensity}
                        onChange={(e) => updateShotIntensity(shot.id, Number(e.target.value))}
                        className="w-full h-2 rounded-full appearance-none cursor-pointer
                          bg-void-lighter
                          [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-4 [&::-webkit-slider-thumb]:h-4 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-indigo [&::-webkit-slider-thumb]:shadow-[0_0_8px_rgba(79,70,229,0.5)] [&::-webkit-slider-thumb]:cursor-pointer
                          [&::-moz-range-thumb]:w-4 [&::-moz-range-thumb]:h-4 [&::-moz-range-thumb]:rounded-full [&::-moz-range-thumb]:bg-indigo [&::-moz-range-thumb]:border-0 [&::-moz-range-thumb]:shadow-[0_0_8px_rgba(79,70,229,0.5)] [&::-moz-range-thumb]:cursor-pointer"
                      />
                    </div>

                    {/* Duration */}
                    <div className="flex flex-col gap-1 min-w-[70px]">
                      <label className="text-[10px] text-text-muted uppercase tracking-wider">Duration</label>
                      <span className="text-sm text-text-primary font-mono">{shot.duration}</span>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      </motion.div>

      {/* Action Buttons */}
      <motion.div variants={fadeInUp} className="flex flex-wrap gap-4">
        <Button variant="primary" size="md">
          Apply to Scene
        </Button>
        <Button variant="secondary" size="md">
          <span className="flex items-center gap-2">
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Preview Sync
          </span>
        </Button>
      </motion.div>

      {/* OpenClaw Emotion Engine */}
      <motion.div variants={fadeInUp}>
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <svg className="w-4 h-4 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
            </svg>
            <span className="text-sm font-semibold text-emerald-400">OpenClaw Emotion Engine</span>
            <span className="text-[10px] text-text-muted ml-auto">24/7 real-time emotion sync</span>
          </div>
          <OpenClawMetricsBar
            accuracy={openClawAgents.find(a => a.name === "Voice Synthesizer")?.accuracy ?? 98}
            consistency={openClawAgents.find(a => a.name === "Voice Synthesizer")?.consistency ?? 97}
            speed={openClawAgents.find(a => a.name === "Voice Synthesizer")?.speed ?? 95}
          />
        </Card>
      </motion.div>

      {/* Intensity Heat Strip */}
      <motion.div variants={fadeInUp}>
        <Card hover={false}>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-text-primary tracking-wide uppercase">Overall Emotion Flow</h2>
            <span className="text-xs text-text-muted">
              Avg Intensity: <span className="text-text-primary font-mono">{overallIntensity}%</span>
            </span>
          </div>

          {/* Heat strip */}
          <div className="relative h-10 rounded-xl overflow-hidden">
            <div
              className="absolute inset-0 rounded-xl"
              style={{
                background: `linear-gradient(to right,
                  rgba(56,189,248,0.6) 0%,
                  rgba(56,189,248,0.4) 10%,
                  rgba(79,70,229,0.5) 25%,
                  rgba(168,85,247,0.6) 40%,
                  rgba(236,72,153,0.7) 55%,
                  rgba(239,68,68,0.8) 70%,
                  rgba(239,68,68,0.9) 85%,
                  rgba(239,68,68,1) 100%
                )`,
              }}
            />
            {/* animated overlay */}
            <motion.div
              className="absolute inset-0 rounded-xl"
              animate={{ backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"] }}
              transition={{ duration: 8, repeat: Infinity, ease: "linear" }}
              style={{
                backgroundSize: "200% 200%",
                background: "linear-gradient(90deg, transparent 0%, rgba(255,255,255,0.05) 50%, transparent 100%)",
              }}
            />
            {/* Playhead marker on strip */}
            <motion.div
              className="absolute top-0 bottom-0 w-0.5 bg-white/70"
              animate={{ left: `${timelinePosition}%` }}
              transition={{ type: "spring", stiffness: 120, damping: 20 }}
            />
          </div>

          {/* Labels */}
          <div className="flex items-center justify-between mt-2">
            <span className="text-[10px] text-sky-400 flex items-center gap-1">
              <span className="w-2 h-2 rounded-full bg-sky-400 inline-block" />
              Calm
            </span>
            <span className="text-[10px] text-violet-400">Moderate</span>
            <span className="text-[10px] text-red-400 flex items-center gap-1">
              Intense
              <span className="w-2 h-2 rounded-full bg-red-400 inline-block" />
            </span>
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
}
