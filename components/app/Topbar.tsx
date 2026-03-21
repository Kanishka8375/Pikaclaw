"use client";

import { useState, useRef, useEffect } from "react";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { motion, AnimatePresence } from "framer-motion";

const pageTitles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/projects": "Projects",
  "/pipeline": "Episode Pipeline",
  "/workflow": "Workflow Canvas",
  "/characters": "Character DNA Vault",
  "/world-atlas": "World Atlas",
  "/emotion": "Emotion Choreography",
  "/soundtrack": "Soundtrack Forge",
  "/render-queue": "Render Queue",
  "/bible": "Production Bible",
  "/marketplace": "Marketplace",
  "/trend-radar": "Trend Radar",
  "/multilingual": "Multilingual Engine",
  "/settings": "Settings",
  "/billing": "Billing",
};

export default function Topbar() {
  const pathname = usePathname();
  const { user, logout } = useAuth();
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const basePath = "";
  const relativePath = basePath ? pathname?.replace(basePath, "") : pathname;
  const pageTitle =
    pageTitles[relativePath || ""] ||
    relativePath
      ?.split("/")
      .filter(Boolean)
      .pop()
      ?.replace(/-/g, " ")
      .replace(/\b\w/g, (c) => c.toUpperCase()) ||
    "Dashboard";

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        setDropdownOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <header className="h-14 flex items-center justify-between px-6 border-b border-[#2A2A3E] bg-[#141420]/80 backdrop-blur-md flex-shrink-0">
      {/* Page title */}
      <div className="flex items-center gap-3">
        <h1 className="text-lg font-semibold text-[#E2E8F0] pl-10 lg:pl-0">
          {pageTitle}
        </h1>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* Search bar */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-[#1E1E2E] border border-[#2A2A3E] text-[#64748B] w-56 cursor-text hover:border-[#4F46E5]/40 transition-colors">
          <svg
            className="w-3.5 h-3.5 flex-shrink-0"
            viewBox="0 0 24 24"
            fill="none"
            strokeWidth={2}
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <circle cx="11" cy="11" r="7" />
            <path d="M21 21l-4.35-4.35" />
          </svg>
          <span className="text-xs">Search...</span>
          <kbd className="ml-auto text-[10px] px-1.5 py-0.5 rounded bg-[#0A0A0F] border border-[#2A2A3E] text-[#64748B] font-mono">
            /
          </kbd>
        </div>

        {/* Notification bell */}
        <button className="relative p-2 rounded-lg text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-[#1E1E2E] transition-colors">
          <svg
            className="w-4.5 h-4.5"
            viewBox="0 0 24 24"
            fill="none"
            strokeWidth={1.5}
            stroke="currentColor"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M18 8A6 6 0 006 8c0 7-3 9-3 9h18s-3-2-3-9" />
            <path d="M13.73 21a2 2 0 01-3.46 0" />
          </svg>
          <span className="absolute top-1.5 right-1.5 w-2 h-2 rounded-full bg-[#EC4899] ring-2 ring-[#141420]" />
        </button>

        {/* User dropdown */}
        <div className="relative" ref={dropdownRef}>
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="flex items-center gap-2 p-1.5 rounded-lg hover:bg-[#1E1E2E] transition-colors"
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#4F46E5] to-[#EC4899] flex items-center justify-center">
              <span className="text-white text-xs font-bold">
                {user?.name?.charAt(0)?.toUpperCase() ||
                  user?.email?.charAt(0)?.toUpperCase() ||
                  "S"}
              </span>
            </div>
            <svg
              className={`w-3 h-3 text-[#64748B] transition-transform ${dropdownOpen ? "rotate-180" : ""}`}
              viewBox="0 0 24 24"
              fill="none"
              strokeWidth={2}
              stroke="currentColor"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <path d="M6 9l6 6 6-6" />
            </svg>
          </button>

          <AnimatePresence>
            {dropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: -4, scale: 0.95 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -4, scale: 0.95 }}
                transition={{ duration: 0.15 }}
                className="absolute right-0 top-full mt-1.5 w-56 rounded-xl bg-[#1E1E2E] border border-[#2A2A3E] shadow-xl shadow-black/40 overflow-hidden z-50"
              >
                {/* User info */}
                <div className="px-4 py-3 border-b border-[#2A2A3E]">
                  <div className="text-sm font-medium text-[#E2E8F0] truncate">
                    {user?.name || "User"}
                  </div>
                  <div className="text-xs text-[#64748B] truncate mt-0.5">
                    {user?.email || "user@synthos.ai"}
                  </div>
                </div>

                {/* Menu items */}
                <div className="py-1.5">
                  <button
                    onClick={() => {
                      setDropdownOpen(false);
                      window.location.href = "/settings";
                    }}
                    className="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-[#141420] transition-colors"
                  >
                    <svg
                      className="w-3.5 h-3.5"
                      viewBox="0 0 24 24"
                      fill="none"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <circle cx="12" cy="12" r="3" />
                      <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
                    </svg>
                    Settings
                  </button>
                  <button
                    onClick={() => {
                      setDropdownOpen(false);
                      window.location.href = "/billing";
                    }}
                    className="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-[#141420] transition-colors"
                  >
                    <svg
                      className="w-3.5 h-3.5"
                      viewBox="0 0 24 24"
                      fill="none"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <rect x="2" y="4" width="20" height="16" rx="2" />
                      <path d="M2 10h20" />
                    </svg>
                    Billing
                  </button>
                </div>

                {/* Logout */}
                <div className="border-t border-[#2A2A3E] py-1.5">
                  <button
                    onClick={() => {
                      setDropdownOpen(false);
                      logout();
                    }}
                    className="w-full flex items-center gap-2.5 px-4 py-2 text-sm text-red-400 hover:text-red-300 hover:bg-[#141420] transition-colors"
                  >
                    <svg
                      className="w-3.5 h-3.5"
                      viewBox="0 0 24 24"
                      fill="none"
                      strokeWidth={1.5}
                      stroke="currentColor"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                    >
                      <path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" />
                      <polyline points="16 17 21 12 16 7" />
                      <line x1="21" y1="12" x2="9" y2="12" />
                    </svg>
                    Log out
                  </button>
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </header>
  );
}
