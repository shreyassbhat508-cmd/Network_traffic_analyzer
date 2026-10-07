"use client";

import { useEffect, useState } from "react";
import type { AnimationIntensity } from "@/lib/workspace-context";

// Global flag to prevent re-animating on every dashboard visit
let globalAnimationPlayed = false;

export function CountUp({ value, duration = 1200, separator = ",", motion = "full" }: { value: number, duration?: number, separator?: string, motion?: AnimationIntensity }) {
  const [count, setCount] = useState(globalAnimationPlayed || motion === "off" ? value : 0);

  useEffect(() => {
    if (globalAnimationPlayed || motion === "off") {
      return;
    }

    let startTimestamp: number | null = null;
    let animationFrame: number;
    let lastUpdate = 0;
    const animationDuration = motion === "reduced" ? Math.min(duration, 500) : duration;
    const step = (timestamp: number) => {
      if (!startTimestamp) startTimestamp = timestamp;
      const progress = Math.min((timestamp - startTimestamp) / animationDuration, 1);
      
      const easeProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      if (timestamp - lastUpdate >= 50 || progress === 1) {
        setCount(Math.floor(easeProgress * value));
        lastUpdate = timestamp;
      }
      
      if (progress < 1) {
        animationFrame = window.requestAnimationFrame(step);
      } else {
        globalAnimationPlayed = true;
      }
    };
    animationFrame = window.requestAnimationFrame(step);

    return () => {
      if (animationFrame) cancelAnimationFrame(animationFrame);
    };
  }, [value, duration, motion]);

  const formattedValue = new Intl.NumberFormat('en-US').format(count);
  return <span>{separator === "," ? formattedValue : count.toString()}</span>;
}
