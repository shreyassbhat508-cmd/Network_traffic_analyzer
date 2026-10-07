"use client";

import { useState } from "react";
import { AlertTriangle, ShieldAlert, Shield, Crosshair, ArrowRight, Filter } from "lucide-react";

export const ALERTS = [
  {
    id: 1,
    type: "Port Scan Detected",
    desc: "Rapid connection sweep across 1,024 ports in under 4 seconds from single source.",
    src: "192.168.1.105",
    dst: "10.0.0.1",
    time: "10:24:11 UTC",
    sev: "high" as const,
    Icon: Crosshair,
    proto: "TCP",
    packets: 1024,
  },
  {
    id: 2,
    type: "Unusual Data Transfer",
    desc: "8.4 GB outbound to unrecognised external host in 12 minutes — possible exfiltration.",
    src: "192.168.1.42",
    dst: "8.8.4.4",
    time: "10:09:44 UTC",
    sev: "medium" as const,
    Icon: AlertTriangle,
    proto: "TCP",
    packets: 14200,
  },
  {
    id: 3,
    type: "Malware Signature Match",
    desc: "Packet payload matches known Cobalt Strike C2 beacon fingerprint in threat database.",
    src: "45.33.22.1",
    dst: "192.168.1.10",
    time: "08:30:07 UTC",
    sev: "high" as const,
    Icon: ShieldAlert,
    proto: "TCP",
    packets: 38,
  },
  {
    id: 4,
    type: "SSH Brute-force Attempt",
    desc: "147 consecutive failed authentication attempts originating from a single IP.",
    src: "172.16.0.5",
    dst: "SSH Server",
    time: "07:15:22 UTC",
    sev: "low" as const,
    Icon: Shield,
    proto: "TCP",
    packets: 147,
  },
  {
    id: 5,
    type: "DNS Tunnelling Detected",
    desc: "Unusually long DNS TXT query payload — potential command channel over DNS.",
    src: "192.168.1.10",
    dst: "1.1.1.1",
    time: "06:55:01 UTC",
    sev: "medium" as const,
    Icon: AlertTriangle,
    proto: "DNS",
    packets: 92,
  },
];

const SEV_STYLES = {
  high:   { bar: "bg-[#e78a70]", icon: "text-[#ef9b82]", iconBg: "bg-[#e78a70]/10 border-[#e78a70]/20", badge: "text-[#ef9b82] bg-[#e78a70]/10 border-[#e78a70]/20", card: "border-[#e78a70]/35", labelClass: "text-[#ef9b82]", label: "Critical" },
  medium: { bar: "bg-[#d6a968]", icon: "text-[#dfb878]", iconBg: "bg-[#d6a968]/10 border-[#d6a968]/20", badge: "text-[#dfb878] bg-[#d6a968]/10 border-[#d6a968]/20", card: "border-[#d6a968]/35", labelClass: "text-[#dfb878]", label: "Warning" },
  low:    { bar: "bg-[#8c9eab]", icon: "text-[#a7bac6]", iconBg: "bg-[#8c9eab]/10 border-[#8c9eab]/20", badge: "text-[#a7bac6] bg-[#8c9eab]/10 border-[#8c9eab]/20", card: "border-[#8c9eab]/30", labelClass: "text-[#a7bac6]", label: "Info" },
};

