"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import Input from "@/components/ui/Input";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";
import OpenClawMetricsBar from "@/components/app/OpenClawMetricsBar";
import { openClawStatus, openClawMetrics, openClawAgents } from "@/lib/openclaw";

/* ------------------------------------------------------------------ */
/*  Types & Constants                                                  */
/* ------------------------------------------------------------------ */

type Tab = "profile" | "preferences" | "api-keys" | "openclaw" | "self-hosted" | "notifications";

const TABS: { id: Tab; label: string; icon: React.ReactNode }[] = [
  {
    id: "profile",
    label: "Profile",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    ),
  },
  {
    id: "preferences",
    label: "Preferences",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.066 2.573c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.573 1.066c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.066-2.573c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.573-1.066z" />
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
      </svg>
    ),
  },
  {
    id: "api-keys",
    label: "API Keys",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z" />
      </svg>
    ),
  },
  {
    id: "openclaw",
    label: "OpenClaw",
    icon: (
      <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
        <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
      </svg>
    ),
  },
  {
    id: "self-hosted",
    label: "Self-Hosted",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
      </svg>
    ),
  },
  {
    id: "notifications",
    label: "Notifications",
    icon: (
      <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
      </svg>
    ),
  },
];

const LANGUAGES = ["English", "Japanese", "Chinese", "Korean", "Spanish"];
const RESOLUTIONS = ["720p", "1080p", "4K"];
const STYLE_PRESETS = ["Anime (JJK)", "Anime (Ghibli)", "Realistic", "Cel-Shaded", "Watercolor", "Cyberpunk"];

/* ------------------------------------------------------------------ */
/*  Toggle Component                                                   */
/* ------------------------------------------------------------------ */

function Toggle({ enabled, onChange, label, description }: {
  enabled: boolean;
  onChange: (v: boolean) => void;
  label: string;
  description?: string;
}) {
  return (
    <div className="flex items-center justify-between py-3">
      <div>
        <p className="text-sm font-medium text-text-primary">{label}</p>
        {description && <p className="text-xs text-text-muted mt-0.5">{description}</p>}
      </div>
      <button
        type="button"
        onClick={() => onChange(!enabled)}
        className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors cursor-pointer ${
          enabled ? "bg-indigo" : "bg-void-lighter"
        }`}
      >
        <span
          className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
            enabled ? "translate-x-6" : "translate-x-1"
          }`}
        />
      </button>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Select Component                                                   */
/* ------------------------------------------------------------------ */

function Select({ value, onChange, options, label }: {
  value: string;
  onChange: (v: string) => void;
  options: readonly string[];
  label: string;
}) {
  return (
    <div>
      <label className="block text-sm font-medium text-text-primary mb-2">{label}</label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-3 rounded-xl bg-void-light border border-void-border text-text-primary focus:outline-none focus:border-indigo focus:ring-1 focus:ring-indigo/50 transition-all duration-200 cursor-pointer"
      >
        {options.map((opt) => (
          <option key={opt} value={opt}>{opt}</option>
        ))}
      </select>
    </div>
  );
}

/* ------------------------------------------------------------------ */
/*  Tab Content Components                                             */
/* ------------------------------------------------------------------ */

function ProfileTab() {
  const { user } = useAuth();
  const [name, setName] = useState(user?.name ?? "");
  const [email, setEmail] = useState(user?.email ?? "");
  const [saved, setSaved] = useState(false);

  const initial = (user?.name ?? "S").charAt(0).toUpperCase();

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Avatar Section */}
      <Card>
        <motion.div variants={fadeInUp} className="flex items-center gap-6">
          <div className="h-20 w-20 rounded-full bg-gradient-to-br from-indigo to-pink flex items-center justify-center text-3xl font-bold text-white shrink-0">
            {initial}
          </div>
          <div>
            <h3 className="text-lg font-semibold text-text-primary">{user?.name ?? "User"}</h3>
            <p className="text-sm text-text-muted mt-0.5">{user?.email ?? "user@synthos.ai"}</p>
            <Button variant="secondary" size="sm" className="mt-3">
              Change Avatar
            </Button>
          </div>
        </motion.div>
      </Card>

      {/* Edit Fields */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-5">
          <h3 className="text-lg font-semibold text-text-primary">Account Information</h3>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">Display Name</label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">Email Address</label>
            <Input type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="you@example.com" />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">Current Plan</label>
            <span className="inline-flex items-center rounded-full bg-indigo/20 px-3 py-1 text-sm font-medium text-indigo border border-indigo/30">
              {user?.plan ?? "Free"}
            </span>
          </div>
          <div className="flex items-center gap-3 pt-2">
            <Button onClick={handleSave}>
              {saved ? "Saved!" : "Save Changes"}
            </Button>
          </div>
        </motion.div>
      </Card>

      {/* Danger Zone */}
      <Card className="!border-red-500/30">
        <motion.div variants={fadeInUp}>
          <h3 className="text-lg font-semibold text-red-400">Danger Zone</h3>
          <p className="text-sm text-text-muted mt-1">
            Permanently delete your account and all associated data. This action cannot be undone.
          </p>
          <button
            type="button"
            className="mt-4 px-5 py-2.5 rounded-xl bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium hover:bg-red-500/20 transition-colors cursor-pointer"
          >
            Delete Account
          </button>
        </motion.div>
      </Card>
    </motion.div>
  );
}

