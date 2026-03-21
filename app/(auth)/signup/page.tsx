"use client";

import { useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { useAuth } from "@/contexts/AuthContext";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import GradientText from "@/components/ui/GradientText";

export default function SignupPage() {
  const { signup, isLoading } = useAuth();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    try {
      await signup(name, email, password);
      const base =
        typeof window !== "undefined" &&
        window.location.pathname.startsWith("/Pikaclaw")
          ? "/Pikaclaw"
          : "";
      window.location.href = base + "/dashboard";
    } catch (err: unknown) {
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError("Something went wrong. Please try again.");
      }
    }
  };

  const fields = [
    {
      label: "Full Name",
      type: "text",
      placeholder: "John Doe",
      value: name,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setName(e.target.value),
    },
    {
      label: "Email",
      type: "email",
      placeholder: "you@example.com",
      value: email,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setEmail(e.target.value),
    },
    {
      label: "Password",
      type: "password",
      placeholder: "At least 8 characters",
      value: password,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setPassword(e.target.value),
    },
    {
      label: "Confirm Password",
      type: "password",
      placeholder: "Re-enter your password",
      value: confirmPassword,
      onChange: (e: React.ChangeEvent<HTMLInputElement>) =>
        setConfirmPassword(e.target.value),
    },
  ];

  return (
    <div className="min-h-screen bg-void flex items-center justify-center px-4 py-12">
      {/* Background glow effects */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-1/3 right-1/3 w-96 h-96 bg-pink/5 rounded-full blur-3xl" />
        <div className="absolute bottom-1/3 left-1/3 w-96 h-96 bg-indigo/5 rounded-full blur-3xl" />
      </div>

      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="relative w-full max-w-md"
      >
        {/* Card */}
        <div className="bg-void-light/80 backdrop-blur-xl border border-void-border rounded-2xl p-8 shadow-2xl shadow-black/20">
          {/* Logo / Brand */}
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.5 }}
            className="text-center mb-8"
          >
            <Link href="/" className="inline-block">
              <h1 className="text-3xl font-bold tracking-tight">
                <GradientText>SYNTHOS</GradientText>
              </h1>
            </Link>
            <p className="text-text-secondary mt-2 text-sm">
              Create your account to get started.
            </p>
          </motion.div>

          {/* Error message */}
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              className="mb-4 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center"
            >
              {error}
            </motion.div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {fields.map((field, index) => (
              <motion.div
                key={field.label}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.25 + index * 0.1, duration: 0.4 }}
              >
                <label className="block text-text-secondary text-sm font-medium mb-1.5">
                  {field.label}
                </label>
                <Input
                  type={field.type}
                  placeholder={field.placeholder}
                  value={field.value}
                  onChange={field.onChange}
                  required
                />
              </motion.div>
            ))}

            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7, duration: 0.4 }}
              className="pt-1"
            >
              <Button
                type="submit"
                disabled={isLoading}
                className="w-full"
                size="lg"
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <svg
                      className="animate-spin h-5 w-5"
                      viewBox="0 0 24 24"
                      fill="none"
                    >
                      <circle
                        className="opacity-25"
                        cx="12"
                        cy="12"
                        r="10"
                        stroke="currentColor"
                        strokeWidth="4"
                      />
                      <path
                        className="opacity-75"
                        fill="currentColor"
                        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
                      />
                    </svg>
                    Creating account...
                  </span>
                ) : (
                  "Create Account"
                )}
              </Button>
            </motion.div>
          </form>

          {/* Terms notice */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.8, duration: 0.4 }}
            className="mt-4 text-center text-text-secondary/60 text-xs leading-relaxed"
          >
            By creating an account, you agree to our{" "}
            <span className="text-text-secondary hover:text-text-primary cursor-pointer transition-colors">
              Terms of Service
            </span>{" "}
            and{" "}
            <span className="text-text-secondary hover:text-text-primary cursor-pointer transition-colors">
              Privacy Policy
            </span>
            .
          </motion.p>

          {/* Divider */}
          <div className="my-6 flex items-center gap-3">
            <div className="flex-1 h-px bg-void-border" />
            <span className="text-text-secondary text-xs uppercase tracking-wider">
              or
            </span>
            <div className="flex-1 h-px bg-void-border" />
          </div>

          {/* Login link */}
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.9, duration: 0.4 }}
            className="text-center text-text-secondary text-sm"
          >
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-indigo hover:text-indigo-light font-medium transition-colors"
            >
              Log in
            </Link>
          </motion.p>
        </div>
      </motion.div>
    </div>
  );
}
