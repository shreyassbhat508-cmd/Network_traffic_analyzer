export interface NetworkSampleNode {
  id: string;
  x: number;
  y: number;
  z: number;
  type: "internal" | "external" | "router" | "database" | "threat";
  label: string;
  activity: number;
}

export interface NetworkSampleLink {
  a: number;
  b: number;
  active: boolean;
  offset: number;
}

const CORE_NODES: NetworkSampleNode[] = [
  { id: "gw-01", x: 0, y: 0, z: 0.42, type: "router", label: "Gateway · 10.0.0.1", activity: 0.9 },
  { id: "ep-105", x: -0.48, y: -0.42, z: 0.08, type: "internal", label: "192.168.1.105", activity: 0.68 },
  { id: "ep-042", x: 0.47, y: -0.46, z: -0.15, type: "internal", label: "192.168.1.42", activity: 0.43 },
  { id: "db-01", x: -0.72, y: 0.48, z: -0.38, type: "database", label: "Database server", activity: 0.28 },
  { id: "dns-88", x: 0.78, y: 0.46, z: 0.14, type: "external", label: "DNS · 8.8.8.8", activity: 0.52 },
  { id: "host-01", x: 0.02, y: -0.72, z: 0.63, type: "threat", label: "Flagged · 45.33.22.1", activity: 0.76 },
  { id: "ep-010", x: -0.84, y: -0.04, z: 0.22, type: "internal", label: "10.0.0.10", activity: 0.32 },
  { id: "dns-11", x: 0.88, y: -0.02, z: -0.2, type: "external", label: "DNS · 1.1.1.1", activity: 0.36 },
];

const AMBIENT_NODES: NetworkSampleNode[] = Array.from({ length: 40 }, (_, index): NetworkSampleNode => {
  const angle = index * 2.399963;
  const spread = 0.18 + ((index * 17) % 62) / 100;
  return {
    id: `ep-${String(index + 200).padStart(3, "0")}`,
    x: Math.cos(angle) * spread,
    y: Math.sin(angle) * spread,
    z: Math.sin(index * 1.71) * 0.72,
    type: "internal",
    label: `Endpoint ${index + 1}`,
    activity: 0.12 + ((index * 37) % 63) / 100,
  };
});

export const NETWORK_NODES = [...CORE_NODES, ...AMBIENT_NODES];

const CORE_LINKS: NetworkSampleLink[] = [
  { a: 0, b: 1, active: true, offset: 0 },
  { a: 0, b: 2, active: true, offset: 20 },
  { a: 0, b: 3, active: false, offset: 30 },
  { a: 0, b: 4, active: true, offset: 40 },
  { a: 0, b: 5, active: true, offset: 55 },
  { a: 0, b: 6, active: false, offset: 70 },
  { a: 0, b: 7, active: false, offset: 80 },
  { a: 5, b: 1, active: true, offset: 95 },
  { a: 2, b: 4, active: false, offset: 110 },
];

const AMBIENT_LINKS = AMBIENT_NODES.map((_, index): NetworkSampleLink => ({
  a: index + CORE_NODES.length,
  b: index % 4 === 0 ? 0 : (index * 7) % CORE_NODES.length,
  active: index % 6 === 0,
  offset: (index * 17) % 120,
}));

export const NETWORK_LINKS = [...CORE_LINKS, ...AMBIENT_LINKS];
