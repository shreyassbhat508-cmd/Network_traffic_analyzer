"use client";

import { Activity, Globe2, ShieldAlert, Waypoints } from "lucide-react";

const METRICS = [
  { label: "Total packets", value: 1_245_082, Icon: Activity, tone: "text-primary" },
  { label: "Unique endpoints", value: 842, Icon: Globe2, tone: "text-cyan-200" },
  { label: "Active protocols", value: 14, Icon: Waypoints, tone: "text-violet-300" },
  { label: "Security alerts", value: 3, Icon: ShieldAlert, tone: "text-[#ed9387]" },
];

export function OverviewCards() {
  return (
    <section aria-label="Capture summary" className="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
      {METRICS.map(({ label, value, Icon, tone }, index) => (
        <div
          key={label}
          className="glass-panel flex min-h-[104px] flex-col justify-between px-4 py-3.5"
          style={{ animationDelay: `${index * 65}ms` }}
        >
          <div className="flex items-center justify-between gap-2">
            <p className="text-[13px] font-medium text-muted-foreground">{label}</p>
            <Icon aria-hidden="true" className={`h-3.5 w-3.5 ${tone}`} strokeWidth={1.8} />
          </div>
          <p className="font-mono text-[27px] font-medium leading-none tracking-[-0.045em] text-foreground tabular-nums">
            {value.toLocaleString("en-US")}
          </p>
        </div>
      ))}
    </section>
  );
}
