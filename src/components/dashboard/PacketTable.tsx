"use client";

import { useState } from "react";
import { Search } from "lucide-react";

const PROTOCOLS = ["All", "TCP", "UDP", "ICMP", "DNS"];

const packets = [
  { id:  1, time: "10:24:11.241", src: "192.168.1.105", sp: 54321, dst: "10.0.0.1",       dp: 443,   proto: "TCP",  size: 1420, flag: false },
  { id:  2, time: "10:24:11.503", src: "10.0.0.1",       sp: 443,   dst: "192.168.1.105", dp: 54321, proto: "TCP",  size: 64,   flag: false },
  { id:  3, time: "10:24:12.012", src: "192.168.1.42",   sp: 123,   dst: "8.8.8.8",        dp: 123,   proto: "UDP",  size: 90,   flag: false },
  { id:  4, time: "10:24:12.899", src: "192.168.1.10",   sp: 53,    dst: "1.1.1.1",         dp: 53,    proto: "DNS",  size: 128,  flag: false },
  { id:  5, time: "10:24:13.104", src: "172.16.0.5",     sp: 3389,  dst: "192.168.1.200",  dp: 49152, proto: "TCP",  size: 1514, flag: true  },
  { id:  6, time: "10:24:13.444", src: "192.168.1.105",  sp: 0,     dst: "10.0.0.1",        dp: 0,     proto: "ICMP", size: 64,   flag: false },
  { id:  7, time: "10:24:14.221", src: "45.33.22.1",     sp: 443,   dst: "192.168.1.10",   dp: 55432, proto: "TCP",  size: 1420, flag: true  },
  { id:  8, time: "10:24:14.901", src: "192.168.1.105",  sp: 54322, dst: "10.0.0.1",        dp: 443,   proto: "TCP",  size: 1420, flag: false },
  { id:  9, time: "10:24:15.003", src: "8.8.8.8",         sp: 53,    dst: "192.168.1.10",   dp: 4422,  proto: "DNS",  size: 112,  flag: false },
  { id: 10, time: "10:24:15.188", src: "192.168.1.200",  sp: 49152, dst: "172.16.0.5",      dp: 3389,  proto: "TCP",  size: 512,  flag: false },
];

const protoBg: Record<string, string> = {
  TCP:  "text-blue-400  bg-blue-500/10  border-blue-500/20 shadow-[0_0_8px_rgba(59,130,246,0.15)]",
  UDP:  "text-cyan-400  bg-cyan-500/10  border-cyan-500/20 shadow-[0_0_8px_rgba(6,182,212,0.15)]",
  ICMP: "text-violet-400 bg-violet-500/10 border-violet-500/20 shadow-[0_0_8px_rgba(139,92,246,0.15)]",
  DNS:  "text-amber-400 bg-amber-500/10 border-amber-500/20 shadow-[0_0_8px_rgba(245,158,11,0.15)]",
};

export function PacketTable() {
  const [query, setQuery] = useState("");
  const [proto, setProto] = useState("All");

  const rows = packets.filter(p => {
    const matchProto = proto === "All" || p.proto === proto;
    const q = query.toLowerCase();
    const matchQ = !q || p.src.includes(q) || p.dst.includes(q) || p.proto.toLowerCase().includes(q);
    return matchProto && matchQ;
  });

  return (
    <div className="glass-panel rounded-xl overflow-hidden flex flex-col">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 px-6 py-4 border-b border-white/5 bg-black/20">
        <div>
          <h2 className="text-[13px] font-bold text-foreground uppercase tracking-widest">Packet Inspection</h2>
          <p className="text-[13px] text-muted-foreground mt-0.5 font-medium">
            Showing {rows.length} of {packets.length} demo packets
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          {/* Protocol filter pills */}
          <div className="flex items-center gap-1.5 bg-black/30 p-1 rounded-lg border border-white/5">
            {PROTOCOLS.map(p => (
              <button
                key={p}
                onClick={() => setProto(p)}
                className={`px-3 py-1 rounded-md text-[12px] font-bold uppercase tracking-widest transition-all ${
                  proto === p
                    ? "bg-primary/20 text-primary border border-primary/30 shadow-[0_0_10px_rgba(59,130,246,0.2)]"
                    : "text-muted-foreground hover:bg-white/5 hover:text-foreground border border-transparent"
                }`}
              >
                {p}
              </button>
            ))}
          </div>
          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground pointer-events-none" />
            <input
              type="text"
              value={query}
              onChange={e => setQuery(e.target.value)}
              placeholder="Search IP or protocol…"
              className="w-56 h-8 pl-9 pr-3 rounded-lg text-[13px] font-mono bg-black/30 border border-white/10 text-foreground placeholder:text-muted-foreground/50 focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-all shadow-inner"
            />
          </div>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-[13px] font-mono">
          <thead>
            <tr className="border-b border-white/5 bg-black/40">
              {["#", "Timestamp", "Source", "Destination", "Proto", "Size", "Flag"].map(h => (
                <th
                  key={h}
                  className="px-6 py-3 text-left font-bold uppercase tracking-widest text-muted-foreground/60 whitespace-nowrap"
                >
                  {h}
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {rows.length > 0 ? rows.map(p => (
              <tr key={p.id} className="hover:bg-white/5 transition-colors group">
                <td className="px-6 py-3 text-muted-foreground/40 font-semibold">{String(p.id).padStart(2, "0")}</td>
                <td className="px-6 py-3 text-muted-foreground font-medium">{p.time}</td>
                <td className="px-6 py-3 whitespace-nowrap">
                  <span className="text-foreground/90">{p.src}</span>
                  <span className="text-muted-foreground/50">:{p.sp}</span>
                </td>
                <td className="px-6 py-3 whitespace-nowrap">
                  <span className="text-foreground/90">{p.dst}</span>
                  <span className="text-muted-foreground/50">:{p.dp}</span>
                </td>
                <td className="px-6 py-3">
                  <span className={`inline-block px-1.5 py-0.5 rounded border text-[11px] font-bold uppercase tracking-widest ${protoBg[p.proto] ?? "text-muted-foreground bg-white/5 border-white/10"}`}>
                    {p.proto}
                  </span>
                </td>
                <td className="px-6 py-3 text-muted-foreground/80 tabular-nums font-medium">{p.size} B</td>
                <td className="px-6 py-3">
                  {p.flag && (
                    <span className="inline-block w-2 h-2 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.8)] animate-pulse" title="Suspicious packet" />
                  )}
                </td>
              </tr>
            )) : (
              <tr>
                <td colSpan={7} className="px-6 py-12 text-center text-muted-foreground">
                  <Search className="w-6 h-6 mx-auto mb-3 opacity-20" />
                  <p className="text-sm font-sans font-medium">No packets match your filters</p>
                  <p className="text-xs font-sans mt-1 opacity-50">Try a different search query or protocol</p>
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
