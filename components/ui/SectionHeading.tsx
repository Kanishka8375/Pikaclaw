"use client";

import { motion } from "framer-motion";
import { fadeInUp } from "@/lib/animations";
import GradientText from "./GradientText";

interface SectionHeadingProps {
  title: string;
  subtitle?: string;
  gradient?: boolean;
  className?: string;
}

export default function SectionHeading({
  title,
  subtitle,
  gradient = true,
  className = "",
}: SectionHeadingProps) {
  return (
    <motion.div
      variants={fadeInUp}
      initial="hidden"
      whileInView="visible"
      viewport={{ once: true, margin: "-100px" }}
      className={`text-center mb-16 ${className}`}
    >
      <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold font-display mb-4">
        {gradient ? <GradientText>{title}</GradientText> : title}
      </h2>
      {subtitle && (
        <p className="text-text-secondary text-lg md:text-xl max-w-2xl mx-auto">
          {subtitle}
        </p>
      )}
    </motion.div>
  );
}
