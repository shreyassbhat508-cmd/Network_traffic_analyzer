"use client";

import {
  PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend,
  AreaChart, Area, XAxis, YAxis, CartesianGrid,
} from "recharts";
import type { AnimationIntensity } from "@/lib/workspace-context";

const protocols = [
  { name: "TCP", value: 68 },
  { name: "UDP", value: 24 },
  { name: "ICMP", value: 5 },
  { name: "DNS", value: 3 },
];

const protocolColors = ["#48c8ed", "#6289e8", "#9b8bdf", "#d6a764"];
const trafficData = [
  { time: "10:00", packets: 42_000 },
  { time: "10:05", packets: 56_000 },
  { time: "10:10", packets: 49_000 },
  { time: "10:15", packets: 71_000 },
  { time: "10:20", packets: 66_000 },
  { time: "10:25", packets: 88_000 },
  { time: "10:30", packets: 76_000 },
];

const tooltipStyle: React.CSSProperties = {
  backgroundColor: "#171e27",
  border: "1px solid rgba(199, 214, 228, 0.14)",
  borderRadius: "7px",
  padding: "9px 12px",
  fontSize: "13px",
  color: "#e7edf3",
  boxShadow: "0 8px 22px rgba(0,0,0,0.35)",
};

export function Charts({ motion = "full" }: { motion?: AnimationIntensity }) {
  const chartAnimation = motion === "full";

  return (
    <div className="grid gap-4 md:grid-cols-[minmax(0,1.55fr)_minmax(250px,0.9fr)]">
      <section className="glass-panel min-w-0">
        <div className="flex items-start justify-between gap-3 border-b border-white/[0.08] px-4 py-3.5 sm:px-5">
          <div>
            <h2 className="text-[14px] font-semibold text-foreground">Traffic over time</h2>
            <p className="mt-1 text-[12px] text-muted-foreground">Packet volume · 5 minute intervals</p>
          </div>
          <span className="rounded border border-white/[0.08] px-2 py-1 font-mono text-[10px] text-muted-foreground">SAMPLE</span>
        </div>
        <div className="h-[235px] px-2 pb-3 pt-4">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={trafficData} margin={{ top: 6, right: 12, left: -15, bottom: 0 }}>
              <defs>
                <linearGradient id="trafficFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#48c8ed" stopOpacity={0.2} />
                  <stop offset="100%" stopColor="#48c8ed" stopOpacity={0.01} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="2 5" stroke="rgba(214,226,238,0.08)" vertical={false} />
              <XAxis dataKey="time" tick={{ fontSize: 11, fill: "#82909e" }} tickLine={false} axisLine={false} dy={8} />
              <YAxis tick={{ fontSize: 11, fill: "#82909e" }} tickLine={false} axisLine={false} tickFormatter={value => `${Math.round(value / 1000)}k`} />
              <Tooltip contentStyle={tooltipStyle} formatter={value => [Number(value).toLocaleString(), "Packets"]} labelFormatter={label => `${label} · sample`} />
              <Area type="monotone" dataKey="packets" stroke="#48c8ed" strokeWidth={2} fill="url(#trafficFill)" isAnimationActive={chartAnimation} animationDuration={650} dot={false} activeDot={{ r: 3.5, fill: "#e7edf3", stroke: "#48c8ed", strokeWidth: 2 }} />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </section>

      <section className="glass-panel min-w-0">
        <div className="border-b border-white/[0.08] px-4 py-3.5 sm:px-5">
          <h2 className="text-[14px] font-semibold text-foreground">Protocol mix</h2>
          <p className="mt-1 text-[12px] text-muted-foreground">Share of sample packets</p>
        </div>
        <div className="h-[235px] px-3 pb-2 pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie data={protocols} cx="50%" cy="45%" innerRadius={54} outerRadius={78} paddingAngle={2} dataKey="value" stroke="none" isAnimationActive={chartAnimation} animationDuration={650}>
                {protocols.map((protocol, index) => <Cell key={protocol.name} fill={protocolColors[index]} />)}
              </Pie>
              <Tooltip contentStyle={tooltipStyle} formatter={value => [`${value}%`, "Share"]} cursor={false} />
              <Legend verticalAlign="bottom" iconType="circle" iconSize={6} wrapperStyle={{ fontSize: "12px", color: "#aab5c0", paddingTop: "6px" }} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>
    </div>
  );
}
