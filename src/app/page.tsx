"use client";

import { useCallback, useState } from "react";
import { Activity, ArrowDownToLine, Bell, Database, Network, Radio, Search, Settings, ShieldAlert, WifiOff } from "lucide-react";
import { NavProvider, useNav, type View } from "@/lib/nav-context";
import { WorkspacePreferencesProvider, useWorkspacePreferences } from "@/lib/workspace-context";
import { NETWORK_LINKS, NETWORK_NODES } from "@/lib/network-data";
import { OverviewCards } from "@/components/dashboard/OverviewCards";
import { Charts } from "@/components/dashboard/Charts";
import { MiniAlertsPanel } from "@/components/dashboard/MiniAlertsPanel";
import { PacketUpload } from "@/components/dashboard/PacketUpload";
import { TopIps } from "@/components/dashboard/TopIps";
import { NetworkOrb } from "@/components/shared/NetworkOrb";
import { PacketSearchView } from "@/components/views/PacketSearchView";
import { SecurityAlertsView } from "@/components/views/SecurityAlertsView";
import { NetworkTopologyView } from "@/components/views/NetworkTopologyView";
import { SettingsView } from "@/components/views/SettingsView";
import { SplashScreen } from "@/components/entry/SplashScreen";
import { WelcomeScreen } from "@/components/entry/WelcomeScreen";
import { LoginScreen } from "@/components/entry/LoginScreen";

const NAV_ITEMS: { id: View; label: string; icon: typeof Activity }[] = [
  { id: "dashboard", label: "Dashboard", icon: Activity },
  { id: "search", label: "Packet Search", icon: Search },
  { id: "alerts", label: "Security Alerts", icon: ShieldAlert },
  { id: "topology", label: "Network Topology", icon: Radio },
  { id: "settings", label: "Settings", icon: Settings },
];

function DashboardView() {
  const { animationIntensity } = useWorkspacePreferences();
  const [selectedNode, setSelectedNode] = useState<{ label: string; type: string } | null>(null);
  const handleNodeClick = useCallback((node: { label?: string; type?: string }) => {
    setSelectedNode({ label: node.label ?? "Network node", type: node.type ?? "endpoint" });
  }, []);

  return (
    <div className="space-y-5 sm:space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="mb-1.5 font-mono text-[12px] text-primary">NETWORK INTELLIGENCE · DEMO CAPTURE 04</p>
          <h1 className="text-[26px] font-semibold tracking-[-0.04em] text-foreground sm:text-[30px]">Traffic overview</h1>
          <p className="mt-1 text-[14px] text-muted-foreground">A sample snapshot for exploring packets, endpoints, and flagged activity.</p>
        </div>
        <a href="#capture-import" className="inline-flex h-9 items-center gap-2 rounded-md bg-primary px-3.5 text-[13px] font-semibold text-primary-foreground transition-colors hover:bg-primary/90">
          <ArrowDownToLine className="h-3.5 w-3.5" /> Import PCAP
        </a>
      </div>

      <OverviewCards />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.8fr)_minmax(290px,0.78fr)]">
        <section className="glass-panel relative isolate min-h-[390px] overflow-hidden sm:min-h-[450px]">
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,rgba(17,92,129,0.14),transparent_62%)]" />
          <div className="absolute left-4 top-4 z-10 sm:left-5 sm:top-5">
            <h2 className="text-[14px] font-semibold text-foreground">Endpoint relationships</h2>
            <p className="mt-1 font-mono text-[11px] text-muted-foreground">ILLUSTRATIVE TOPOLOGY · 48 NODES</p>
          </div>
          <div className="absolute right-4 top-4 z-10 rounded border border-white/10 bg-[#10151b]/85 px-2.5 py-1.5 font-mono text-[11px] text-muted-foreground sm:right-5 sm:top-5">
            {selectedNode ? <><span className="text-primary">SELECTED</span> · {selectedNode.label}</> : "MOVE POINTER TO ORBIT · CLICK A NODE"}
          </div>
          <div className="absolute inset-0 z-0 opacity-90">
            <NetworkOrb
              interactive
              scale={1.22}
              motion={animationIntensity}
              initialNodes={NETWORK_NODES}
              initialLinks={NETWORK_LINKS}
              onNodeClick={handleNodeClick}
            />
          </div>
          <div className="pointer-events-none absolute bottom-4 left-4 z-10 flex flex-wrap gap-x-4 gap-y-2 rounded border border-white/10 bg-[#10151b]/90 px-3 py-2 sm:bottom-5 sm:left-5">
            {[
              ["bg-blue-400", "Gateway"], ["bg-cyan-300", "Internal"], ["bg-violet-300", "External"], ["bg-amber-300", "Server"], ["bg-red-400", "Flagged"],
            ].map(([color, label]) => <span key={label} className="flex items-center gap-1.5 text-[11px] text-muted-foreground"><span className={`h-1.5 w-1.5 rounded-full ${color}`} />{label}</span>)}
          </div>
          <p className="absolute bottom-4 right-4 z-10 hidden font-mono text-[11px] text-muted-foreground/70 md:block">SAMPLE CONNECTIONS · NOT LIVE TRAFFIC</p>
        </section>

        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-1 xl:grid-rows-[minmax(190px,0.82fr)_minmax(220px,1fr)]">
          <div id="capture-import" className="min-h-[200px] scroll-mt-20">
            <PacketUpload />
          </div>
          <MiniAlertsPanel />
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1.6fr)_minmax(330px,0.9fr)]">
        <Charts motion={animationIntensity} />
        <TopIps />
      </div>
    </div>
  );
}

