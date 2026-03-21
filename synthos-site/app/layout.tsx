import type { Metadata } from "next";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";

export const metadata: Metadata = {
  title: "SYNTHOS — Autonomous Storytelling Engine",
  description:
    "The world's first AI-native production studio. Transform a single story brief into fully produced episodes with consistent characters, locations, music, and voice across unlimited episodes.",
  keywords: [
    "AI video generation",
    "autonomous storytelling",
    "anime production",
    "AI series creator",
    "video production SaaS",
  ],
  openGraph: {
    title: "SYNTHOS — Autonomous Storytelling Engine",
    description:
      "Synthesize stories. Ship scenes. Scale everything. The AI production studio that remembers.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>
        <AuthProvider>{children}</AuthProvider>
      </body>
    </html>
  );
}