function PreferencesTab() {
  const [theme, setTheme] = useState<"dark" | "light" | "system">("dark");
  const [language, setLanguage] = useState("English");
  const [resolution, setResolution] = useState("1080p");
  const [stylePreset, setStylePreset] = useState("Anime (JJK)");
  const [autoSave, setAutoSave] = useState(true);
  const [emailNotifs, setEmailNotifs] = useState(true);
  const [pushNotifs, setPushNotifs] = useState(false);

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Theme */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">Appearance</h3>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-3">Theme</label>
            <div className="flex gap-3">
              {(["dark", "light", "system"] as const).map((t) => (
                <button
                  key={t}
                  type="button"
                  onClick={() => setTheme(t)}
                  className={`px-5 py-2.5 rounded-xl text-sm font-medium border transition-all cursor-pointer capitalize ${
                    theme === t
                      ? "bg-indigo/20 border-indigo/50 text-indigo"
                      : "bg-void-lighter border-void-border text-text-secondary hover:border-indigo/30"
                  }`}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>
        </motion.div>
      </Card>

      {/* Language & Resolution */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-5">
          <h3 className="text-lg font-semibold text-text-primary">Production Defaults</h3>
          <Select label="Language" value={language} onChange={setLanguage} options={LANGUAGES} />
          <Select label="Default Resolution" value={resolution} onChange={setResolution} options={RESOLUTIONS} />
          <Select label="Default Style Preset" value={stylePreset} onChange={setStylePreset} options={STYLE_PRESETS} />
        </motion.div>
      </Card>

      {/* Toggles */}
      <Card>
        <motion.div variants={fadeInUp}>
          <h3 className="text-lg font-semibold text-text-primary mb-2">General</h3>
          <div className="divide-y divide-void-border">
            <Toggle label="Auto-Save" description="Automatically save project changes" enabled={autoSave} onChange={setAutoSave} />
            <Toggle label="Email Notifications" description="Receive updates via email" enabled={emailNotifs} onChange={setEmailNotifs} />
            <Toggle label="Push Notifications" description="Browser push notifications" enabled={pushNotifs} onChange={setPushNotifs} />
          </div>
        </motion.div>
      </Card>
    </motion.div>
  );
}

function APIKeysTab() {
  const [revealed, setRevealed] = useState(false);
  const [copied, setCopied] = useState(false);
  const [webhookUrl, setWebhookUrl] = useState("");

  const apiKey = "sk-synthos-a3f8b29c...d41e7f02";
  const fullKey = "sk-synthos-a3f8b29c4d5e6f7a8b9c0d1e2f3a4b5c6d41e7f02";

  const handleCopy = () => {
    navigator.clipboard.writeText(fullKey);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* API Key */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">API Key</h3>
          <p className="text-sm text-text-muted">
            Use this key to authenticate API requests. Keep it secret and never share it publicly.
          </p>
          <div className="flex items-center gap-3">
            <div className="flex-1 px-4 py-3 rounded-xl bg-void border border-void-border font-mono text-sm text-text-secondary">
              {revealed ? fullKey : apiKey}
            </div>
            <Button variant="secondary" size="sm" onClick={() => setRevealed(!revealed)}>
              {revealed ? "Hide" : "Reveal"}
            </Button>
          </div>
          <div className="flex gap-3">
            <Button variant="secondary" size="sm" onClick={handleCopy}>
              {copied ? "Copied!" : "Copy to Clipboard"}
            </Button>
            <Button size="sm">Generate New Key</Button>
          </div>
        </motion.div>
      </Card>

      {/* Usage Stats */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">API Usage</h3>
          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-sm text-text-secondary">API Calls This Month</p>
              <p className="text-sm font-semibold text-text-primary">1,247 <span className="text-text-muted">/ 10,000</span></p>
            </div>
            <div className="h-3 w-full overflow-hidden rounded-full bg-void">
              <motion.div
                className="h-full rounded-full bg-gradient-to-r from-indigo to-pink"
                initial={{ width: 0 }}
                animate={{ width: "12.47%" }}
                transition={{ duration: 1, ease: "easeOut", delay: 0.3 }}
              />
            </div>
            <p className="mt-1 text-right text-xs text-text-muted">12.5% used</p>
          </div>
          <div className="pt-2">
            <h4 className="text-sm font-medium text-text-primary mb-1">Rate Limits</h4>
            <div className="text-sm text-text-muted space-y-1">
              <p>100 requests / minute</p>
              <p>10,000 requests / month</p>
              <p>Max payload: 10 MB</p>
            </div>
          </div>
        </motion.div>
      </Card>

      {/* Webhook */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">Webhook</h3>
          <p className="text-sm text-text-muted">Receive POST notifications when renders complete or events occur.</p>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">Webhook URL</label>
            <Input value={webhookUrl} onChange={(e) => setWebhookUrl(e.target.value)} placeholder="https://your-server.com/webhook" />
          </div>
          <Button variant="secondary" size="sm">Save Webhook</Button>
        </motion.div>
      </Card>
    </motion.div>
  );
}

function OpenClawTab() {
  const [instanceUrl, setInstanceUrl] = useState("https://openclaw.local:8080");
  const [apiToken, setApiToken] = useState("");
  const [connectionStatus, setConnectionStatus] = useState<"disconnected" | "testing" | "connected">("connected");
  const [autoRestart, setAutoRestart] = useState(true);
  const [heartbeatInterval, setHeartbeatInterval] = useState("30");
  const [selectedModel, setSelectedModel] = useState("Claude Sonnet 4");

  const handleTestConnection = () => {
    setConnectionStatus("testing");
    setTimeout(() => setConnectionStatus("connected"), 2000);
  };

  const statusColors = {
    disconnected: "bg-red-500/20 text-red-400 border-red-500/30",
    testing: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    connected: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Engine Status */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center">
                <svg className="w-5 h-5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-text-primary">OpenClaw Engine</h3>
                <p className="text-xs text-text-muted">v{openClawStatus.version} &middot; Uptime: {openClawStatus.uptime}</p>
              </div>
            </div>
            <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium border ${statusColors[connectionStatus]}`}>
              <span className={`h-2 w-2 rounded-full ${connectionStatus === "connected" ? "bg-emerald-400 animate-pulse" : connectionStatus === "testing" ? "bg-amber-400 animate-pulse" : "bg-red-400"}`} />
              {connectionStatus === "connected" ? "Online" : connectionStatus === "testing" ? "Testing..." : "Offline"}
            </span>
          </div>
          <OpenClawMetricsBar accuracy={openClawMetrics.accuracy} consistency={openClawMetrics.consistency} speed={openClawMetrics.speed} />
          <div className="grid grid-cols-3 gap-4 pt-2">
            <div className="text-center p-3 rounded-xl bg-void border border-void-border">
              <p className="text-xs text-text-muted">Active Agents</p>
              <p className="text-lg font-bold text-emerald-400 mt-1">{openClawStatus.activeAgents}/{openClawStatus.totalAgents}</p>
            </div>
            <div className="text-center p-3 rounded-xl bg-void border border-void-border">
              <p className="text-xs text-text-muted">Tasks Completed</p>
              <p className="text-lg font-bold text-text-primary mt-1">{openClawMetrics.tasksCompleted.toLocaleString()}</p>
            </div>
            <div className="text-center p-3 rounded-xl bg-void border border-void-border">
              <p className="text-xs text-text-muted">Avg Response</p>
              <p className="text-lg font-bold text-[#818CF8] mt-1">{openClawMetrics.avgResponseTime}</p>
            </div>
          </div>
        </motion.div>
      </Card>

      {/* Connect Your Instance */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">Connect Your OpenClaw Instance</h3>
          <p className="text-sm text-text-muted">
            Connect your own self-hosted OpenClaw instance for full control over your AI automation pipeline.
          </p>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">Instance URL</label>
            <Input value={instanceUrl} onChange={(e) => setInstanceUrl(e.target.value)} placeholder="https://your-openclaw-instance:8080" />
          </div>
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">API Token</label>
            <Input type="password" value={apiToken} onChange={(e) => setApiToken(e.target.value)} placeholder="oc_token_xxxxxxxxxxxx" />
          </div>
          <div className="flex gap-3">
            <Button variant="secondary" size="sm" onClick={handleTestConnection}>
              Test Connection
            </Button>
            <Button size="sm">Save & Connect</Button>
          </div>
        </motion.div>
      </Card>

      {/* Heartbeat Scheduler */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">Heartbeat Scheduler</h3>
          <p className="text-sm text-text-muted">
            Configure the heartbeat scheduler for 24/7 autonomous operation. OpenClaw will keep agents alive and restart failed tasks automatically.
          </p>
          <div className="divide-y divide-void-border">
            <Toggle label="Auto-Restart Failed Tasks" description="Automatically restart agents that crash or timeout" enabled={autoRestart} onChange={setAutoRestart} />
          </div>
          <Select label="Heartbeat Interval (seconds)" value={heartbeatInterval} onChange={setHeartbeatInterval} options={["10", "15", "30", "60", "120"]} />
        </motion.div>
      </Card>

      {/* Model Selection */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">AI Model Configuration</h3>
          <p className="text-sm text-text-muted">
            OpenClaw is model-agnostic. Select the default model for your agents.
          </p>
          <Select label="Default Model" value={selectedModel} onChange={setSelectedModel} options={["Claude Sonnet 4", "Claude Opus 4", "GPT-4o", "Gemini 2.5 Pro", "Llama 4 Scout", "Custom / Local"]} />
        </motion.div>
      </Card>

      {/* Agent Overview */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">Agent Overview</h3>
          <p className="text-sm text-text-muted">All OpenClaw agents powering SYNTHOS features.</p>
          <div className="space-y-2">
            {openClawAgents.map((agent) => (
              <div key={agent.name} className="flex items-center justify-between p-3 rounded-xl bg-void border border-void-border hover:border-indigo/20 transition-colors">
                <div className="flex items-center gap-3">
                  <span className={`h-2 w-2 rounded-full ${agent.status === "active" || agent.status === "processing" ? "bg-emerald-400 animate-pulse" : agent.status === "idle" ? "bg-amber-400" : "bg-red-400"}`} />
                  <div>
                    <p className="text-sm font-medium text-text-primary">{agent.name}</p>
                    <p className="text-[10px] text-text-muted capitalize">{agent.status} &middot; {agent.tasksCompleted} tasks</p>
                  </div>
                </div>
                <div className="flex items-center gap-4 text-xs text-text-muted">
                  <span>Acc <span className="text-emerald-400 font-mono font-bold">{agent.accuracy}%</span></span>
                  <span>Spd <span className="text-[#F472B6] font-mono font-bold">{agent.speed}%</span></span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      </Card>
    </motion.div>
  );
}

function SelfHostedTab() {
  const [connectionStatus, setConnectionStatus] = useState<"disconnected" | "testing" | "connected">("disconnected");

  const handleTestConnection = () => {
    setConnectionStatus("testing");
    setTimeout(() => setConnectionStatus("connected"), 2000);
  };

  const dockerCompose = `version: "3.8"
services:
  synthos-engine:
    image: synthos/engine:latest
    runtime: nvidia
    ports:
      - "8090:8090"
    volumes:
      - ./models:/app/models
      - ./output:/app/output
    environment:
      - SYNTHOS_API_KEY=\${SYNTHOS_API_KEY}
      - CUDA_VISIBLE_DEVICES=0
    deploy:
      resources:
        reservations:
          devices:
            - capabilities: [gpu]

  synthos-web:
    image: synthos/web:latest
    ports:
      - "3000:3000"
    depends_on:
      - synthos-engine
    environment:
      - ENGINE_URL=http://synthos-engine:8090`;

  const statusColors = {
    disconnected: "bg-red-500/20 text-red-400 border-red-500/30",
    testing: "bg-amber-500/20 text-amber-400 border-amber-500/30",
    connected: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  };

  const statusLabels = {
    disconnected: "Disconnected",
    testing: "Testing...",
    connected: "Connected",
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      {/* Header */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-3">
          <div className="flex items-center gap-3">
            <h3 className="text-lg font-semibold text-text-primary">Sovereign Mode</h3>
            <span className="inline-flex items-center rounded-full bg-pink/20 px-2.5 py-0.5 text-xs font-medium text-pink border border-pink/30">
              Studio+
            </span>
          </div>
          <p className="text-sm text-text-muted">
            Run SYNTHOS on your own hardware. Your GPU, your data, your rules. Full Docker stack runs on a single RTX 3090/4090/5070.
          </p>

          {/* Connection Status */}
          <div className="flex items-center gap-3 pt-2">
            <span className={`inline-flex items-center gap-2 rounded-full px-3 py-1 text-xs font-medium border ${statusColors[connectionStatus]}`}>
              <span className={`h-2 w-2 rounded-full ${
                connectionStatus === "connected" ? "bg-emerald-400" :
                connectionStatus === "testing" ? "bg-amber-400 animate-pulse" :
                "bg-red-400"
              }`} />
              {statusLabels[connectionStatus]}
            </span>
            <Button variant="secondary" size="sm" onClick={handleTestConnection}>
              Test Connection
            </Button>
          </div>
        </motion.div>
      </Card>

      {/* Docker Setup */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">Docker Setup</h3>
          <p className="text-sm text-text-muted">Copy this docker-compose.yml to get started:</p>
          <div className="relative">
            <pre className="overflow-x-auto rounded-xl bg-void border border-void-border p-4 text-sm text-text-secondary font-mono leading-relaxed">
              {dockerCompose}
            </pre>
            <button
              type="button"
              onClick={() => navigator.clipboard.writeText(dockerCompose)}
              className="absolute top-3 right-3 px-3 py-1.5 rounded-lg bg-void-lighter border border-void-border text-xs text-text-muted hover:text-text-primary transition-colors cursor-pointer"
            >
              Copy
            </button>
          </div>
        </motion.div>
      </Card>

      {/* System Requirements */}
      <Card>
        <motion.div variants={fadeInUp} className="space-y-4">
          <h3 className="text-lg font-semibold text-text-primary">System Requirements</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-void-border">
                  <th className="py-3 px-4 text-left font-medium text-text-muted">Component</th>
                  <th className="py-3 px-4 text-left font-medium text-text-muted">Minimum</th>
                  <th className="py-3 px-4 text-left font-medium text-text-muted">Recommended</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-void-border">
                {[
                  ["GPU", "RTX 3090 (24 GB)", "RTX 4090 (24 GB)"],
                  ["CPU", "8-core / 16-thread", "16-core / 32-thread"],
                  ["RAM", "32 GB DDR4", "64 GB DDR5"],
                  ["Storage", "100 GB SSD", "500 GB NVMe SSD"],
                  ["OS", "Ubuntu 22.04 LTS", "Ubuntu 24.04 LTS"],
                  ["Docker", "24.0+", "25.0+"],
                  ["NVIDIA Driver", "535+", "550+"],
                ].map(([component, min, rec]) => (
                  <tr key={component} className="hover:bg-void-lighter/50 transition-colors">
                    <td className="py-3 px-4 font-medium text-text-primary">{component}</td>
                    <td className="py-3 px-4 text-text-secondary">{min}</td>
                    <td className="py-3 px-4 text-text-secondary">{rec}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </motion.div>
      </Card>
    </motion.div>
  );
}

function NotificationsTab() {
  const [renderComplete, setRenderComplete] = useState(true);
  const [pipelineUpdates, setPipelineUpdates] = useState(true);
  const [teamMentions, setTeamMentions] = useState(true);
  const [marketplaceUpdates, setMarketplaceUpdates] = useState(false);
  const [systemAnnouncements, setSystemAnnouncements] = useState(true);
  const [emailNotifications, setEmailNotifications] = useState(true);
  const [notificationSound, setNotificationSound] = useState(false);

  return (
    <motion.div
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="space-y-6"
    >
      <Card>
        <motion.div variants={fadeInUp}>
          <h3 className="text-lg font-semibold text-text-primary mb-2">Notification Preferences</h3>
          <p className="text-sm text-text-muted mb-4">Choose which notifications you want to receive.</p>
          <div className="divide-y divide-void-border">
            <Toggle
              label="Render Complete"
              description="Get notified when a render job finishes"
              enabled={renderComplete}
              onChange={setRenderComplete}
            />
            <Toggle
              label="Pipeline Updates"
              description="Updates about your production pipeline status"
              enabled={pipelineUpdates}
              onChange={setPipelineUpdates}
            />
            <Toggle
              label="Team Mentions"
              description="When a team member mentions you"
              enabled={teamMentions}
              onChange={setTeamMentions}
            />
            <Toggle
              label="Marketplace Updates"
              description="New workflows and assets in the marketplace"
              enabled={marketplaceUpdates}
              onChange={setMarketplaceUpdates}
            />
            <Toggle
              label="System Announcements"
              description="Important platform updates and maintenance notices"
              enabled={systemAnnouncements}
              onChange={setSystemAnnouncements}
            />
          </div>
        </motion.div>
      </Card>

      <Card>
        <motion.div variants={fadeInUp}>
          <h3 className="text-lg font-semibold text-text-primary mb-2">Delivery</h3>
          <div className="divide-y divide-void-border">
            <Toggle
              label="Email Notifications"
              description="Send notifications to your email address"
              enabled={emailNotifications}
              onChange={setEmailNotifications}
            />
            <Toggle
              label="Notification Sound"
              description="Play a sound for in-app notifications"
              enabled={notificationSound}
              onChange={setNotificationSound}
            />
          </div>
        </motion.div>
      </Card>
    </motion.div>
  );
}

/* ------------------------------------------------------------------ */
/*  Main Settings Page                                                 */
/* ------------------------------------------------------------------ */

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>("profile");

  const tabContent: Record<Tab, React.ReactNode> = {
    profile: <ProfileTab />,
    preferences: <PreferencesTab />,
    "api-keys": <APIKeysTab />,
    "openclaw": <OpenClawTab />,
    "self-hosted": <SelfHostedTab />,
    notifications: <NotificationsTab />,
  };

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
          <GradientText>Settings</GradientText>
        </h1>
        <p className="mt-1 text-text-secondary">Manage your account, preferences, and integrations.</p>
      </motion.div>

      {/* Tab Navigation */}
      <motion.div variants={fadeInUp} className="flex gap-1 overflow-x-auto rounded-xl bg-void-light/50 border border-void-border p-1.5">
        {TABS.map((tab) => (
          <button
            key={tab.id}
            type="button"
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 whitespace-nowrap rounded-lg px-4 py-2.5 text-sm font-medium transition-all cursor-pointer ${
              activeTab === tab.id
                ? "bg-indigo/20 text-indigo border border-indigo/30"
                : "text-text-muted hover:text-text-primary hover:bg-void-lighter border border-transparent"
            }`}
          >
            {tab.icon}
            {tab.label}
          </button>
        ))}
      </motion.div>

      {/* Tab Content */}
      <AnimatePresence mode="wait">
        <motion.div
          key={activeTab}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          transition={{ duration: 0.2 }}
        >
          {tabContent[activeTab]}
        </motion.div>
      </AnimatePresence>
    </motion.div>
  );
}
