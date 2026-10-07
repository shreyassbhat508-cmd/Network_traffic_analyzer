"use client";

import { useWorkspacePreferences } from "@/lib/workspace-context";
import type { AnimationIntensity, RowsPerPage } from "@/lib/workspace-context";

function PreferenceRow({ title, detail, children }: { title: string; detail: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-3 px-5 py-4 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <h3 className="text-sm font-medium text-foreground">{title}</h3>
        <p className="mt-1 max-w-xl text-xs leading-relaxed text-muted-foreground">{detail}</p>
      </div>
      <div className="shrink-0">{children}</div>
    </div>
  );
}

function Select<T extends string | number>({ value, options, onChange }: {
  value: T;
  options: { label: string; value: T }[];
  onChange: (value: T) => void;
}) {
  return (
    <select
      value={value}
      onChange={event => {
        const option = options.find(item => String(item.value) === event.target.value);
        if (option) onChange(option.value);
      }}
      className="min-w-36 rounded-md border border-white/10 bg-[#10151b] px-3 py-2 text-sm text-foreground outline-none focus-visible:ring-2 focus-visible:ring-primary"
    >
      {options.map(option => <option key={String(option.value)} value={String(option.value)}>{option.label}</option>)}
    </select>
  );
}

function Toggle({ checked, onChange, label }: { checked: boolean; onChange: (checked: boolean) => void; label: string }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={() => onChange(!checked)}
      className={`relative h-6 w-11 rounded-full border transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary ${checked ? "border-primary bg-primary/70" : "border-white/15 bg-white/10"}`}
    >
      <span className={`absolute top-0.5 h-4 w-4 rounded-full bg-white transition-transform ${checked ? "translate-x-[1.35rem]" : "translate-x-0.5"}`} />
    </button>
  );
}

export function SettingsView() {
  const preferences = useWorkspacePreferences();
  const update = preferences.updatePreferences;

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <header>
        <p className="font-mono text-[12px] uppercase tracking-[0.18em] text-primary">Workspace</p>
        <h1 className="mt-2 text-2xl font-semibold tracking-tight text-foreground">Display settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">Tune motion and table density for this session.</p>
      </header>

      <section className="glass-panel overflow-hidden rounded-lg">
        <div className="border-b border-white/[0.07] px-5 py-3">
          <h2 className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">Motion</h2>
        </div>
        <PreferenceRow title="Animation" detail="Reduce canvas redraws or pause decorative motion. Interactive node selection remains available.">
          <Select<AnimationIntensity>
            value={preferences.animationIntensity}
            options={[
              { label: "Full", value: "full" },
              { label: "Reduced", value: "reduced" },
              { label: "Off", value: "off" },
            ]}
            onChange={animationIntensity => update({ animationIntensity })}
          />
        </PreferenceRow>
      </section>

      <section className="glass-panel overflow-hidden rounded-lg">
        <div className="border-b border-white/[0.07] px-5 py-3">
          <h2 className="text-xs font-semibold uppercase tracking-[0.12em] text-muted-foreground">Packet table</h2>
        </div>
        <PreferenceRow title="Rows per page" detail="Controls the number of sample packet records shown at once.">
          <Select<RowsPerPage>
            value={preferences.rowsPerPage}
            options={[10, 25, 50].map(value => ({ label: `${value} rows`, value: value as RowsPerPage }))}
            onChange={rowsPerPage => update({ rowsPerPage })}
          />
        </PreferenceRow>
        <div className="divide-y divide-white/[0.06] border-t border-white/[0.07]">
          <PreferenceRow title="Compact rows" detail="Use less vertical space in packet results.">
            <Toggle checked={preferences.compactTables} onChange={compactTables => update({ compactTables })} label="Compact packet rows" />
          </PreferenceRow>
          <PreferenceRow title="Timestamps" detail="Show packet capture times in the results table.">
            <Toggle checked={preferences.showTimestamps} onChange={showTimestamps => update({ showTimestamps })} label="Show packet timestamps" />
          </PreferenceRow>
        </div>
      </section>

      <p className="rounded-md border border-white/[0.07] bg-white/[0.02] px-4 py-3 text-xs leading-relaxed text-muted-foreground">
        These preferences apply immediately and last until the page is reloaded. The current workspace has no connected analysis service.
      </p>
    </div>
  );
}
