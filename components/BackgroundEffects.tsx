"use client";

import { motion } from "framer-motion";

export default function BackgroundEffects() {
  return (
    <div className="fixed inset-0 pointer-events-none overflow-hidden z-0">
      {/* Indigo orb - top left */}
      <motion.div
        animate={{
          x: [0, 30, -20, 0],
          y: [0, -20, 30, 0],
          scale: [1, 1.1, 0.95, 1],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute -top-40 -left-40 w-[500px] h-[500px] rounded-full bg-indigo/10 blur-[120px]"
      />

      {/* Pink orb - top right */}
      <motion.div
        animate={{
          x: [0, -40, 20, 0],
          y: [0, 30, -20, 0],
          scale: [1, 0.95, 1.1, 1],
        }}
        transition={{
          duration: 25,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute -top-20 -right-40 w-[400px] h-[400px] rounded-full bg-pink/8 blur-[100px]"
      />

      {/* Subtle indigo orb - middle */}
      <motion.div
        animate={{
          x: [0, 20, -30, 0],
          y: [0, -30, 20, 0],
        }}
        transition={{
          duration: 30,
          repeat: Infinity,
          ease: "easeInOut",
        }}
        className="absolute top-1/2 left-1/3 w-[300px] h-[300px] rounded-full bg-indigo/5 blur-[100px]"
      />

      {/* Grid overlay */}
      <div
        className="absolute inset-0 opacity-[0.03]"
        style={{
          backgroundImage:
            "linear-gradient(rgba(79, 70, 229, 0.3) 1px, transparent 1px), linear-gradient(90deg, rgba(79, 70, 229, 0.3) 1px, transparent 1px)",
          backgroundSize: "60px 60px",
        }}
      />
    </div>
  );
}