function TopNavigation() {
  const { view, setView } = useNav();
  return (
    <header className="sticky top-0 z-30 border-b border-white/[0.08] bg-[#0d1116]/95 backdrop-blur-sm">
      <div className="flex min-h-[60px] flex-wrap items-center justify-between gap-x-5 gap-y-2 px-4 py-2.5 sm:px-6 xl:flex-nowrap">
        <a href="#dashboard" onClick={event => { event.preventDefault(); setView("dashboard"); }} className="flex shrink-0 items-center gap-2.5 rounded-sm focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary">
          <span className="grid h-8 w-8 place-items-center rounded-md border border-primary/25 bg-primary/[0.08] text-primary"><Network className="h-4 w-4" strokeWidth={1.7} /></span>
          <span className="text-[15px] font-semibold tracking-[-0.02em] text-foreground">NetAnalyzer</span>
        </a>

        <nav aria-label="Primary navigation" className="order-3 -mx-1 flex w-full min-w-0 gap-1 overflow-x-auto xl:order-2 xl:mx-0 xl:w-auto xl:flex-1 xl:justify-center">
          {NAV_ITEMS.map(item => {
            const active = view === item.id;
            return (
              <button key={item.id} type="button" aria-current={active ? "page" : undefined} onClick={() => setView(item.id)} className={`relative flex shrink-0 items-center gap-2 rounded px-3 py-2 text-[13px] font-medium transition-colors after:absolute after:inset-x-3 after:bottom-0 after:h-[2px] after:rounded-full after:transition-colors ${active ? "text-foreground after:bg-primary" : "text-muted-foreground after:bg-transparent hover:bg-white/[0.035] hover:text-foreground"}`}>
                <item.icon className={`h-3.5 w-3.5 ${active ? "text-primary" : "opacity-75"}`} strokeWidth={1.8} />
                {item.label}
              </button>
            );
          })}
        </nav>

        <div className="order-2 ml-auto flex shrink-0 items-center gap-2.5 xl:order-3">
          <span className="hidden items-center gap-1.5 rounded border border-amber-400/20 bg-amber-400/[0.06] px-2 py-1.5 text-[11px] text-amber-200/90 sm:flex">
            <WifiOff className="h-3 w-3" /> Backend offline
          </span>
          <button type="button" onClick={() => setView("alerts")} aria-label="Open security alerts" title="Open security alerts" className="relative grid h-8 w-8 place-items-center rounded text-muted-foreground transition-colors hover:bg-white/[0.05] hover:text-foreground">
            <Bell className="h-4 w-4" />
            <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full bg-[#ed9387]" />
          </button>
          <span className="hidden items-center gap-1.5 border-l border-white/10 pl-3 font-mono text-[11px] text-muted-foreground sm:flex"><Database className="h-3 w-3" /> SAMPLE</span>
        </div>
      </div>
    </header>
  );
}

function ViewRouter() {
  const { view } = useNav();
  switch (view) {
    case "search": return <PacketSearchView />;
    case "alerts": return <SecurityAlertsView />;
    case "topology": return <NetworkTopologyView />;
    case "settings": return <SettingsView />;
    default: return <DashboardView />;
  }
}

function WorkspaceShell() {
  const { animationIntensity } = useWorkspacePreferences();
  return (
    <div className="workspace relative flex h-dvh flex-col overflow-hidden" data-reduced-motion={animationIntensity !== "full"}>
      <div aria-hidden="true" className="workspace-backdrop pointer-events-none fixed inset-0 z-0 overflow-hidden">
        <div className="workspace-grid absolute inset-0" />
        <div className="absolute inset-0 opacity-[0.11] mix-blend-screen">
          <NetworkOrb interactive={false} scale={1.3} particleCount={26} motion={animationIntensity} />
        </div>
      </div>
      <div className="relative z-10 flex min-h-0 flex-1 flex-col">
        <TopNavigation />
        <main className="min-h-0 flex-1 overflow-y-auto px-4 py-5 sm:px-6 sm:py-6 xl:px-8">
          <div className="mx-auto max-w-[1580px] pb-8">
            <ViewRouter />
            <footer className="mt-7 flex flex-wrap items-center justify-between gap-2 border-t border-white/[0.08] pt-3 font-mono text-[11px] tracking-wide text-muted-foreground/65">
              <span>DEMO SNAPSHOT · NOT CONNECTED TO A LIVE SENSOR</span>
              <span>LOCAL SESSION</span>
            </footer>
          </div>
        </main>
      </div>
    </div>
  );
}

export default function Page() {
  const [entryState, setEntryState] = useState<"splash" | "welcome" | "login" | "app">("splash");

  if (entryState === "splash") return <SplashScreen onComplete={() => setEntryState("welcome")} />;
  if (entryState === "welcome") return <WelcomeScreen onEnter={() => setEntryState("login")} onLogin={() => setEntryState("app")} />;
  if (entryState === "login") return <LoginScreen onBack={() => setEntryState("welcome")} onLogin={() => setEntryState("app")} />;

  return (
    <NavProvider>
      <WorkspacePreferencesProvider>
        <WorkspaceShell />
      </WorkspacePreferencesProvider>
    </NavProvider>
  );
}
