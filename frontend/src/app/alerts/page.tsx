"use client";
import { useEffect, useState } from "react";
import { api, Alert } from "@/lib/api";

export default function AlertsPage() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [onlyOpen, setOnlyOpen] = useState(true);

  async function load() {
    setAlerts(await api.alerts(onlyOpen));
  }

  useEffect(() => { load(); }, [onlyOpen]);

  async function handleResolve(id: number) {
    await api.resolveAlert(id);
    load();
  }

  return (
    <div className="space-y-5 max-w-3xl">
      <div className="flex items-center justify-between">
        <h1 className="font-mono text-[#00d4ff] text-xl font-bold tracking-wide">
          Alertas
        </h1>
        <label className="flex items-center gap-2 font-mono text-xs text-slate-400 cursor-pointer">
          <input
            type="checkbox"
            checked={onlyOpen}
            onChange={e => setOnlyOpen(e.target.checked)}
            className="accent-[#00d4ff]"
          />
          Solo abiertas
        </label>
      </div>

      {alerts.length === 0 ? (
        <div className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl p-8 text-center font-mono text-slate-500">
          Sin alertas {onlyOpen ? "pendientes" : "registradas"} ✅
        </div>
      ) : (
        <div className="space-y-2">
          {alerts.map((a) => (
            <div
              key={a.id}
              className={`flex items-center justify-between rounded-xl border px-4 py-3
                ${a.resolved
                  ? "bg-[#1a2235] border-[#1e3a5f]"
                  : "bg-red-950/30 border-red-900/50"
                }`}
            >
              <div className="flex items-center gap-4">
                <span className="font-mono font-bold text-[#ff3860] text-lg">{a.plate}</span>
                <span className="text-xs text-slate-500 font-mono">
                  Cámara {a.camera_id} · {a.timestamp.slice(0, 16).replace("T", " ")}
                </span>
                {a.resolved && (
                  <span className="text-[10px] text-[#00ff88] bg-green-900/30 px-2 py-0.5 rounded-full font-mono">
                    RESUELTA
                  </span>
                )}
              </div>
              {!a.resolved && (
                <button
                  onClick={() => handleResolve(a.id)}
                  className="text-xs font-mono text-[#00ff88] border border-green-900/50 px-3 py-1 rounded-lg hover:bg-green-900/20 transition"
                >
                  Marcar resuelta
                </button>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
