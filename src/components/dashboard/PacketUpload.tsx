"use client";

import { useState } from "react";
import { UploadCloud, CheckCircle, AlertCircle, FilePlus2, FolderOpen } from "lucide-react";

type Status = "idle" | "uploading" | "success" | "error";

export function PacketUpload() {
  const [dragActive, setDragActive] = useState(false);
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [progress, setProgress] = useState(0);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(e.type === "dragenter" || e.type === "dragover");
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files?.[0]) handleFile(e.dataTransfer.files[0]);
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) handleFile(e.target.files[0]);
  };

  const handleFile = (f: File) => {
    const valid = [".pcap", ".pcapng"].some(ext => f.name.toLowerCase().endsWith(ext));
    if (!valid) { setStatus("error"); return; }
    setFile(f);
    setStatus("uploading");
    setProgress(0);
    const iv = setInterval(() => {
      setProgress(p => {
        if (p >= 100) { clearInterval(iv); setStatus("success"); return 100; }
        return p + Math.random() * 18;
      });
    }, 120);
  };

  const reset = (e: React.MouseEvent) => {
    e.stopPropagation();
    setStatus("idle");
    setFile(null);
    setProgress(0);
  };

  return (
    <div className="glass-panel rounded-xl flex flex-col h-full relative overflow-hidden">
      {/* Header */}
      <div className="flex items-center justify-between px-6 py-4 border-b border-white/5 bg-black/20">
        <div>
          <h2 className="text-[13px] font-bold text-foreground uppercase tracking-widest">Import Packet Capture</h2>
          <p className="text-[13px] text-muted-foreground mt-0.5 font-medium">Upload a PCAP or PCAPNG file for demo analysis</p>
        </div>
        <span className="text-[11px] font-bold text-cyan-400 bg-cyan-400/10 border border-cyan-400/25 px-2 py-1 rounded shadow-[0_0_8px_rgba(6,182,212,0.2)] uppercase tracking-widest">
          Analysis Node
        </span>
      </div>

      {/* Drop zone */}
      <div className="p-6 flex-1 flex flex-col">
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          className={`relative rounded-xl border border-dashed transition-all duration-300 flex-1 flex flex-col items-center justify-center py-10 px-6 text-center select-none ${
            status === "idle"
              ? dragActive
                ? "border-primary bg-primary/10 shadow-[0_0_30px_rgba(59,130,246,0.15)] scale-[1.01]"
                : "border-white/10 hover:border-white/30 hover:bg-white/5 cursor-pointer"
              : status === "success"
              ? "border-emerald-500/30 bg-emerald-500/5 shadow-[0_0_20px_rgba(16,185,129,0.1)]"
              : status === "error"
              ? "border-red-500/30 bg-red-500/5 shadow-[0_0_20px_rgba(239,68,68,0.1)]"
              : "border-white/10 bg-black/20"
          }`}
        >
          {/* Invisible file input covering drop zone */}
          {(status === "idle" || status === "error") && (
            <input
              type="file"
              accept=".pcap,.pcapng"
              onChange={handleChange}
              className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
            />
          )}

          {status === "idle" && (
            <>
              <div className="w-14 h-14 rounded-full border border-white/10 bg-black/40 flex items-center justify-center mb-5 shadow-inner transition-transform group-hover:scale-110">
                <UploadCloud className="w-6 h-6 text-muted-foreground" />
              </div>
              <p className="text-[15px] font-semibold text-foreground mb-1.5 tracking-wide">
                {dragActive ? "Drop the file to begin" : "Drag & drop your capture file"}
              </p>
              <p className="text-[13px] text-muted-foreground mb-5 font-mono">PCAP or PCAPNG · MAX 50MB</p>
              <div className="inline-flex items-center gap-2 px-5 py-2.5 rounded-lg bg-white/5 border border-white/10 text-[13px] font-bold text-foreground uppercase tracking-widest hover:bg-white/10 transition-colors pointer-events-none">
                <FolderOpen className="w-3.5 h-3.5" />
                Browse Local Files
              </div>
            </>
          )}

          {status === "uploading" && (
            <>
              <div className="w-14 h-14 rounded-full border border-primary/20 bg-primary/10 flex items-center justify-center mb-5 relative">
                <div className="absolute inset-0 border-2 border-primary border-t-transparent rounded-full animate-spin" />
                <FilePlus2 className="w-6 h-6 text-primary" />
              </div>
              <p className="text-[15px] font-semibold text-foreground mb-1 tracking-wide">Processing {file?.name}</p>
              <p className="text-[13px] font-mono text-primary mb-5">{Math.min(Math.round(progress), 100)}% COMPLETE</p>
              <div className="w-56 h-1.5 rounded-full bg-black/50 overflow-hidden border border-white/5">
                <div
                  className="h-full bg-primary rounded-full transition-all duration-100 shadow-[0_0_10px_rgba(59,130,246,0.8)]"
                  style={{ width: `${Math.min(progress, 100)}%` }}
                />
              </div>
            </>
          )}

          {status === "success" && (
            <>
              <div className="w-14 h-14 rounded-full border border-emerald-500/30 bg-emerald-500/10 flex items-center justify-center mb-5 shadow-[0_0_15px_rgba(16,185,129,0.2)]">
                <CheckCircle className="w-6 h-6 text-emerald-400" />
              </div>
              <p className="text-[15px] font-bold text-emerald-400 mb-1 tracking-wide">Capture Uploaded</p>
              <p className="text-[13px] font-mono text-muted-foreground mb-1">{file?.name}</p>
              <p className="text-[12px] text-amber-400/80 mb-5 max-w-[280px] font-medium leading-relaxed bg-amber-500/10 border border-amber-500/20 px-3 py-2 rounded-md mt-2">
                ⚠ Demo mode active. Backend parsing is simulated. The dashboard is displaying static sample data.
              </p>
              <button
                onClick={reset}
                className="text-[13px] font-bold text-muted-foreground uppercase tracking-widest hover:text-foreground border-b border-transparent hover:border-foreground pb-0.5 transition-all relative z-10"
              >
                Upload new file
              </button>
            </>
          )}

          {status === "error" && (
            <>
              <div className="w-14 h-14 rounded-full border border-red-500/30 bg-red-500/10 flex items-center justify-center mb-5 shadow-[0_0_15px_rgba(239,68,68,0.2)]">
                <AlertCircle className="w-6 h-6 text-red-400" />
              </div>
              <p className="text-[15px] font-bold text-red-400 mb-1 tracking-wide">Format Rejected</p>
              <p className="text-[13px] font-mono text-muted-foreground mb-5">Unrecognised magic bytes. Ensure file is valid PCAP/PCAPNG.</p>
              <button
                onClick={reset}
                className="text-[13px] font-bold text-muted-foreground uppercase tracking-widest hover:text-foreground border-b border-transparent hover:border-foreground pb-0.5 transition-all relative z-10"
              >
                Reset and try again
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
