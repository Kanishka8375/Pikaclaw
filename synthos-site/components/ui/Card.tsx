"use client";

import { motion } from "framer-motion";
import { fadeInUp } from "@/lib/animations";

interface CardProps {
  children: React.ReactNode;
  className?: string;
  hover?: boolean;
}

export default function Card({
  children,
  className = "",
  hover = true,
}: CardProps) {
  return (
    <motion.div
      variants={fadeInUp}
      className={`
        rounded-2xl p-6
        bg-void-light/50 border border-void-border
        backdrop-blur-sm
        ${hover ? "hover:border-indigo/30 hover:bg-void-light/80 transition-all duration-300" : ""}
        ${className}
      `}
    >
      {children}
    </motion.div>
  );
}
