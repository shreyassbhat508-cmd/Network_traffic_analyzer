"use client";

import { useEffect, useState } from "react";
import { NetworkOrb } from "@/components/shared/NetworkOrb";
import { Network } from "lucide-react";

export function SplashScreen({ onComplete }: { onComplete: () => void }) {
  const [showLogo, setShowLogo] = useState(false);

  useEffect(() => {
    // Reveal logo slightly after orb starts
    const t1 = setTimeout(() => setShowLogo(true), 400);
    // Move to next screen after ~2.5s
    const t2 = setTimeout(() => onComplete(), 2500);

    return () => {
      clearTimeout(t1);
      clearTimeout(t2);
    };
  }, [onComplete]);

  return (
    <div className="fixed inset-0 bg-[#06080D] flex flex-col items-center justify-center z-[100]">
      <div className="absolute inset-0 opacity-40">
        <NetworkOrb scale={0.8} />
      </div>
      
      <div className={`relative z-10 flex flex-col items-center transition-all duration-1000 transform ${showLogo ? 'opacity-100 translate-y-0' : 'opacity-0 translate-y-4'}`}>
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-primary/20 to-cyan-500/10 border border-primary/30 flex items-center justify-center shadow-[0_0_30px_rgba(59,130,246,0.2)] mb-6 backdrop-blur-md">
          <Network className="w-6 h-6 text-primary" />
        </div>
        <h1 className="text-2xl font-bold tracking-widest text-foreground">NetAnalyzer</h1>
        <p className="text-[13px] uppercase tracking-[0.2em] text-muted-foreground mt-3 font-medium">Initializing network intelligence</p>
        
        <div className="mt-12 w-32 h-px bg-white/10 relative overflow-hidden">
          <div className="absolute top-0 left-0 h-full w-1/3 bg-gradient-to-r from-transparent via-cyan-400 to-transparent animate-[shimmer_1.5s_infinite]" />
        </div>
      </div>
    </div>
  );
}
