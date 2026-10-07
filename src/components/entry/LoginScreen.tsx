"use client";

import { useState } from "react";
import { NetworkOrb } from "@/components/shared/NetworkOrb";
import { Network, ArrowLeft, Eye, EyeOff, Loader2 } from "lucide-react";

export function LoginScreen({ onBack, onLogin }: { onBack: () => void, onLogin: () => void }) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    // Simulate auth check then always drop to demo
    setTimeout(() => {
      setLoading(false);
      onLogin();
    }, 1200);
  };

  return (
    <div className="fixed inset-0 bg-[#06080D] overflow-hidden flex flex-col items-center justify-center selection:bg-primary/30">
      {/* 3D Orb Background */}
      <div className="absolute inset-0 opacity-30 pointer-events-none mix-blend-screen scale-110">
        <NetworkOrb scale={1.5} />
      </div>
      <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px]" />

      <div className="relative z-10 w-full max-w-md px-6 animate-in fade-in zoom-in-95 duration-500">
        <button 
          onClick={onBack}
          className="mb-8 flex items-center gap-2 text-[13px] font-bold uppercase tracking-widest text-muted-foreground hover:text-foreground transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Welcome
        </button>

        <div className="glass-panel p-8 sm:p-10 rounded-2xl border border-white/10 shadow-[0_0_50px_rgba(0,0,0,0.5)] backdrop-blur-xl relative overflow-hidden">
          {/* Subtle gradient border highlight on top edge */}
          <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-white/30 to-transparent" />
          
          <div className="flex flex-col items-center mb-10">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-tr from-white/10 to-white/5 border border-white/10 flex items-center justify-center shadow-inner mb-5">
              <Network className="w-6 h-6 text-foreground" />
            </div>
            <h2 className="text-2xl font-bold tracking-wide text-foreground">Sign In</h2>
            <p className="text-sm text-muted-foreground mt-2 font-medium text-center">
              Authenticate to access the intelligence dashboard.
            </p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div className="space-y-1.5">
              <label className="text-[13px] font-bold uppercase tracking-widest text-muted-foreground ml-1">Email Address</label>
              <input 
                type="email"
                required
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full h-11 px-4 rounded-xl bg-black/40 border border-white/10 text-sm text-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all shadow-inner"
                placeholder="analyst@example.com"
              />
            </div>
            
            <div className="space-y-1.5">
              <div className="flex items-center justify-between ml-1 pr-1">
                <label className="text-[13px] font-bold uppercase tracking-widest text-muted-foreground">Password</label>
                <button type="button" className="text-[13px] font-bold text-primary/80 hover:text-primary transition-colors">Forgot?</button>
              </div>
              <div className="relative">
                <input 
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  className="w-full h-11 pl-4 pr-11 rounded-xl bg-black/40 border border-white/10 text-sm text-foreground focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all shadow-inner"
                  placeholder="••••••••"
                />
                <button 
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full h-11 mt-4 rounded-xl bg-primary text-primary-foreground font-bold tracking-wide hover:bg-primary/90 transition-all shadow-[0_0_15px_rgba(59,130,246,0.25)] flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed"
            >
              {loading ? <Loader2 className="w-5 h-5 animate-spin" /> : "Authenticate"}
            </button>
          </form>

          <div className="mt-8 pt-6 border-t border-white/5 text-center">
            <p className="text-[13px] text-muted-foreground font-medium mb-3">Don&apos;t have an account?</p>
            <button
              onClick={onLogin}
              className="w-full h-10 rounded-xl bg-white/5 border border-white/10 text-sm font-bold tracking-wide text-foreground hover:bg-white/10 transition-all"
            >
              Continue as Guest (Demo)
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
