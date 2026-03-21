"use client";

import { useEffect } from "react";
import { useAuth } from "@/contexts/AuthContext";
import Sidebar from "@/components/app/Sidebar";
import Topbar from "@/components/app/Topbar";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  useEffect(() => {
    if (!isLoading && !user) {
      const base = window.location.pathname.startsWith("/Pikaclaw")
        ? "/Pikaclaw"
        : "";
      window.location.href = base + "/login";
    }
  }, [user, isLoading]);

  if (isLoading || !user) {
    return (
      <div className="h-screen bg-[#0A0A0F] flex items-center justify-center">
        <div className="text-[#4F46E5] text-xl animate-pulse">
          Loading SYNTHOS...
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex bg-[#0A0A0F] overflow-hidden">
      <Sidebar />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Topbar />
        <main className="flex-1 overflow-y-auto p-6">{children}</main>
      </div>
    </div>
  );
}
