"use client";

import { useEffect, useState } from "react";
import { NetworkOrb } from "@/components/shared/NetworkOrb";
import { Network, ArrowRight, PlayCircle } from "lucide-react";

export function WelcomeScreen({ onEnter, onLogin }: { onEnter: () => void, onLogin: () => void }) {
  const [mounted, setMounted] = useState(false);

  useEffect(() => {
    setMounted(true);
  }, []);

  return (
    <div className="fixed inset-0 bg-[#06080D] overflow-hidden flex flex-col selection:bg-primary/30">
      {/* Cinematic backgrounds */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top_right,rgba(6,182,212,0.1)_0%,transparent_50%)]" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom_left,rgba(59,130,246,0.15)_0%,transparent_50%)]" />
      <div className="absolute inset-0 tech-grid opacity-20 mask-radial-fade" />
      
      {/* 3D Orb Positioned Off-Center */}
      <div className="absolute top-[-10%] right-[-15%] w-[80%] h-[120%] opacity-80 pointer-events-none mix-blend-screen hidden md:block">
        <NetworkOrb scale={1.8} />
      </div>
      <div className="absolute top-[10%] right-[-30%] w-[120%] h-[120%] opacity-40 pointer-events-none mix-blend-screen md:hidden">
        <NetworkOrb scale={1.2} />
      </div>

      {/* Top Bar */}
      <header className={`relative z-10 flex items-center justify-between px-8 py-6 transition-all duration-1000 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4'}`}>
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 rounded-lg bg-white/5 border border-white/10 flex items-center justify-center backdrop-blur-md shadow-[0_0_15px_rgba(255,255,255,0.05)]">
            <Network className="w-4 h-4 text-foreground" />
          </div>
          <span className="font-bold text-[17px] tracking-wide text-foreground">NetAnalyzer</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-500/20 backdrop-blur-md">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse shadow-[0_0_8px_rgba(52,211,153,0.8)]" />
          <span className="text-[12px] font-bold uppercase tracking-widest text-emerald-400">System Ready</span>
        </div>
      </header>

      {/* Main Content Area */}
      <main className="relative z-10 flex-1 flex flex-col justify-center px-8 md:px-24 max-w-7xl mx-auto w-full">
        <div className={`max-w-2xl transition-all duration-1000 delay-300 ${mounted ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-8'}`}>
          <p className="text-[13px] font-bold uppercase tracking-[0.25em] text-primary mb-6">
            Packet Analysis · Network Intelligence · Threat Visibility
          </p>
          
          <h1 className="text-5xl md:text-7xl font-bold tracking-tight text-white leading-[1.1] mb-6">
            See what moves <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-blue-500">through your network.</span>
          </h1>
          
          <p className="text-lg md:text-xl text-muted-foreground/80 leading-relaxed mb-12 max-w-xl font-medium">
            Explore network traffic, understand connected endpoints, and uncover suspicious activity in one intelligent workspace.
          </p>
          
          <div className="flex flex-col sm:flex-row items-center gap-5">
            <button
              onClick={onLogin}
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-foreground text-background font-bold tracking-wide hover:bg-white/90 hover:scale-[1.02] active:scale-[0.98] transition-all flex items-center justify-center gap-2 shadow-[0_0_30px_rgba(255,255,255,0.15)]"
            >
              Enter Workspace
              <ArrowRight className="w-4 h-4" />
            </button>
            <button
              onClick={onEnter}
              className="w-full sm:w-auto px-8 py-4 rounded-xl bg-white/5 border border-white/10 text-foreground font-bold tracking-wide hover:bg-white/10 transition-all flex items-center justify-center gap-2 backdrop-blur-md"
            >
              <PlayCircle className="w-4 h-4 text-muted-foreground" />
              Explore Demo
            </button>
          </div>
        </div>
      </main>
      
      {/* Footer */}
      <footer className={`relative z-10 p-8 flex justify-between items-end transition-all duration-1000 delay-500 ${mounted ? 'opacity-100' : 'opacity-0'}`}>
        <p className="text-[12px] uppercase tracking-widest text-muted-foreground/40 font-medium">v0.1.0 Beta</p>
        <p className="text-[12px] uppercase tracking-widest text-muted-foreground/40 font-medium hidden md:block">Hackathon Build</p>
      </footer>
    </div>
  );
}
