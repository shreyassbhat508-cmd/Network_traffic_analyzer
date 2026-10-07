"use client";

import { useEffect, useMemo, useState } from "react";
import { ChevronLeft, ChevronRight, Search, X } from "lucide-react";
import { useWorkspacePreferences } from "@/lib/workspace-context";

const PROTOCOLS = ["All", "TCP", "UDP", "ICMP", "DNS"] as const;

export const PACKETS = [
  { id: 1, time: "10:24:11.241", src: "192.168.1.105", sp: 54321, dst: "10.0.0.1", dp: 443, proto: "TCP", size: 1420, flag: false },
  { id: 2, time: "10:24:11.503", src: "10.0.0.1", sp: 443, dst: "192.168.1.105", dp: 54321, proto: "TCP", size: 64, flag: false },
  { id: 3, time: "10:24:12.012", src: "192.168.1.42", sp: 123, dst: "8.8.8.8", dp: 123, proto: "UDP", size: 90, flag: false },
  { id: 4, time: "10:24:12.899", src: "192.168.1.10", sp: 53, dst: "1.1.1.1", dp: 53, proto: "DNS", size: 128, flag: false },
  { id: 5, time: "10:24:13.104", src: "172.16.0.5", sp: 3389, dst: "192.168.1.200", dp: 49152, proto: "TCP", size: 1514, flag: true },
  { id: 6, time: "10:24:13.444", src: "192.168.1.105", sp: 0, dst: "10.0.0.1", dp: 0, proto: "ICMP", size: 64, flag: false },
  { id: 7, time: "10:24:14.221", src: "45.33.22.1", sp: 443, dst: "192.168.1.10", dp: 55432, proto: "TCP", size: 1420, flag: true },
  { id: 8, time: "10:24:14.901", src: "192.168.1.105", sp: 54322, dst: "10.0.0.1", dp: 443, proto: "TCP", size: 1420, flag: false },
  { id: 9, time: "10:24:15.003", src: "8.8.8.8", sp: 53, dst: "192.168.1.10", dp: 4422, proto: "DNS", size: 112, flag: false },
  { id: 10, time: "10:24:15.188", src: "192.168.1.200", sp: 49152, dst: "172.16.0.5", dp: 3389, proto: "TCP", size: 512, flag: false },
  { id: 11, time: "10:24:15.299", src: "192.168.1.105", sp: 54323, dst: "10.0.0.2", dp: 8080, proto: "TCP", size: 256, flag: false },
  { id: 12, time: "10:24:15.411", src: "10.0.0.1", sp: 80, dst: "192.168.1.10", dp: 50230, proto: "TCP", size: 1200, flag: false },
];

type Packet = (typeof PACKETS)[number];
const protocolClass: Record<string, string> = {
  TCP: "border-blue-400/20 bg-blue-400/[0.08] text-blue-200",
  UDP: "border-cyan-300/20 bg-cyan-300/[0.08] text-cyan-200",
  ICMP: "border-violet-300/20 bg-violet-300/[0.08] text-violet-200",
  DNS: "border-amber-300/20 bg-amber-300/[0.08] text-amber-200",
};

function PacketDetails({ packet, onClose }: { packet: Packet; onClose: () => void }) {
  useEffect(() => {
    const handleKey = (event: KeyboardEvent) => { if (event.key === "Escape") onClose(); };
    window.addEventListener("keydown", handleKey);
    return () => window.removeEventListener("keydown", handleKey);
  }, [onClose]);

  const details = [
    ["Timestamp", packet.time], ["Protocol", packet.proto], ["Source address", packet.src],
    ["Source port", String(packet.sp)], ["Destination address", packet.dst],
    ["Destination port", String(packet.dp)], ["Packet size", `${packet.size} bytes`],
    ["Sample flag", packet.flag ? "Flagged in demo data" : "Not flagged"],
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 p-4" onMouseDown={event => { if (event.target === event.currentTarget) onClose(); }}>
      <section role="dialog" aria-modal="true" aria-labelledby="packet-detail-title" className="w-full max-w-lg rounded-xl border border-white/10 bg-[#141a22] shadow-2xl">
        <div className="flex items-start justify-between border-b border-white/[0.08] px-5 py-4">
          <div><p className="font-mono text-[11px] text-primary">SAMPLE RECORD · #{String(packet.id).padStart(2, "0")}</p><h2 id="packet-detail-title" className="mt-1 text-[18px] font-semibold text-foreground">Packet details</h2></div>
          <button type="button" onClick={onClose} aria-label="Close packet details" className="grid h-8 w-8 place-items-center rounded text-muted-foreground hover:bg-white/[0.06] hover:text-foreground"><X className="h-4 w-4" /></button>
        </div>
        <dl className="grid grid-cols-1 gap-x-6 px-5 py-3 sm:grid-cols-2">
          {details.map(([label, value]) => <div key={label} className="border-b border-white/[0.06] py-3"><dt className="text-[12px] text-muted-foreground">{label}</dt><dd className="mt-1 break-all font-mono text-[13px] text-foreground">{value}</dd></div>)}
        </dl>
        <p className="px-5 pb-4 text-[12px] leading-relaxed text-muted-foreground">Sample records are included for interface preview and are not from a connected capture.</p>
      </section>
    </div>
  );
}

