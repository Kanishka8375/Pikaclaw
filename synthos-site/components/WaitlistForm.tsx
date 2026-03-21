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
      setStatus("success");
      setMessage("You're already on the list!");
      return;
    }

    stored.push(normalizedEmail);
    localStorage.setItem("synthos_waitlist", JSON.stringify(stored));

    setStatus("success");
    setMessage("You're on the list! We'll reach out soon.");
    setEmail("");
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
            if (status !== "idle" && status !== "loading") setStatus("idle");
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

      <AnimatePresence mode="wait">
        {(status === "success" || status === "error") && (
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className={`text-sm mt-3 text-center ${
              status === "success" ? "text-green-400" : "text-red-400"
            }`}
          >
            {message}
          </motion.p>
        )}
      </AnimatePresence>
    </div>
  );
}
