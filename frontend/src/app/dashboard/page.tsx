import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const [stats, recentDetections, openAlerts] = await Promise.all([
    api.stats(),
    api.detections(5),
    api.alerts(true),
  ]);

  const cards = [
    { label: "Detecciones totales", value: stats.total_detections, color: "text-[#00d4ff]" },
    { label: "Autorizadas",         value: stats.authorized,        color: "text-[#00ff88]" },
    { label: "No autorizadas",      value: stats.unauthorized,      color: "text-[#ff3860]" },
    { label: "Alertas abiertas",    value: stats.open_alerts,       color: "text-[#ffd700]" },
    { label: "Vehículos reg.",      value: stats.registered_vehicles, color: "text-slate-300" },
  ];

  return (
    <div className="space-y-6">
      <h1 className="font-mono text-[#00d4ff] text-xl font-bold tracking-wide">Dashboard</h1>

      {/* Stat cards */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {cards.map((c) => (
          <div key={c.label} className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl p-4">
            <p className="text-[10px] font-mono text-slate-500 uppercase mb-1">{c.label}</p>
            <p className={`font-mono text-3xl font-bold ${c.color}`}>{c.value}</p>
          </div>
        ))}
      </div>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Recent detections */}
        <div className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl p-5">
          <h2 className="font-mono text-slate-400 text-xs uppercase mb-4">Últimas detecciones</h2>
          <table className="w-full text-sm font-mono">
            <thead>
              <tr className="text-[10px] text-slate-500 uppercase">
                <th className="text-left pb-2">Placa</th>
                <th className="text-left pb-2">Estado</th>
                <th className="text-left pb-2">Confianza</th>
                <th className="text-left pb-2">Hora</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[#1e3a5f]">
              {recentDetections.map((d) => (
                <tr key={d.id}>
                  <td className="py-2 text-[#00d4ff]">{d.plate}</td>
                  <td className="py-2">
                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                      d.authorized
                        ? "bg-green-900/40 text-[#00ff88]"
                        : "bg-red-900/40 text-[#ff3860]"
                    }`}>
                      {d.authorized ? "AUTORIZADO" : "NO AUTORIZADO"}
                    </span>
                  </td>
                  <td className="py-2 text-slate-400">{(d.confidence * 100).toFixed(0)}%</td>
                  <td className="py-2 text-slate-500 text-xs">
                    {d.timestamp.slice(11, 16)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Open alerts */}
        <div className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl p-5">
          <h2 className="font-mono text-slate-400 text-xs uppercase mb-4">
            Alertas abiertas ({openAlerts.length})
          </h2>
          {openAlerts.length === 0 ? (
            <p className="text-slate-500 font-mono text-sm">Sin alertas pendientes ✅</p>
          ) : (
            <ul className="space-y-2">
              {openAlerts.slice(0, 6).map((a) => (
                <li key={a.id} className="flex items-center justify-between bg-red-950/30 border border-red-900/40 rounded-lg px-3 py-2">
                  <span className="font-mono text-[#ff3860] font-bold">{a.plate}</span>
                  <span className="text-xs text-slate-500 font-mono">
                    Cámara {a.camera_id} · {a.timestamp.slice(11, 16)}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </div>
  );
}
