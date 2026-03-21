"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { motion, AnimatePresence } from "framer-motion";

interface NavItem {
  label: string;
  href: string;
  icon: React.ReactNode;
}

interface NavSection {
  title: string;
  items: NavItem[];
}

const iconClass = "w-4 h-4 stroke-current";

const sections: NavSection[] = [
  {
    title: "OVERVIEW",
    items: [
      {
        label: "Dashboard",
        href: "/dashboard",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <rect x="3" y="3" width="7" height="7" rx="1" />
            <rect x="14" y="3" width="7" height="7" rx="1" />
            <rect x="3" y="14" width="7" height="7" rx="1" />
            <rect x="14" y="14" width="7" height="7" rx="1" />
          </svg>
        ),
      },
    ],
  },
  {
    title: "PRODUCTION",
    items: [
      {
        label: "Projects",
        href: "/projects",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 7V17C3 18.1 3.9 19 5 19H19C20.1 19 21 18.1 21 17V9C21 7.9 20.1 7 19 7H13L11 5H5C3.9 5 3 5.9 3 7Z" />
          </svg>
        ),
      },
      {
        label: "Episode Pipeline",
        href: "/pipeline",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 6h16M4 12h16M4 18h16" />
            <circle cx="8" cy="6" r="1.5" fill="currentColor" />
            <circle cx="14" cy="12" r="1.5" fill="currentColor" />
            <circle cx="10" cy="18" r="1.5" fill="currentColor" />
          </svg>
        ),
      },
      {
        label: "Workflow Canvas",
        href: "/workflow",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <circle cx="6" cy="6" r="2" />
            <circle cx="18" cy="6" r="2" />
            <circle cx="12" cy="18" r="2" />
            <path d="M8 6h8M6 8l6 8M18 8l-6 8" />
          </svg>
        ),
      },
    ],
  },
  {
    title: "CREATIVE",
    items: [
      {
        label: "Character DNA Vault",
        href: "/characters",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="8" r="4" />
            <path d="M6 21v-2a4 4 0 014-4h4a4 4 0 014 4v2" />
          </svg>
        ),
      },
      {
        label: "World Atlas",
        href: "/world-atlas",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="9" />
            <path d="M3.6 9h16.8M3.6 15h16.8" />
            <ellipse cx="12" cy="12" rx="4" ry="9" />
          </svg>
        ),
      },
      {
        label: "Emotion Choreography",
        href: "/emotion",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 21C12 21 4 15 4 9.5C4 6.46 6.46 4 9.5 4C11.06 4 12 5 12 5C12 5 12.94 4 14.5 4C17.54 4 20 6.46 20 9.5C20 15 12 21 12 21Z" />
          </svg>
        ),
      },
    ],
  },
  {
    title: "TOOLS",
    items: [
      {
        label: "Soundtrack Forge",
        href: "/soundtrack",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <path d="M9 18V5l12-2v13" />
            <circle cx="6" cy="18" r="3" />
            <circle cx="18" cy="16" r="3" />
          </svg>
        ),
      },
      {
        label: "Render Queue",
        href: "/render-queue",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="3" width="20" height="14" rx="2" />
            <path d="M8 21h8M12 17v4" />
            <path d="M10 9l4 2-4 2V9Z" fill="currentColor" />
          </svg>
        ),
      },
      {
        label: "Production Bible",
        href: "/bible",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <path d="M4 19.5A2.5 2.5 0 016.5 17H20" />
            <path d="M4 4.5A2.5 2.5 0 016.5 2H20v20H6.5A2.5 2.5 0 014 19.5v-15Z" />
            <path d="M8 7h8M8 11h6" />
          </svg>
        ),
      },
    ],
  },
  {
    title: "DISCOVER",
    items: [
      {
        label: "Marketplace",
        href: "/marketplace",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <path d="M3 9l1.5-5h15L21 9" />
            <path d="M3 9h18v11a1 1 0 01-1 1H4a1 1 0 01-1-1V9Z" />
            <path d="M9 9v3a3 3 0 006 0V9" />
          </svg>
        ),
      },
      {
        label: "Trend Radar",
        href: "/trend-radar",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="9" />
            <circle cx="12" cy="12" r="5" />
            <circle cx="12" cy="12" r="1" />
            <path d="M12 3v4M12 17v4M3 12h4M17 12h4" />
          </svg>
        ),
      },
      {
        label: "Multilingual Engine",
        href: "/multilingual",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <path d="M5 8l6 6M4 14l6-6M2 5h12M7 2v3" />
            <path d="M14 14l3 8 3-8M15 18h4" />
          </svg>
        ),
      },
    ],
  },
  {
    title: "ACCOUNT",
    items: [
      {
        label: "Settings",
        href: "/settings",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="3" />
            <path d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42" />
          </svg>
        ),
      },
      {
        label: "Billing",
        href: "/billing",
        icon: (
          <svg className={iconClass} viewBox="0 0 24 24" fill="none" strokeWidth={1.5} strokeLinecap="round" strokeLinejoin="round">
            <rect x="2" y="4" width="20" height="16" rx="2" />
            <path d="M2 10h20" />
            <path d="M6 16h4" />
          </svg>
        ),
      },
    ],
  },
];

