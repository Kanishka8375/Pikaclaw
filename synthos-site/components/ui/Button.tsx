"use client";

import { motion } from "framer-motion";

interface ButtonProps {
  children: React.ReactNode;
  onClick?: () => void;
  type?: "button" | "submit";
  disabled?: boolean;
  variant?: "primary" | "secondary";
  size?: "sm" | "md" | "lg";
  className?: string;
}

export default function Button({
  children,
  onClick,
  type = "button",
  disabled = false,
  variant = "primary",
  size = "md",
  className = "",
}: ButtonProps) {
  const sizeClasses = {
    sm: "px-4 py-2 text-sm",
    md: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg",
  };

  const variantClasses = {
    primary:
      "bg-gradient-to-r from-indigo to-pink text-white hover:shadow-[0_0_30px_rgba(79,70,229,0.4)]",
    secondary:
      "bg-void-lighter text-text-primary border border-void-border hover:border-indigo/50",
  };

  return (
    <motion.button
      type={type}
      onClick={onClick}
      disabled={disabled}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      className={`
        ${sizeClasses[size]}
        ${variantClasses[variant]}
        rounded-xl font-medium transition-all duration-300
        disabled:opacity-50 disabled:cursor-not-allowed
        cursor-pointer
        ${className}
      `}
    >
      {children}
    </motion.button>
  );
}
