"use client";

import { createContext, useContext, useMemo, useState } from "react";

export type AnimationIntensity = "full" | "reduced" | "off";
export type RowsPerPage = 10 | 25 | 50;

export interface WorkspacePreferences {
  animationIntensity: AnimationIntensity;
  compactTables: boolean;
  showTimestamps: boolean;
  rowsPerPage: RowsPerPage;
}

interface WorkspacePreferencesContextValue extends WorkspacePreferences {
  updatePreferences: (updates: Partial<WorkspacePreferences>) => void;
}

const DEFAULT_PREFERENCES: WorkspacePreferences = {
  animationIntensity: "full",
  compactTables: false,
  showTimestamps: true,
  rowsPerPage: 10,
};

const WorkspacePreferencesContext = createContext<WorkspacePreferencesContextValue>({
  ...DEFAULT_PREFERENCES,
  updatePreferences: () => {},
});

export function WorkspacePreferencesProvider({ children }: { children: React.ReactNode }) {
  const [preferences, setPreferences] = useState(DEFAULT_PREFERENCES);
  const value = useMemo(() => ({
    ...preferences,
    updatePreferences: (updates: Partial<WorkspacePreferences>) => {
      setPreferences(current => ({ ...current, ...updates }));
    },
  }), [preferences]);

  return (
    <WorkspacePreferencesContext.Provider value={value}>
      {children}
    </WorkspacePreferencesContext.Provider>
  );
}

export function useWorkspacePreferences() {
  return useContext(WorkspacePreferencesContext);
}
