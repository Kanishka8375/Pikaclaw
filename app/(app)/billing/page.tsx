"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";

interface Plan {
  name: string;
  price: string;
  period: string;
  features: string[];
  highlight: boolean;
  current: boolean;
}

const plans: Plan[] = [
  {
    name: "Free",
    price: "$0",
    period: "forever",
    features: [
      "1 project",
      "720p renders",
      "5 render hours/month",
      "5 GB storage",
      "Community support",
    ],
    highlight: false,
    current: false,
  },
  {
    name: "Creator",
    price: "$29",
    period: "/month",
    features: [
      "10 projects",
      "1080p renders",
      "50 render hours/month",
      "50 GB storage",
      "Priority support",
      "Marketplace access",
      "Multilingual (3 languages)",
    ],
    highlight: true,
    current: true,
  },
  {
    name: "Studio",
    price: "$99",
    period: "/month",
    features: [
      "Unlimited projects",
      "4K renders",
      "200 render hours/month",
      "500 GB storage",
      "Dedicated support",
      "API access",
      "Self-hosted option",
      "Multilingual (all languages)",
      "Team collaboration",
    ],
    highlight: false,
    current: false,
  },
  {
    name: "Enterprise",
    price: "Custom",
    period: "",
    features: [
      "Everything in Studio",
      "Unlimited render hours",
      "Custom model training",
      "SLA guarantee",
      "Dedicated account manager",
      "On-premise deployment",
      "Custom integrations",
    ],
    highlight: false,
    current: false,
  },
];

interface Invoice {
  id: string;
  date: string;
  amount: string;
  status: "paid" | "pending";
}

const invoices: Invoice[] = [
  { id: "INV-2026-003", date: "Mar 1, 2026", amount: "$29.00", status: "paid" },
  { id: "INV-2026-002", date: "Feb 1, 2026", amount: "$29.00", status: "paid" },
  { id: "INV-2026-001", date: "Jan 1, 2026", amount: "$29.00", status: "paid" },
];

