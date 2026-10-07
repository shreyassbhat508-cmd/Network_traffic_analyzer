"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Maximize2, Minimize2, Minus, Plus, RotateCcw } from "lucide-react";
import { NetworkOrb } from "@/components/shared/NetworkOrb";
import { NETWORK_LINKS, NETWORK_NODES } from "@/lib/network-data";
import { useWorkspacePreferences } from "@/lib/workspace-context";

type SelectedNode = { id: string; label: string; type: string; activity: number };

const NODE_STYLE = {
  router: { color: "bg-blue-400", label: "Gateway" },
  internal: { color: "bg-cyan-300", label: "Internal" },
  external: { color: "bg-violet-300", label: "External" },
  database: { color: "bg-amber-300", label: "Server" },
  threat: { color: "bg-red-400", label: "Flagged" },
} as const;

export function NetworkTopologyView() {
  const [selectedNode, setSelectedNode] = useState<SelectedNode | null>(null);
  const [zoom, setZoom] = useState(1);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const canvasPanelRef = useRef<HTMLDivElement>(null);
  const { animationIntensity } = useWorkspacePreferences();
  const handleNodeClick = useCallback((node: { id?: string; label?: string; type?: string; activity?: number }) => {
    setSelectedNode({
      id: node.id ?? "",
      label: node.label ?? "Network node",
      type: node.type ?? "internal",
      activity: node.activity ?? 0.5,
    });
  }, []);

  useEffect(() => {
    const updateFullscreen = () => setIsFullscreen(document.fullscreenElement === canvasPanelRef.current);
    document.addEventListener("fullscreenchange", updateFullscreen);
    return () => document.removeEventListener("fullscreenchange", updateFullscreen);
  }, []);

  const connections = useMemo(() => {
    if (!selectedNode) return [];
    const index = NETWORK_NODES.findIndex(node => node.id === selectedNode.id);
    if (index < 0) return [];
    return NETWORK_LINKS
      .filter(link => link.a === index || link.b === index)
      .map(link => NETWORK_NODES[link.a === index ? link.b : link.a]);
  }, [selectedNode]);

  const toggleFullscreen = async () => {
    try {
      if (document.fullscreenElement === canvasPanelRef.current) await document.exitFullscreen();
      else await canvasPanelRef.current?.requestFullscreen();
    } catch {
      // Fullscreen can be unavailable in embedded or restricted browser contexts.
    }
  };

  return (
    <section className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="mb-1.5 font-mono text-[12px] text-primary">SAMPLE TOPOLOGY · 48 NODES</p>
          <h1 className="text-[26px] font-semibold tracking-[-0.035em] text-foreground">Network topology</h1>
          <p className="mt-1 text-[15px] text-muted-foreground">Select a node to inspect its connected sample endpoints.</p>
        </div>
        <span className="rounded border border-white/10 px-2.5 py-1.5 font-mono text-[11px] text-muted-foreground">DEMO SCENARIO</span>
      </div>

      <div ref={canvasPanelRef} className={`glass-panel relative isolate min-h-[560px] overflow-hidden ${isFullscreen ? "h-screen min-h-screen w-screen rounded-none" : "h-[min(72vh,760px)]"}`}>
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(25,103,139,0.11),transparent_60%)]" />
        <div className="absolute left-4 top-4 z-10 flex max-w-[calc(100%-5rem)] flex-wrap gap-1.5 sm:left-5 sm:top-5">
          {(Object.keys(NODE_STYLE) as Array<keyof typeof NODE_STYLE>).map(type => (
            <span key={type} className="flex items-center gap-1.5 rounded border border-white/10 bg-[#10151b]/90 px-2.5 py-1.5 text-[12px] text-foreground/85">
              <span className={`h-1.5 w-1.5 rounded-full ${NODE_STYLE[type].color}`} />
              {NODE_STYLE[type].label}
            </span>
          ))}
        </div>

        <div className="absolute right-4 top-4 z-10 flex items-center gap-1 sm:right-5 sm:top-5">
          <button onClick={() => setZoom(value => Math.max(0.7, Math.round((value - 0.15) * 100) / 100))} aria-label="Zoom out" className="grid h-8 w-8 place-items-center rounded border border-white/10 bg-[#10151b]/90 text-muted-foreground hover:text-foreground"><Minus className="h-3.5 w-3.5" /></button>
          <button onClick={() => setZoom(value => Math.min(1.9, Math.round((value + 0.15) * 100) / 100))} aria-label="Zoom in" className="grid h-8 w-8 place-items-center rounded border border-white/10 bg-[#10151b]/90 text-muted-foreground hover:text-foreground"><Plus className="h-3.5 w-3.5" /></button>
          <button onClick={() => setZoom(1)} aria-label="Reset zoom" className="grid h-8 w-8 place-items-center rounded border border-white/10 bg-[#10151b]/90 text-muted-foreground hover:text-foreground"><RotateCcw className="h-3.5 w-3.5" /></button>
          <button onClick={() => void toggleFullscreen()} aria-label={isFullscreen ? "Exit fullscreen" : "Enter fullscreen"} className="ml-1 grid h-8 w-8 place-items-center rounded border border-white/10 bg-[#10151b]/90 text-muted-foreground hover:text-foreground">
            {isFullscreen ? <Minimize2 className="h-3.5 w-3.5" /> : <Maximize2 className="h-3.5 w-3.5" />}
          </button>
        </div>

        <NetworkOrb
          interactive
          showLabels
          scale={1.15 * zoom}
          motion={animationIntensity}
          initialNodes={NETWORK_NODES}
          initialLinks={NETWORK_LINKS}
          onNodeClick={handleNodeClick}
        />

        <div className="absolute bottom-4 left-4 z-10 rounded border border-white/10 bg-[#10151b]/85 px-3 py-2 font-mono text-[11px] text-muted-foreground sm:bottom-5 sm:left-5">
          MOVE POINTER TO ORBIT <span className="px-1 text-white/20">·</span> SELECT NODE FOR DETAILS
        </div>

        {selectedNode && (
          <aside className="absolute bottom-4 right-4 z-10 w-[min(320px,calc(100%-2rem))] rounded-lg border border-white/10 bg-[#10151b]/95 p-4 shadow-xl sm:bottom-5 sm:right-5">
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="font-mono text-[11px] uppercase tracking-[0.12em] text-primary">{selectedNode.type} · SAMPLE NODE</p>
                <h2 className="mt-1 truncate text-[15px] font-semibold text-foreground">{selectedNode.label}</h2>
              </div>
              <button onClick={() => setSelectedNode(null)} aria-label="Close node details" className="text-[12px] text-muted-foreground hover:text-foreground">Close</button>
            </div>
            <div className="mt-3 flex items-center justify-between text-[12px] text-muted-foreground">
              <span>Illustrative activity</span>
              <span className="font-mono tabular-nums text-foreground">{Math.round(selectedNode.activity * 100)}%</span>
            </div>
            <div className="mt-1.5 h-1 overflow-hidden rounded bg-white/10">
              <div className="h-full rounded bg-primary" style={{ width: `${Math.round(selectedNode.activity * 100)}%` }} />
            </div>
            <div className="mt-3 border-t border-white/[0.08] pt-2.5">
              <p className="font-mono text-[11px] text-muted-foreground">CONNECTED SAMPLE NODES</p>
              <div className="mt-1.5 flex flex-wrap gap-1.5">
                {connections.map(node => <span key={node.id} className="rounded border border-white/10 px-1.5 py-1 font-mono text-[11px] text-foreground/80">{node.label}</span>)}
                {connections.length === 0 && <span className="text-[12px] text-muted-foreground">No connections in this sample.</span>}
              </div>
            </div>
          </aside>
        )}
      </div>
    </section>
  );
}
