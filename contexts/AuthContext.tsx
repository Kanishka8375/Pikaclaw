"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import type { User } from "@/lib/types";

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<boolean>;
  signup: (
    name: string,
    email: string,
    password: string,
  ) => Promise<boolean>;
  logout: () => void;
  updateUser: (updates: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | null>(null);

const DEMO_USER: User = {
  id: "usr_001",
  name: "Demo Creator",
  email: "demo@synthos.ai",
  avatar: "",
  plan: "creator",
  createdAt: "2026-01-15",
};

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const stored = localStorage.getItem("synthos_user");
    if (stored) {
      setUser(JSON.parse(stored));
    }
    setIsLoading(false);
  }, []);

  function persistUser(u: User | null) {
    if (u) {
      localStorage.setItem("synthos_user", JSON.stringify(u));
    } else {
      localStorage.removeItem("synthos_user");
    }
    setUser(u);
  }

  async function login(
    email: string,
    _password: string,
  ): Promise<boolean> {
    // Simulated auth - accept any valid email
    const u: User = {
      ...DEMO_USER,
      email,
      name: email.split("@")[0],
      id: "usr_" + Date.now(),
    };
    persistUser(u);
    return true;
  }

  async function signup(
    name: string,
    email: string,
    _password: string,
  ): Promise<boolean> {
    const u: User = {
      ...DEMO_USER,
      name,
      email,
      id: "usr_" + Date.now(),
    };
    persistUser(u);
    return true;
  }

  function logout() {
    persistUser(null);
  }

  function updateUser(updates: Partial<User>) {
    if (user) {
      persistUser({ ...user, ...updates });
    }
  }

  return (
    <AuthContext.Provider
      value={{ user, isLoading, login, signup, logout, updateUser }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
