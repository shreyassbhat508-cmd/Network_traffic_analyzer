import { AlertTriangle, ShieldAlert, Shield, Crosshair, ArrowRight } from "lucide-react";

const alerts = [
  {
    id: 1,
    type: "Port Scan Detected",
    desc: "Rapid connection sweep across 1,024 ports",
    src: "192.168.1.105",
    dst: "10.0.0.1",
    time: "2m ago",
    sev: "high" as const,
    Icon: Crosshair,
  },
  {
    id: 2,
    type: "Unusual Data Transfer",
    desc: "8.4 GB outbound to unknown external host",
    src: "192.168.1.42",
    dst: "8.8.4.4",
    time: "15m ago",
    sev: "medium" as const,
    Icon: AlertTriangle,
  },
  {
    id: 3,
    type: "Malware Signature Match",
    desc: "Packet payload matches known C2 fingerprint",
    src: "45.33.22.1",
    dst: "192.168.1.10",
    time: "2h ago",
    sev: "high" as const,
    Icon: ShieldAlert,
  },
  {
    id: 4,
    type: "SSH Brute-force Attempt",
    desc: "147 failed logins from single source IP",
    src: "172.16.0.5",
    dst: "SSH Server",
    time: "3h ago",
    sev: "low" as const,
    Icon: Shield,
  },
];

const sevMap = {
  high:   { bar: "bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.8)]",    text: "text-red-400",    bg: "bg-red-500/10",    border: "border-red-500/20",    badge: "text-red-400 bg-red-500/10 border-red-500/20 shadow-[0_0_8px_rgba(239,68,68,0.15)]" },
  medium: { bar: "bg-amber-500 shadow-[0_0_10px_rgba(245,158,11,0.8)]",  text: "text-amber-400",  bg: "bg-amber-500/10",  border: "border-amber-500/20",  badge: "text-amber-400 bg-amber-500/10 border-amber-500/20 shadow-[0_0_8px_rgba(245,158,11,0.15)]" },
  low:    { bar: "bg-blue-500 shadow-[0_0_10px_rgba(59,130,246,0.8)]",   text: "text-blue-400",   bg: "bg-blue-500/10",   border: "border-blue-500/20",   badge: "text-blue-400 bg-blue-500/10 border-blue-500/20 shadow-[0_0_8px_rgba(59,130,246,0.15)]" },
};

export function AlertsPanel() {
  return (
    <div className="glass-panel rounded-xl h-full flex flex-col overflow-hidden">
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-black/20">
        <div>
          <h2 className="text-[13px] font-bold text-foreground uppercase tracking-widest">Security Alerts</h2>
          <p className="text-[13px] text-muted-foreground mt-0.5 font-medium">Recent suspicious activities</p>
        </div>
        <span className="text-[11px] font-bold text-red-400 bg-red-500/10 border border-red-500/20 px-2.5 py-1 rounded shadow-[0_0_8px_rgba(239,68,68,0.2)] uppercase tracking-widest flex items-center gap-1.5">
          <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
          {alerts.filter(a => a.sev === "high").length} Critical
        </span>
      </div>

      <div className="flex-1 divide-y divide-white/5 p-2">
        {alerts.map((a) => {
          const s = sevMap[a.sev];
          return (
            <div key={a.id} className="flex gap-4 px-4 py-3.5 hover:bg-white/5 rounded-lg transition-all border border-transparent hover:border-white/5 group">
              {/* Severity stripe */}
              <div className={`w-0.5 rounded-full self-stretch shrink-0 ${s.bar}`} />

              {/* Icon */}
              <div className={`w-8 h-8 rounded-lg shrink-0 flex items-center justify-center border ${s.bg} ${s.border} group-hover:bg-opacity-20 transition-colors`}>
                <a.Icon className={`w-4 h-4 ${s.text}`} />
              </div>

              {/* Body */}
              <div className="flex-1 min-w-0 flex flex-col justify-center">
                <div className="flex items-start justify-between gap-2">
                  <p className="text-[15px] font-semibold text-foreground leading-tight tracking-wide">{a.type}</p>
                  <span className="text-[12px] text-muted-foreground whitespace-nowrap font-medium">{a.time}</span>
                </div>
                <p className="text-[13px] text-muted-foreground mt-1 leading-tight truncate">{a.desc}</p>
                <div className="flex items-center gap-1.5 mt-2">
                  <span className="text-[12px] font-mono font-medium text-muted-foreground/80 bg-black/30 px-1.5 py-0.5 rounded border border-white/5">{a.src}</span>
                  <ArrowRight className="w-2.5 h-2.5 text-muted-foreground/40" />
                  <span className="text-[12px] font-mono font-medium text-muted-foreground/80 truncate bg-black/30 px-1.5 py-0.5 rounded border border-white/5">{a.dst}</span>
                </div>
              </div>

              {/* Severity badge */}
              <div className={`self-start shrink-0 text-[11px] uppercase font-bold px-2 py-0.5 rounded border tracking-widest ${s.badge}`}>
                {a.sev}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