export default function BillingPage() {
  const [billingCycle, setBillingCycle] = useState<"monthly" | "annual">("monthly");

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
          <GradientText>Billing</GradientText>
        </h1>
        <p className="mt-1 text-text-secondary">
          Manage your subscription and view invoices.
        </p>
      </motion.div>

      {/* Current Plan Summary */}
      <motion.div variants={fadeInUp}>
        <Card className="relative overflow-hidden">
          <div className="pointer-events-none absolute -right-8 -top-8 h-32 w-32 rounded-full bg-gradient-to-br from-[#4F46E5] to-[#EC4899] opacity-10 blur-3xl" />
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <p className="text-sm text-text-muted">Current Plan</p>
              <h2 className="text-2xl font-bold text-text-primary mt-1">
                Creator Plan
              </h2>
              <p className="text-sm text-text-secondary mt-0.5">
                $29/month &middot; Next billing date: Apr 1, 2026
              </p>
            </div>
            <div className="flex gap-3">
              <Button variant="secondary" size="sm">
                Cancel Plan
              </Button>
              <Button size="sm">Upgrade</Button>
            </div>
          </div>

          {/* Usage */}
          <div className="mt-6 grid grid-cols-2 gap-4 sm:grid-cols-4">
            {[
              { label: "Render Hours", used: 142, limit: 200, unit: "hrs" },
              { label: "Storage", used: 34, limit: 100, unit: "GB" },
              { label: "Projects", used: 12, limit: 50, unit: "" },
              { label: "API Calls", used: 1247, limit: 10000, unit: "" },
            ].map((meter) => (
              <div key={meter.label}>
                <p className="text-xs text-text-muted">{meter.label}</p>
                <p className="text-sm font-semibold text-text-primary mt-1">
                  {meter.used.toLocaleString()}
                  <span className="text-text-muted font-normal">
                    {" "}/ {meter.limit.toLocaleString()} {meter.unit}
                  </span>
                </p>
                <div className="mt-1.5 h-1.5 w-full overflow-hidden rounded-full bg-[#1E1E2E]">
                  <div
                    className="h-full rounded-full bg-gradient-to-r from-[#4F46E5] to-[#EC4899]"
                    style={{ width: `${(meter.used / meter.limit) * 100}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </Card>
      </motion.div>

      {/* Billing Cycle Toggle */}
      <motion.div variants={fadeInUp} className="flex items-center justify-center gap-3">
        <span className={`text-sm ${billingCycle === "monthly" ? "text-text-primary font-medium" : "text-text-muted"}`}>
          Monthly
        </span>
        <button
          onClick={() => setBillingCycle(billingCycle === "monthly" ? "annual" : "monthly")}
          className="relative inline-flex h-6 w-11 items-center rounded-full bg-void-lighter border border-void-border transition-colors cursor-pointer"
        >
          <span
            className={`inline-block h-4 w-4 transform rounded-full transition-transform ${
              billingCycle === "annual"
                ? "translate-x-6 bg-[#4F46E5]"
                : "translate-x-1 bg-text-muted"
            }`}
          />
        </button>
        <span className={`text-sm ${billingCycle === "annual" ? "text-text-primary font-medium" : "text-text-muted"}`}>
          Annual <span className="text-emerald-400 text-xs">Save 20%</span>
        </span>
      </motion.div>

      {/* Plans Grid */}
      <motion.div
        variants={staggerContainer}
        className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4"
      >
        {plans.map((plan) => (
          <Card
            key={plan.name}
            className={`flex flex-col ${
              plan.highlight ? "!border-[#4F46E5]/50 ring-1 ring-[#4F46E5]/20" : ""
            }`}
          >
            {plan.current && (
              <span className="inline-flex self-start rounded-full bg-[#4F46E5]/20 px-2.5 py-0.5 text-[10px] font-medium text-[#818CF8] border border-[#4F46E5]/30 mb-3">
                Current Plan
              </span>
            )}
            <h3 className="text-lg font-bold text-text-primary">{plan.name}</h3>
            <div className="mt-2">
              <span className="text-3xl font-bold text-text-primary">
                {billingCycle === "annual" && plan.price !== "$0" && plan.price !== "Custom"
                  ? `$${Math.round(parseInt(plan.price.replace("$", "")) * 0.8)}`
                  : plan.price}
              </span>
              <span className="text-sm text-text-muted">{plan.period}</span>
            </div>
            <ul className="mt-6 space-y-3 flex-1">
              {plan.features.map((feature) => (
                <li key={feature} className="flex items-start gap-2 text-sm text-text-secondary">
                  <svg className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                  </svg>
                  {feature}
                </li>
              ))}
            </ul>
            <div className="mt-6">
              {plan.current ? (
                <Button variant="secondary" size="md" className="w-full">
                  Current Plan
                </Button>
              ) : plan.name === "Enterprise" ? (
                <Button variant="secondary" size="md" className="w-full">
                  Contact Sales
                </Button>
              ) : (
                <Button size="md" className="w-full">
                  {parseInt(plan.price.replace("$", "")) > 29 ? "Upgrade" : "Downgrade"}
                </Button>
              )}
            </div>
          </Card>
        ))}
      </motion.div>

      {/* Invoices */}
      <motion.div variants={fadeInUp}>
        <Card hover={false} className="!p-0 overflow-hidden">
          <div className="border-b border-void-border px-6 py-4">
            <h2 className="text-lg font-semibold text-text-primary">Invoice History</h2>
          </div>
          <div className="divide-y divide-void-border">
            {invoices.map((inv) => (
              <div
                key={inv.id}
                className="flex items-center justify-between px-6 py-4 hover:bg-void-lighter/50 transition-colors"
              >
                <div>
                  <p className="text-sm font-medium text-text-primary">{inv.id}</p>
                  <p className="text-xs text-text-muted mt-0.5">{inv.date}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-sm font-semibold text-text-primary">{inv.amount}</span>
                  <span className="rounded-full bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 px-2.5 py-0.5 text-[10px] font-medium capitalize">
                    {inv.status}
                  </span>
                  <button className="text-xs text-[#818CF8] hover:text-[#4F46E5] transition-colors cursor-pointer">
                    Download
                  </button>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </motion.div>
    </motion.div>
  );
}
