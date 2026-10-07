"use client";

import { createContext, useContext, useState } from "react";

export type View = "dashboard" | "search" | "alerts" | "topology" | "settings";

interface NavContextValue {
  view: View;
  setView: (v: View) => void;
}

const NavContext = createContext<NavContextValue>({
  view: "dashboard",
  setView: () => {},
});

export function NavProvider({ children }: { children: React.ReactNode }) {
  const [view, setView] = useState<View>("dashboard");
  return (
    <NavContext.Provider value={{ view, setView }}>
      {children}
    </NavContext.Provider>
  );
}

export function useNav() {
  return useContext(NavContext);
}
