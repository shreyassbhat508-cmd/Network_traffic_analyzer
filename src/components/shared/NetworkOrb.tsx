"use client";

import { useEffect, useRef } from "react";
import type { AnimationIntensity } from "@/lib/workspace-context";

interface NetworkOrbProps {
  interactive?: boolean;
  scale?: number;
  className?: string;
  onNodeClick?: (node: OrbNodeInput) => void;
  showLabels?: boolean;
  initialNodes?: OrbNodeInput[];
  initialLinks?: OrbLink[];
  motion?: AnimationIntensity;
  particleCount?: number;
}

interface OrbNodeInput {
  id?: string;
  x?: number;
  y?: number;
  z?: number;
  type?: string;
  label?: string;
  activity?: number;
}

interface OrbNode extends OrbNodeInput {
  origX: number;
  origY: number;
  origZ: number;
  color: string;
  label: string;
  type: string;
  activity: number;
}

interface OrbLink {
  a: number;
  b: number;
  active: boolean;
  offset: number;
}

export function NetworkOrb({ interactive = false, scale = 1, className = "", onNodeClick, showLabels = false, initialNodes, initialLinks, motion = "full", particleCount }: NetworkOrbProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d", { alpha: true });
    if (!ctx) return;

    let animationFrameId = 0;
    let time = 0;
    let isVisible = false;
    let intersectsViewport = false;
    let lastDrawTime = 0;
    let hasDrawn = false;
    const systemPrefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const effectiveMotion = motion === "off" ? "off" : systemPrefersReducedMotion ? "reduced" : motion;
    
    const frameRate = interactive
      ? (effectiveMotion === "full" ? 36 : 18)
      : (effectiveMotion === "full" ? 24 : 12);
    const frameInterval = 1000 / frameRate;
    
    const radius = 200 * scale;
    let nodes: OrbNode[] = [];
    let links: OrbLink[] = [];

    if (initialNodes && initialLinks) {
      nodes = initialNodes.map(n => ({
        ...n,
        origX: (n.x ?? 0) * radius,
        origY: (n.y ?? 0) * radius,
        origZ: (n.z ?? 0) * radius,
        color: n.type === "threat" ? "rgba(239, 117, 104, 0.9)"
          : n.type === "router" ? "rgba(72, 200, 237, 0.9)"
          : n.type === "external" ? "rgba(181, 166, 219, 0.85)"
          : n.type === "database" ? "rgba(214, 169, 104, 0.85)"
          : "rgba(94, 198, 216, 0.78)",
        label: n.label ?? n.id ?? "Network node",
        type: n.type ?? "endpoint",
        activity: n.activity ?? 0.5,
      }));
      links = initialLinks.map(link => ({ ...link }));
    } else {
      // Lower particle counts for performance
      const numNodes = particleCount ?? (interactive ? 50 : 80);
      for (let i = 0; i < numNodes; i++) {
        const phi = Math.acos(-1 + (2 * i) / numNodes);
        const theta = Math.sqrt(numNodes * Math.PI) * phi;
        
        const x = radius * Math.cos(theta) * Math.sin(phi);
        const y = radius * Math.sin(theta) * Math.sin(phi);
        const z = radius * Math.cos(phi);
        
        let color = "rgba(100, 150, 255, 0.4)";
        let label = `NODE-${Math.floor(Math.random() * 999)}`;
        let type = "endpoint";
        const activity = Math.random();

        if (Math.random() > 0.85) {
          color = "rgba(6, 182, 212, 0.8)";
          label = `GW-${Math.floor(Math.random() * 99)}`;
          type = "router";
        } else if (interactive && Math.random() > 0.92) {
          color = "rgba(239, 68, 68, 0.8)";
          label = `UNKN-${Math.floor(Math.random() * 99)}`;
          type = "threat";
        }
        
        nodes.push({ origX: x, origY: y, origZ: z, color, label, type, activity });
      }

      // Generate connections efficiently
      for (let i = 0; i < numNodes; i++) {
        const distances = nodes.map((n, idx) => ({ 
          idx, 
          d: (n.origX - nodes[i].origX)**2 + (n.origY - nodes[i].origY)**2 + (n.origZ - nodes[i].origZ)**2
        }));
        distances.sort((a, b) => a.d - b.d);
        
        // Connect to nearest 2-3 nodes (reduced from 3 for performance)
        const maxConns = interactive ? 3 : 2;
        for (let j = 1; j <= maxConns; j++) {
          if (distances[j] && distances[j].idx > i) {
            links.push({ 
              a: i, 
              b: distances[j].idx, 
              active: Math.random() > 0.8,
              offset: Math.random() * 100
            });
          }
        }
      }
    }

    // Mouse interaction
    let targetRotX = 0;
    let targetRotY = 0;
    let rotX = 0;
    let rotY = 0;
    let dpr = 1;
    let scheduleFrame = () => {};

    const resize = () => {
      const parent = canvas.parentElement;
      if (parent) {
        dpr = Math.min(window.devicePixelRatio || 1, 2); // Cap at 2x for performance
        const w = parent.clientWidth;
        const h = parent.clientHeight;
        const pixelWidth = Math.round(w * dpr);
        const pixelHeight = Math.round(h * dpr);
        if (canvas.width !== pixelWidth) {
          canvas.width = pixelWidth;
          hasDrawn = false;
        }
        if (canvas.height !== pixelHeight) {
          canvas.height = pixelHeight;
          hasDrawn = false;
        }
        ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
        if (effectiveMotion === "off" && hasDrawn) hasDrawn = false;
        scheduleFrame();
      }
    };
    window.addEventListener("resize", resize);
    resize();
    const resizeObserver = new ResizeObserver(resize);
    if (canvas.parentElement) resizeObserver.observe(canvas.parentElement);

    // Pre-allocate arrays for projection to avoid garbage collection
    const projX = new Float32Array(nodes.length);
    const projY = new Float32Array(nodes.length);
    const projZ = new Float32Array(nodes.length);
    const projPersp = new Float32Array(nodes.length);
    const projRadius = new Float32Array(nodes.length);
    const renderOrder = new Int32Array(nodes.length);
    for(let i = 0; i < nodes.length; i++) renderOrder[i] = i;

    const draw = (timestamp: number) => {
      animationFrameId = 0;
      if (!isVisible) return;

      const elapsed = timestamp - lastDrawTime;
      if (elapsed < frameInterval) {
        scheduleFrame();
        return;
      }
      
      lastDrawTime = timestamp - (elapsed % frameInterval);
      time += 0.005 * (elapsed / 16.66); // scale time by actual elapsed for smooth rotation
      
      // We divide by dpr because ctx is scaled
      const w = canvas.width / dpr;
      const h = canvas.height / dpr;
      const cx = w / 2;
      const cy = h / 2;

      ctx.clearRect(0, 0, w, h);

      // Smooth rotation towards target
      rotX += (targetRotX - rotX) * 0.05;
      rotY += (targetRotY - rotY) * 0.05;

      // Base auto-rotation
      const finalRotX = rotX + (interactive ? 0 : time * 0.5);
      const finalRotY = rotY + time;
      
      const cosY = Math.cos(finalRotY);
      const sinY = Math.sin(finalRotY);
      const cosX = Math.cos(finalRotX);
      const sinX = Math.sin(finalRotX);

      // Calculate projected coordinates in O(N)
      for (let i = 0; i < nodes.length; i++) {
        const node = nodes[i];
        
        // Rotate Y
        const x1 = node.origX * cosY - node.origZ * sinY;
        const z1 = node.origX * sinY + node.origZ * cosY;
        
        // Rotate X
        const y2 = node.origY * cosX - z1 * sinX;
        const z2 = node.origY * sinX + z1 * cosX;

        // Perspective
        const perspective = 800 / (800 + z2);
        
        projX[i] = cx + x1 * perspective;
        projY[i] = cy + y2 * perspective;
        projZ[i] = z2;
        projPersp[i] = perspective;
      }

      // Sort indices by Z for proper rendering order
      renderOrder.sort((a, b) => projZ[b] - projZ[a]);

      // Draw links O(L) - extremely fast direct lookups now
      ctx.lineWidth = 1;
      for (let i = 0; i < links.length; i++) {
        const link = links[i];
        const a = link.a;
        const b = link.b;
        
        const avgZ = (projZ[a] + projZ[b]) / 2;
        const opacity = Math.max(0.05, Math.min(0.4, 1 - (avgZ + radius) / (radius * 2.5)));
        
        ctx.beginPath();
        ctx.moveTo(projX[a], projY[a]);
        ctx.lineTo(projX[b], projY[b]);
        
        const persp = (projPersp[a] + projPersp[b]) / 2;
        
        if (link.active) {
          const dashOffset = -time * 500 + link.offset;
          ctx.strokeStyle = `rgba(6, 182, 212, ${opacity * 1.5})`;
          ctx.setLineDash([10, 40]);
          ctx.lineDashOffset = dashOffset;
          ctx.lineWidth = 1.5 * persp;
          ctx.stroke();
          ctx.setLineDash([]);
        } else {
          ctx.strokeStyle = `rgba(150, 180, 255, ${opacity * 0.5})`;
          ctx.lineWidth = 0.5 * persp;
          ctx.stroke();
        }
      }

      // Draw nodes O(N)
      for (let j = 0; j < nodes.length; j++) {
        const i = renderOrder[j];
        const node = nodes[i];
        
        const px = projX[i];
        const py = projY[i];
        const z = projZ[i];
        const perspective = projPersp[i];
        
        const opacity = Math.max(0.1, Math.min(1, 1 - (z + radius) / (radius * 2)));
        const isHighlight = node.type === "threat" || node.type === "router";
        const size = Math.max(0.5, (isHighlight ? 3 : 1.5) * perspective);
        projRadius[i] = size;
        
        ctx.globalAlpha = opacity;
        
        // Node core
        ctx.beginPath();
        ctx.arc(px, py, size, 0, Math.PI * 2);
        ctx.fillStyle = node.color;
        ctx.fill();

        // Node glow if active
        if (isHighlight) {
          const pulse = Math.sin(time * 10 + px) * 0.2 + 0.8;
          ctx.beginPath();
          ctx.arc(px, py, size * 3 * pulse, 0, Math.PI * 2);
          ctx.globalAlpha = opacity * 0.16;
          ctx.fillStyle = node.color;
          ctx.fill();
          ctx.globalAlpha = opacity;
        }

        // Labels
        if (showLabels && opacity > 0.7 && size > 2) {
          ctx.fillStyle = `rgba(255,255,255,${(opacity - 0.7) * 3})`;
          ctx.font = `${Math.max(8, 10 * perspective)}px "Inter", monospace`;
          ctx.textAlign = "center";
          ctx.fillText(node.label, px, py - size - 4);
        }
      }
      
      ctx.globalAlpha = 1;
      hasDrawn = true;
      if (effectiveMotion !== "off") scheduleFrame();
    };

    scheduleFrame = () => {
      if (isVisible && animationFrameId === 0 && (effectiveMotion !== "off" || !hasDrawn)) {
        animationFrameId = requestAnimationFrame(draw);
      }
    };

    const setVisible = () => {
      const nextVisibility = intersectsViewport && !document.hidden && canvas.clientWidth > 0 && canvas.clientHeight > 0;
      if (nextVisibility && !isVisible) lastDrawTime = performance.now();
      isVisible = nextVisibility;
      if (isVisible) scheduleFrame();
      else if (animationFrameId) {
        cancelAnimationFrame(animationFrameId);
        animationFrameId = 0;
      }
    };

    const handleMouseMove = (e: MouseEvent) => {
      if (!interactive) return;
      const rect = canvas.getBoundingClientRect();
      const mouseX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
      const mouseY = ((e.clientY - rect.top) / rect.height) * 2 - 1;
      targetRotY = mouseX * Math.PI * 0.5;
      targetRotX = mouseY * Math.PI * 0.2;
    };

    const handleClick = (e: MouseEvent) => {
      if (!interactive || !onNodeClick) return;
      const rect = canvas.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      let hit = -1;
      let nearest = 18 * 18;
      for (let i = 0; i < nodes.length; i++) {
        const dx = projX[i] - x;
        const dy = projY[i] - y;
        const distance = dx * dx + dy * dy;
        const hitRadius = Math.max(18, projRadius[i] + 10);
        if (distance < Math.min(nearest, hitRadius * hitRadius)) {
          nearest = distance;
          hit = i;
        }
      }
      if (hit >= 0) onNodeClick(nodes[hit]);
    };

    const handleVisibilityChange = () => {
      setVisible();
    };

    // Intersection observer to pause rendering if canvas is offscreen
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        intersectsViewport = entry.isIntersecting;
      });
      setVisible();
    }, { threshold: 0 });
    observer.observe(canvas);

    if (interactive) {
      canvas.addEventListener("mousemove", handleMouseMove);
      canvas.addEventListener("click", handleClick);
    }
    document.addEventListener("visibilitychange", handleVisibilityChange);

    return () => {
      window.removeEventListener("resize", resize);
      resizeObserver.disconnect();
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      observer.disconnect();
      if (interactive) {
        canvas.removeEventListener("mousemove", handleMouseMove);
        canvas.removeEventListener("click", handleClick);
      }
      cancelAnimationFrame(animationFrameId);
    };
  }, [interactive, scale, showLabels, onNodeClick, initialNodes, initialLinks, motion, particleCount]);

  return (
    <canvas 
      ref={canvasRef} 
      className={`w-full h-full block ${interactive ? 'cursor-crosshair' : 'pointer-events-none'} ${className}`} 
      style={{ touchAction: "none" }}
    />
  );
}
