const sources = [
  { ip: "192.168.1.105", count: "45,210", pct: 32, internal: true  },
  { ip: "192.168.1.42",  count: "12,400", pct: 9,  internal: true  },
  { ip: "45.33.22.1",    count: "8,920",  pct: 6,  internal: false },
  { ip: "10.0.0.1",      count: "5,110",  pct: 4,  internal: true  },
  { ip: "172.16.0.5",    count: "3,200",  pct: 2,  internal: true  },
];

const dests = [
  { ip: "10.0.0.1",       count: "50,102", pct: 35, internal: true  },
  { ip: "8.8.8.8",        count: "14,200", pct: 10, internal: false },
  { ip: "192.168.1.105",  count: "11,500", pct: 8,  internal: true  },
  { ip: "1.1.1.1",        count: "6,200",  pct: 4,  internal: false },
  { ip: "192.168.1.200",  count: "4,100",  pct: 3,  internal: true  },
];

function IpTable({ rows }: { rows: typeof sources }) {
  return (
    <div className="space-y-1">
      {rows.map((r, i) => (
        <div key={i} className="flex items-center gap-3 py-2.5 px-4 rounded-lg hover:bg-white/5 border border-transparent hover:border-white/5 transition-all group">
          <span className="w-5 text-[13px] text-muted-foreground/60 font-mono font-semibold text-right">{i + 1}</span>
          <span className="flex-1 font-mono text-[15px] font-medium text-foreground/90 truncate tracking-wide">{r.ip}</span>
          <span
            className={`text-[11px] px-1.5 py-0.5 rounded border uppercase tracking-widest font-bold ${
              r.internal
                ? "text-blue-400 bg-blue-500/10 border-blue-500/20 shadow-[0_0_8px_rgba(59,130,246,0.15)]"
                : "text-purple-400 bg-purple-500/10 border-purple-500/20 shadow-[0_0_8px_rgba(168,85,247,0.15)]"
            }`}
          >
            {r.internal ? "INT" : "EXT"}
          </span>
          <div className="flex items-center gap-3 w-32">
            <div className="flex-1 h-1.5 rounded-full bg-black/40 overflow-hidden border border-white/5">
              <div className="h-full bg-gradient-to-r from-primary/50 to-primary rounded-full shadow-[0_0_5px_rgba(59,130,246,0.8)]" style={{ width: `${r.pct * 2.5}%` }} />
            </div>
            <span className="text-[13px] font-mono font-medium text-muted-foreground w-12 text-right">{r.count}</span>
          </div>
        </div>
      ))}
    </div>
  );
}

export function TopIps() {
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <div className="glass-panel rounded-xl flex flex-col">
        <div className="px-6 py-4 border-b border-white/5 bg-black/20">
          <h2 className="text-[13px] font-bold text-foreground uppercase tracking-widest">Top Source IPs</h2>
          <p className="text-[13px] text-muted-foreground mt-0.5 font-medium">Highest-volume traffic originators</p>
        </div>
        <div className="p-3">
          <IpTable rows={sources} />
        </div>
      </div>

      <div className="glass-panel rounded-xl flex flex-col">
        <div className="px-6 py-4 border-b border-white/5 bg-black/20">
          <h2 className="text-[13px] font-bold text-foreground uppercase tracking-widest">Top Destination IPs</h2>
          <p className="text-[13px] text-muted-foreground mt-0.5 font-medium">Most frequently targeted hosts</p>
        </div>
        <div className="p-3">
          <IpTable rows={dests} />
        </div>
      </div>
    </div>
  );
}