export function SecurityAlertsView() {
  const [filter, setFilter] = useState<"all" | "high" | "medium" | "low">("all");

  const rows = filter === "all" ? ALERTS : ALERTS.filter(a => a.sev === filter);
  const counts = {
    high:   ALERTS.filter(a => a.sev === "high").length,
    medium: ALERTS.filter(a => a.sev === "medium").length,
    low:    ALERTS.filter(a => a.sev === "low").length,
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-foreground tracking-wide">Threat Intelligence</h1>
          <p className="text-[15px] text-muted-foreground mt-1 font-medium">Monitoring engine offline. Displaying static alert database.</p>
        </div>
        <span className="text-[12px] font-bold text-amber-400 bg-amber-500/10 border border-amber-500/20 px-2.5 py-1.5 rounded-md uppercase tracking-widest self-start md:self-auto shadow-[0_0_10px_rgba(245,158,11,0.15)]">
          Demo Dataset
        </span>
      </div>

      {/* Severity summary cards */}
      <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
        {(["high", "medium", "low"] as const).map(s => {
          const st = SEV_STYLES[s];
          const active = filter === s;
          return (
            <button
              key={s}
              onClick={() => setFilter(active ? "all" : s)}
              aria-pressed={active}
              className={`glass-panel relative flex items-center justify-between overflow-hidden p-4 text-left transition-colors group ${active ? st.card : "hover:border-white/20"}`}
            >
              <div className="relative z-10">
                <p className="font-mono text-[28px] font-medium tracking-[-0.06em] text-foreground">{counts[s].toString().padStart(2, "0")}</p>
                <p className={`mt-1.5 text-[12px] font-semibold uppercase tracking-[0.14em] ${st.labelClass}`}>
                  {st.label}
                </p>
              </div>
              <div className={`relative z-10 flex h-9 w-9 items-center justify-center rounded-md border ${st.iconBg} ${active ? "opacity-100" : "opacity-65"}`}>
                 {s === 'high' ? <ShieldAlert className={`w-6 h-6 ${st.icon}`} /> : s === 'medium' ? <AlertTriangle className={`w-6 h-6 ${st.icon}`} /> : <Shield className={`w-6 h-6 ${st.icon}`} />}
              </div>
            </button>
          );
        })}
      </div>

      {/* Filter bar */}
      <div className="flex flex-wrap items-center gap-3 border-y border-white/[0.07] py-2">
        <Filter className="w-4 h-4 text-muted-foreground/60" />
        <span className="text-[13px] font-bold uppercase tracking-widest text-muted-foreground/60">Filter:</span>
        <div className="flex gap-1 rounded-md border border-white/[0.08] bg-black/20 p-1">
          {(["all", "high", "medium", "low"] as const).map(s => (
            <button
              key={s}
              onClick={() => setFilter(s)}
              className={`px-3.5 py-1.5 rounded-lg text-[13px] font-bold uppercase tracking-widest transition-all ${
                filter === s
                  ? "bg-primary/10 text-primary border border-primary/20"
                  : "bg-transparent text-muted-foreground hover:bg-white/5 hover:text-foreground border border-transparent"
              }`}
            >
              {s === "all" ? "All" : SEV_STYLES[s].label}
            </button>
          ))}
        </div>
        <span className="ml-auto text-[13px] font-mono font-medium text-muted-foreground/80 uppercase tracking-widest">{rows.length} alert{rows.length !== 1 ? "s" : ""} found</span>
      </div>

      {/* Alert list */}
      <div className="glass-panel divide-y divide-white/[0.07] overflow-hidden">
        {rows.length > 0 ? rows.map(a => {
          const s = SEV_STYLES[a.sev];
          return (
            <div key={a.id} className="group flex gap-4 px-4 py-5 transition-colors hover:bg-white/[0.025] sm:px-5">
              {/* Severity bar */}
              <div className={`w-0.5 shrink-0 rounded-full ${s.bar}`} />

              {/* Icon */}
                <div className={`flex h-9 w-9 shrink-0 items-center justify-center rounded-md border ${s.iconBg}`}>
                <a.Icon className={`w-5 h-5 ${s.icon}`} />
              </div>

              {/* Body */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-4 flex-wrap">
                  <div>
                    <p className="text-[15px] font-semibold text-foreground leading-tight">{a.type}</p>
                    <p className="mt-1.5 max-w-2xl text-[14px] leading-relaxed text-muted-foreground">{a.desc}</p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`rounded border px-2 py-1 font-mono text-[11px] uppercase tracking-widest ${s.badge}`}>
                      {s.label}
                    </span>
                  </div>
                </div>

                {/* Meta row */}
                <div className="mt-3 inline-flex flex-wrap items-center gap-3 rounded border border-white/[0.07] bg-black/15 px-2.5 py-2 font-mono text-[12px] text-muted-foreground">
                  <span className="flex items-center gap-2 text-foreground/80 font-semibold">
                    {a.src} <ArrowRight className="w-3.5 h-3.5 text-muted-foreground/50" /> {a.dst}
                  </span>
                  <span className="text-white/10">|</span>
                  <span className="font-semibold text-primary/80">{a.proto}</span>
                  <span className="text-white/10">|</span>
                  <span>{a.packets.toLocaleString()} packets</span>
                  <span className="text-white/10">|</span>
                  <span>{a.time}</span>
                </div>
              </div>
            </div>
          );
        }) : (
          <div className="py-16 text-center text-muted-foreground">
            <Shield className="w-10 h-10 mx-auto mb-4 opacity-20" />
            <p className="text-base font-medium text-foreground/80">No threats detected</p>
            <p className="text-[15px] font-medium mt-1.5 opacity-60">No alerts match the selected severity filter.</p>
          </div>
        )}
      </div>
    </div>
  );
}