export function PacketSearchView() {
  const [query, setQuery] = useState("");
  const [protocol, setProtocol] = useState<(typeof PROTOCOLS)[number]>("All");
  const [flaggedOnly, setFlaggedOnly] = useState(false);
  const [page, setPage] = useState(1);
  const [selectedPacket, setSelectedPacket] = useState<Packet | null>(null);
  const { compactTables, rowsPerPage, showTimestamps } = useWorkspacePreferences();

  const filtered = useMemo(() => {
    const search = query.trim().toLowerCase();
    return PACKETS.filter(packet => {
      const matchesProtocol = protocol === "All" || packet.proto === protocol;
      const matchesFlag = !flaggedOnly || packet.flag;
      const matchesSearch = !search || [packet.id, packet.time, packet.src, packet.sp, packet.dst, packet.dp, packet.proto, packet.size].some(value => String(value).toLowerCase().includes(search));
      return matchesProtocol && matchesFlag && matchesSearch;
    });
  }, [query, protocol, flaggedOnly]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / rowsPerPage));
  const currentPage = Math.min(page, pageCount);
  const pageRows = filtered.slice((currentPage - 1) * rowsPerPage, currentPage * rowsPerPage);
  const firstResult = filtered.length ? (currentPage - 1) * rowsPerPage + 1 : 0;
  const lastResult = Math.min(currentPage * rowsPerPage, filtered.length);
  const rowPadding = compactTables ? "py-2" : "py-3";

  return (
    <section className="space-y-5">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div><p className="mb-1.5 font-mono text-[12px] text-primary">DEMO CAPTURE 04 · 12 RECORDS</p><h1 className="text-[26px] font-semibold tracking-[-0.035em] text-foreground">Packet search</h1><p className="mt-1 text-[14px] text-muted-foreground">Search sample packet metadata and inspect individual records.</p></div>
        <span className="rounded border border-white/10 px-2.5 py-1.5 font-mono text-[11px] text-muted-foreground">SAMPLE DATA</span>
      </div>

      <div className="glass-panel flex flex-wrap items-center gap-3 p-3">
        <label className="relative min-w-[220px] flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <input value={query} onChange={event => { setQuery(event.target.value); setPage(1); }} placeholder="Search IP, port, timestamp, protocol…" className="h-9 w-full rounded-md border border-white/10 bg-black/20 pl-9 pr-3 text-[13px] text-foreground placeholder:text-muted-foreground/70" />
        </label>
        <div role="group" aria-label="Filter by protocol" className="flex max-w-full gap-1 overflow-x-auto rounded-md border border-white/[0.08] bg-black/15 p-1">
          {PROTOCOLS.map(item => <button key={item} type="button" aria-pressed={protocol === item} onClick={() => { setProtocol(item); setPage(1); }} className={`rounded px-2.5 py-1.5 text-[12px] transition-colors ${protocol === item ? "bg-primary/[0.12] text-primary" : "text-muted-foreground hover:bg-white/[0.05] hover:text-foreground"}`}>{item}</button>)}
        </div>
        <button type="button" aria-pressed={flaggedOnly} onClick={() => { setFlaggedOnly(value => !value); setPage(1); }} className={`flex h-9 items-center gap-2 rounded-md border px-3 text-[12px] transition-colors ${flaggedOnly ? "border-red-300/25 bg-red-300/[0.08] text-red-200" : "border-white/10 text-muted-foreground hover:text-foreground"}`}><span className={`h-1.5 w-1.5 rounded-full ${flaggedOnly ? "bg-red-300" : "bg-muted-foreground/50"}`} /> Flagged only</button>
      </div>

      <div className="flex flex-wrap items-center justify-between gap-2 text-[12px] text-muted-foreground">
        <p>Showing <span className="font-mono text-foreground">{firstResult}–{lastResult}</span> of <span className="font-mono text-foreground">{filtered.length}</span> matching sample records</p>
        <p className="font-mono">PAGE {currentPage} / {pageCount} · {rowsPerPage} PER PAGE</p>
      </div>

      <div className="glass-panel overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[760px] text-left">
            <thead><tr className="border-b border-white/[0.08] bg-white/[0.02] text-[11px] font-medium text-muted-foreground">
              <th className="px-4 py-3 font-medium">Record</th>{showTimestamps && <th className="px-4 py-3 font-medium">Timestamp</th>}<th className="px-4 py-3 font-medium">Source</th><th className="px-4 py-3 font-medium">Destination</th><th className="px-4 py-3 font-medium">Protocol</th><th className="px-4 py-3 text-right font-medium">Size</th><th className="px-4 py-3 font-medium">Flag</th>
            </tr></thead>
            <tbody className="divide-y divide-white/[0.06]">
              {pageRows.map(packet => <tr key={packet.id} className="transition-colors hover:bg-white/[0.025]">
                <td className={`px-4 ${rowPadding}`}><button type="button" onClick={() => setSelectedPacket(packet)} className="font-mono text-[12px] text-primary hover:text-foreground">#{String(packet.id).padStart(2, "0")}</button></td>
                {showTimestamps && <td className={`whitespace-nowrap px-4 ${rowPadding} font-mono text-[12px] text-muted-foreground`}>{packet.time}</td>}
                <td className={`whitespace-nowrap px-4 ${rowPadding}`}><span className="font-mono text-[12px] text-foreground">{packet.src}</span><span className="font-mono text-[11px] text-muted-foreground">:{packet.sp}</span></td>
                <td className={`whitespace-nowrap px-4 ${rowPadding}`}><span className="font-mono text-[12px] text-foreground">{packet.dst}</span><span className="font-mono text-[11px] text-muted-foreground">:{packet.dp}</span></td>
                <td className={`px-4 ${rowPadding}`}><span className={`rounded border px-1.5 py-1 font-mono text-[11px] ${protocolClass[packet.proto]}`}>{packet.proto}</span></td>
                <td className={`px-4 ${rowPadding} text-right font-mono text-[12px] tabular-nums text-muted-foreground`}>{packet.size.toLocaleString()} B</td>
                <td className={`px-4 ${rowPadding}`}>{packet.flag ? <span className="rounded border border-red-300/20 bg-red-300/[0.07] px-1.5 py-1 text-[11px] text-red-200">Flagged</span> : <span className="text-[12px] text-muted-foreground/60">—</span>}</td>
              </tr>)}
              {pageRows.length === 0 && <tr><td colSpan={showTimestamps ? 7 : 6} className="px-4 py-14 text-center"><Search className="mx-auto mb-3 h-5 w-5 text-muted-foreground/60" /><p className="text-[14px] font-medium text-foreground">No matching packets</p><p className="mt-1 text-[12px] text-muted-foreground">Try another search or filter.</p></td></tr>}
            </tbody>
          </table>
        </div>
        <div className="flex items-center justify-between border-t border-white/[0.08] px-4 py-3">
          <p className="text-[11px] text-muted-foreground">Packet contents are illustrative sample data.</p>
          <div className="flex items-center gap-2">
            <button type="button" disabled={currentPage <= 1} onClick={() => setPage(value => Math.max(1, value - 1))} aria-label="Previous page" className="grid h-7 w-7 place-items-center rounded border border-white/10 text-muted-foreground enabled:hover:text-foreground disabled:opacity-35"><ChevronLeft className="h-3.5 w-3.5" /></button>
            <button type="button" disabled={currentPage >= pageCount} onClick={() => setPage(value => Math.min(pageCount, value + 1))} aria-label="Next page" className="grid h-7 w-7 place-items-center rounded border border-white/10 text-muted-foreground enabled:hover:text-foreground disabled:opacity-35"><ChevronRight className="h-3.5 w-3.5" /></button>
          </div>
        </div>
      </div>
      {selectedPacket && <PacketDetails packet={selectedPacket} onClose={() => setSelectedPacket(null)} />}
    </section>
  );
}
