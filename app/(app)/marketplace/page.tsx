"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import GradientText from "@/components/ui/GradientText";
import { staggerContainer, fadeInUp } from "@/lib/animations";
import { mockMarketplaceItems } from "@/lib/mock-data";
import type { MarketplaceItem } from "@/lib/types";

type CategoryFilter = MarketplaceItem["category"] | "all";

const categoryColors: Record<MarketplaceItem["category"], string> = {
  workflow: "bg-[#4F46E5]/20 text-[#818CF8] border border-[#4F46E5]/30",
  template: "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30",
  preset: "bg-violet-500/20 text-violet-400 border border-violet-500/30",
  character: "bg-amber-500/20 text-amber-400 border border-amber-500/30",
  soundtrack: "bg-[#EC4899]/20 text-[#F472B6] border border-[#EC4899]/30",
};

function StarRating({ rating }: { rating: number }) {
  return (
    <div className="flex items-center gap-0.5">
      {[1, 2, 3, 4, 5].map((star) => (
        <svg
          key={star}
          className={`w-3 h-3 ${
            star <= Math.round(rating) ? "text-amber-400" : "text-[#2A2A3E]"
          }`}
          fill="currentColor"
          viewBox="0 0 24 24"
        >
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
      ))}
      <span className="text-xs text-text-muted ml-1">{rating}</span>
    </div>
  );
}

export default function MarketplacePage() {
  const [filter, setFilter] = useState<CategoryFilter>("all");
  const [search, setSearch] = useState("");

  const filtered = mockMarketplaceItems.filter((item) => {
    const matchesCategory = filter === "all" || item.category === filter;
    const matchesSearch =
      !search ||
      item.name.toLowerCase().includes(search.toLowerCase()) ||
      item.description.toLowerCase().includes(search.toLowerCase()) ||
      item.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()));
    return matchesCategory && matchesSearch;
  });

  const categories: CategoryFilter[] = [
    "all",
    "workflow",
    "template",
    "preset",
    "character",
    "soundtrack",
  ];

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
          <GradientText>Marketplace</GradientText>
        </h1>
        <p className="mt-1 text-text-secondary">
          Discover workflows, templates, presets, and assets from the community.
        </p>
      </motion.div>

      {/* Search + Filters */}
      <motion.div variants={fadeInUp} className="space-y-4">
        <div className="flex items-center gap-2 px-4 py-3 rounded-xl bg-void-light border border-void-border focus-within:border-[#4F46E5]/50 transition-colors">
          <svg className="w-4 h-4 text-text-muted shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <circle cx="11" cy="11" r="7" />
            <path d="M21 21l-4.35-4.35" />
          </svg>
          <input
            type="text"
            placeholder="Search marketplace..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="flex-1 bg-transparent text-sm text-text-primary placeholder:text-text-muted focus:outline-none"
          />
        </div>

        <div className="flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setFilter(cat)}
              className={`cursor-pointer rounded-lg px-4 py-2 text-sm font-medium transition-all duration-200 capitalize ${
                filter === cat
                  ? "bg-gradient-to-r from-[#4F46E5] to-[#EC4899] text-white shadow-lg shadow-[#4F46E5]/20"
                  : "bg-void-light border border-void-border text-text-secondary hover:border-[#4F46E5]/30 hover:text-text-primary"
              }`}
            >
              {cat === "all" ? "All" : cat + "s"}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Items Grid */}
      <motion.div
        variants={staggerContainer}
        className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3"
      >
        {filtered.map((item) => (
          <Card key={item.id} className="flex flex-col">
            {/* Header */}
            <div className="flex items-start justify-between mb-3">
              <div className="min-w-0 flex-1">
                <h3 className="text-sm font-semibold text-text-primary truncate">
                  {item.name}
                </h3>
                <p className="text-xs text-text-muted mt-0.5">by {item.creator}</p>
              </div>
              <span
                className={`shrink-0 ml-3 rounded-full px-2.5 py-0.5 text-[10px] font-medium capitalize ${
                  categoryColors[item.category]
                }`}
              >
                {item.category}
              </span>
            </div>

            {/* Description */}
            <p className="text-xs text-text-secondary leading-relaxed line-clamp-3 flex-1">
              {item.description}
            </p>

            {/* Tags */}
            <div className="flex flex-wrap gap-1.5 mt-3">
              {item.tags.slice(0, 4).map((tag) => (
                <span
                  key={tag}
                  className="rounded-md bg-void-lighter px-2 py-0.5 text-[10px] text-text-muted"
                >
                  {tag}
                </span>
              ))}
            </div>

            {/* Footer */}
            <div className="mt-4 pt-4 border-t border-void-border flex items-center justify-between">
              <div className="space-y-1">
                <StarRating rating={item.rating} />
                <p className="text-xs text-text-muted">
                  {item.downloads.toLocaleString()} downloads
                </p>
              </div>
              <div className="text-right">
                <p className="text-lg font-bold text-text-primary">
                  {item.price === 0 ? (
                    <span className="text-emerald-400">Free</span>
                  ) : (
                    `$${item.price.toFixed(2)}`
                  )}
                </p>
                <Button variant="secondary" size="sm" className="mt-1">
                  {item.price === 0 ? "Install" : "Purchase"}
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </motion.div>

      {filtered.length === 0 && (
        <p className="py-12 text-center text-sm text-text-muted">
          No items match your search.
        </p>
      )}
    </motion.div>
  );
}