export default function Sidebar() {
  const pathname = usePathname();
  const { user } = useAuth();
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const basePath = pathname?.startsWith("/Pikaclaw") ? "/Pikaclaw" : "";

  const isActive = (href: string) => {
    const fullPath = basePath + href;
    return pathname === fullPath || pathname?.startsWith(fullPath + "/");
  };

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center justify-between px-4 py-5 border-b border-[#2A2A3E]">
        <Link href={basePath + "/dashboard"} className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#4F46E5] to-[#EC4899] flex items-center justify-center">
            <svg className="w-4 h-4 text-white" viewBox="0 0 24 24" fill="none" strokeWidth={2} stroke="currentColor" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
            </svg>
          </div>
          {!collapsed && (
            <motion.span
              initial={{ opacity: 0, width: 0 }}
              animate={{ opacity: 1, width: "auto" }}
              exit={{ opacity: 0, width: 0 }}
              className="text-[#E2E8F0] font-bold text-lg tracking-tight"
            >
              SYNTHOS
            </motion.span>
          )}
        </Link>
        {/* Collapse button - desktop only */}
        <button
          onClick={() => setCollapsed(!collapsed)}
          className="hidden lg:flex items-center justify-center w-6 h-6 rounded-md text-[#64748B] hover:text-[#E2E8F0] hover:bg-[#1E1E2E] transition-colors"
        >
          <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" strokeWidth={2} stroke="currentColor" strokeLinecap="round" strokeLinejoin="round">
            {collapsed ? (
              <path d="M9 18l6-6-6-6" />
            ) : (
              <path d="M15 18l-6-6 6-6" />
            )}
          </svg>
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto px-3 py-4 space-y-6 scrollbar-thin">
        {sections.map((section) => (
          <div key={section.title}>
            {!collapsed && (
              <div className="px-3 mb-2 text-[10px] font-semibold tracking-widest text-[#64748B] uppercase">
                {section.title}
              </div>
            )}
            <div className="space-y-0.5">
              {section.items.map((item) => {
                const active = isActive(item.href);
                return (
                  <Link
                    key={item.href}
                    href={basePath + item.href}
                    onClick={() => setMobileOpen(false)}
                    className={`
                      group flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium
                      transition-all duration-150 relative
                      ${
                        active
                          ? "bg-[#4F46E5]/15 text-[#E2E8F0]"
                          : "text-[#94A3B8] hover:text-[#E2E8F0] hover:bg-[#1E1E2E]"
                      }
                    `}
                  >
                    {active && (
                      <motion.div
                        layoutId="sidebar-active"
                        className="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 rounded-r-full bg-[#4F46E5]"
                        transition={{ type: "spring", stiffness: 350, damping: 30 }}
                      />
                    )}
                    <span
                      className={`flex-shrink-0 ${
                        active ? "text-[#4F46E5]" : "text-[#64748B] group-hover:text-[#94A3B8]"
                      } transition-colors`}
                    >
                      {item.icon}
                    </span>
                    {!collapsed && (
                      <span className="truncate">{item.label}</span>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </nav>

      {/* OpenClaw Status */}
      <div className="border-t border-[#2A2A3E] px-3 py-3">
        <Link
          href={basePath + "/settings"}
          onClick={() => setMobileOpen(false)}
          className="flex items-center gap-2.5 px-2 py-2 rounded-lg hover:bg-[#1E1E2E] transition-colors group"
        >
          <div className="w-6 h-6 rounded-md bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center flex-shrink-0">
            <svg className="w-3 h-3 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" />
            </svg>
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-1.5">
                <span className="text-xs font-medium text-emerald-400">OpenClaw</span>
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse" />
              </div>
              <p className="text-[10px] text-[#64748B] mt-0.5">12 agents active</p>
            </div>
          )}
        </Link>
      </div>

      {/* User section */}
      <div className="border-t border-[#2A2A3E] px-3 py-4">
        <div className={`flex items-center ${collapsed ? "justify-center" : "gap-3 px-2"}`}>
          <div className="w-8 h-8 rounded-full bg-gradient-to-br from-[#4F46E5] to-[#EC4899] flex items-center justify-center flex-shrink-0">
            <span className="text-white text-xs font-bold">
              {user?.name?.charAt(0)?.toUpperCase() || user?.email?.charAt(0)?.toUpperCase() || "S"}
            </span>
          </div>
          {!collapsed && (
            <div className="flex-1 min-w-0">
              <div className="text-sm font-medium text-[#E2E8F0] truncate">
                {user?.name || user?.email?.split("@")[0] || "User"}
              </div>
              <div className="flex items-center gap-1.5 mt-0.5">
                <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] font-semibold bg-[#4F46E5]/20 text-[#4F46E5] tracking-wide">
                  PRO
                </span>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return (
    <>
      {/* Mobile hamburger */}
      <button
        onClick={() => setMobileOpen(true)}
        className="lg:hidden fixed top-4 left-4 z-50 p-2 rounded-lg bg-[#141420] border border-[#2A2A3E] text-[#94A3B8] hover:text-[#E2E8F0] transition-colors"
      >
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" strokeWidth={1.5} stroke="currentColor" strokeLinecap="round">
          <path d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      {/* Mobile overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setMobileOpen(false)}
            className="lg:hidden fixed inset-0 z-40 bg-black/60 backdrop-blur-sm"
          />
        )}
      </AnimatePresence>

      {/* Mobile sidebar */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.aside
            initial={{ x: -280 }}
            animate={{ x: 0 }}
            exit={{ x: -280 }}
            transition={{ type: "spring", stiffness: 300, damping: 30 }}
            className="lg:hidden fixed inset-y-0 left-0 z-50 w-[260px] bg-[#141420] border-r border-[#2A2A3E]"
          >
            {/* Close button */}
            <button
              onClick={() => setMobileOpen(false)}
              className="absolute top-4 right-3 p-1 rounded-md text-[#64748B] hover:text-[#E2E8F0] hover:bg-[#1E1E2E] transition-colors"
            >
              <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" strokeWidth={2} stroke="currentColor" strokeLinecap="round">
                <path d="M18 6L6 18M6 6l12 12" />
              </svg>
            </button>
            {sidebarContent}
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Desktop sidebar */}
      <motion.aside
        animate={{ width: collapsed ? 68 : 260 }}
        transition={{ type: "spring", stiffness: 300, damping: 30 }}
        className="hidden lg:flex flex-col bg-[#141420] border-r border-[#2A2A3E] overflow-hidden flex-shrink-0"
      >
        {sidebarContent}
      </motion.aside>
    </>
  );
}
