const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { cache: "no-store" });
  if (!res.ok) throw new Error(`GET ${path} → ${res.status}`);
  return res.json();
}

async function post<T>(path: string, body: unknown): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) throw new Error(`POST ${path} → ${res.status}`);
  return res.json();
}

async function patch<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { method: "PATCH" });
  if (!res.ok) throw new Error(`PATCH ${path} → ${res.status}`);
  return res.json();
}

async function del<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`, { method: "DELETE" });
  if (!res.ok) throw new Error(`DELETE ${path} → ${res.status}`);
  return res.json();
}

// ── Types ─────────────────────────────────────────────────────────────────────
export interface Detection {
  id: number;
  plate: string;
  camera_id: number;
  confidence: number;
  authorized: boolean;
  image_url?: string;
  timestamp: string;
}

export interface Vehicle {
  id: number;
  plate: string;
  owner?: string;
  description?: string;
  created_at: string;
}

export interface Alert {
  id: number;
  plate: string;
  camera_id: number;
  timestamp: string;
  resolved: boolean;
}

export interface Camera {
  id: number;
  name: string;
  location?: string;
  active: boolean;
}

export interface Stats {
  total_detections: number;
  authorized: number;
  unauthorized: number;
  open_alerts: number;
  registered_vehicles: number;
}

// ── API calls ─────────────────────────────────────────────────────────────────
export const api = {
  stats: () => get<Stats>("/stats/"),

  detections: (limit = 100) =>
    get<{ detections: Detection[] }>(`/detections/?limit=${limit}`).then(r => r.detections),

  vehicles: () =>
    get<{ vehicles: Vehicle[] }>("/vehicles/").then(r => r.vehicles),

  addVehicle: (plate: string, owner?: string, description?: string) =>
    post("/vehicles/", { plate, owner, description }),

  removeVehicle: (plate: string) => del(`/vehicles/${plate}`),

  checkVehicle: (plate: string) =>
    get<{ plate: string; authorized: boolean; status: string }>(`/vehicles/check/${plate}`),

  alerts: (unresolvedOnly = false) =>
    get<{ alerts: Alert[] }>(`/alerts/?unresolved_only=${unresolvedOnly}`).then(r => r.alerts),

  resolveAlert: (id: number) => patch(`/alerts/${id}/resolve`),

  cameras: () =>
    get<{ cameras: Camera[] }>("/cameras/").then(r => r.cameras),
};
