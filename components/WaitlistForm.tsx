"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";

interface WaitlistFormProps {
  source?: string;
  className?: string;
}

export default function WaitlistForm({
  source: _source = "landing",
  className = "",
}: WaitlistFormProps) {
  const [email, setEmail] = useState("");
  const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");
  const [message, setMessage] = useState("");
  const [submittedEmail, setSubmittedEmail] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email || status === "loading") return;

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setStatus("error");
      setMessage("Please enter a valid email address.");
      return;
    }

    setStatus("loading");

    // Client-side storage for static deployment
    const stored = JSON.parse(localStorage.getItem("synthos_waitlist") || "[]");
    const normalizedEmail = email.toLowerCase().trim();

    if (stored.includes(normalizedEmail)) {
      setSubmittedEmail(normalizedEmail);
      setStatus("success");
      setMessage("You're already on the list!");
      return;
    }

    stored.push(normalizedEmail);
    localStorage.setItem("synthos_waitlist", JSON.stringify(stored));

    setSubmittedEmail(normalizedEmail);
    setStatus("success");
    setMessage("You're on the list! We'll reach out soon.");
    setEmail("");
  }

  function handleDismiss() {
    setStatus("idle");
    setMessage("");
    setSubmittedEmail("");
  }

  return (
    <div className={className}>
      <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3 max-w-md mx-auto">
        <Input
          type="email"
          placeholder="you@example.com"
          value={email}
          onChange={(e) => {
            setEmail(e.target.value);
            if (status === "error") {
              setStatus("idle");
              setMessage("");
            }
          }}
          required
          className="flex-1"
        />
        <Button
          type="submit"
          disabled={status === "loading"}
          size="md"
        >
          {status === "loading" ? "Joining..." : "Join Waitlist"}
        </Button>
      </form>

      {/* Inline error message */}
      <AnimatePresence mode="wait">
        {status === "error" && (
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="text-sm mt-3 text-center text-red-400"
          >
            {message}
          </motion.p>
        )}
      </AnimatePresence>

      {/* Success popup overlay */}
      <AnimatePresence>
        {status === "success" && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 backdrop-blur-sm"
            onClick={handleDismiss}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.8, y: 30 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.8, y: 30 }}
              transition={{ type: "spring", damping: 20, stiffness: 300 }}
              className="relative bg-gradient-to-br from-gray-900 to-gray-800 border border-indigo-500/30 rounded-2xl p-8 max-w-sm mx-4 text-center shadow-2xl shadow-indigo-500/20"
              onClick={(e) => e.stopPropagation()}
            >
              {/* Checkmark icon */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring", damping: 12, stiffness: 200 }}
                className="w-16 h-16 mx-auto mb-4 rounded-full bg-green-500/20 border-2 border-green-400 flex items-center justify-center"
              >
                <svg className="w-8 h-8 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={3}>
                  <motion.path
                    initial={{ pathLength: 0 }}
                    animate={{ pathLength: 1 }}
                    transition={{ delay: 0.4, duration: 0.4 }}
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    d="M5 13l4 4L19 7"
                  />
                </svg>
              </motion.div>

              <h3 className="text-xl font-bold text-white mb-2">
                {message === "You're already on the list!" ? "Already Registered!" : "You're In!"}
              </h3>

              <p className="text-gray-300 text-sm mb-2">
                {message}
              </p>

              <p className="text-indigo-400 text-sm font-medium mb-5">
                {submittedEmail}
              </p>

              <p className="text-gray-400 text-xs mb-6">
                We&apos;ll send you an email with early access details when SYNTHOS launches. Stay tuned!
              </p>

              <button
                onClick={handleDismiss}
                className="px-6 py-2.5 bg-indigo-600 hover:bg-indigo-500 text-white rounded-lg font-medium transition-colors text-sm"
              >
                Got it!
              </button>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
