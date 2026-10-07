import { ShieldAlert, Crosshair, AlertTriangle, ArrowRight } from "lucide-react";

const miniAlerts = [
  {
    id: 1,
    type: "Port Scan Detected",
    desc: "Rapid connection sweep",
    src: "192.168.1.105",
    sev: "high" as const,
    Icon: Crosshair,
  },
  {
    id: 2,
    type: "Malware Signature",
    desc: "C2 beacon fingerprint",
    src: "45.33.22.1",
    sev: "high" as const,
    Icon: ShieldAlert,
  },
  {
    id: 3,
    type: "Unusual Data Transfer",
    desc: "8.4 GB outbound",
    src: "192.168.1.42",
    sev: "medium" as const,
    Icon: AlertTriangle,
  },
];

const miniSevMap = {
  high:   { icon: "text-red-400", bg: "bg-red-500/10", border: "border-red-500/30", badge: "text-red-400 border-red-500/30 bg-red-500/10 shadow-[0_0_8px_rgba(239,68,68,0.2)]" },
  medium: { icon: "text-amber-400", bg: "bg-amber-500/10", border: "border-amber-500/30", badge: "text-amber-400 border-amber-500/30 bg-amber-500/10 shadow-[0_0_8px_rgba(245,158,11,0.2)]" },
};

export function MiniAlertsPanel() {
  return (
    <div className="glass-panel rounded-xl h-full flex flex-col overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-black/20">
        <div>
          <h2 className="text-[13px] font-bold text-foreground uppercase tracking-widest">Recent Alerts</h2>
        </div>
        <span className="text-[11px] font-bold text-red-400 bg-red-500/10 border border-red-500/20 px-2 py-1 rounded shadow-[0_0_8px_rgba(239,68,68,0.2)] uppercase tracking-widest flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
          Critical
        </span>
      </div>

      <div className="flex-1 p-2 flex flex-col justify-between">
        {miniAlerts.map((a) => {
          const s = miniSevMap[a.sev];
          return (
            <div key={a.id} className="flex gap-3 px-4 py-3 hover:bg-white/5 rounded-lg transition-all group">
              <div className={`w-8 h-8 rounded-lg shrink-0 flex items-center justify-center border ${s.bg} ${s.border}`}>
                <a.Icon className={`w-4 h-4 ${s.icon}`} />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-[14px] font-bold text-foreground leading-tight truncate">{a.type}</p>
                <p className="text-[12px] text-muted-foreground mt-0.5 truncate font-medium">{a.desc}</p>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
