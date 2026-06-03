import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function StatsPage() {
  const stats = await api.stats();
  const authPct = stats.total_detections > 0
    ? Math.round((stats.authorized / stats.total_detections) * 100)
    : 0;

  return (
    <div className="space-y-6 max-w-2xl">
      <h1 className="font-mono text-[#00d4ff] text-xl font-bold tracking-wide">Estadísticas</h1>

      {/* Bar chart visual */}
      <div className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl p-6 space-y-5">
        <h2 className="font-mono text-slate-400 text-xs uppercase">Distribución de accesos</h2>

        <div className="space-y-4">
          {[
            { label: "Autorizadas",   value: stats.authorized,   total: stats.total_detections, color: "bg-[#00ff88]" },
            { label: "No autorizadas", value: stats.unauthorized, total: stats.total_detections, color: "bg-[#ff3860]" },
          ].map(({ label, value, total, color }) => {
            const pct = total > 0 ? Math.round((value / total) * 100) : 0;
            return (
              <div key={label}>
                <div className="flex justify-between font-mono text-xs text-slate-400 mb-1">
                  <span>{label}</span>
                  <span>{value} ({pct}%)</span>
                </div>
                <div className="h-4 bg-[#0a0d14] rounded-full overflow-hidden">
                  <div
                    className={`h-full ${color} rounded-full transition-all`}
                    style={{ width: `${pct}%` }}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4">
        {[
          { label: "Total detecciones",    value: stats.total_detections, color: "text-[#00d4ff]" },
          { label: "Vehículos registrados", value: stats.registered_vehicles, color: "text-slate-200" },
          { label: "Alertas abiertas",     value: stats.open_alerts, color: "text-[#ffd700]" },
        ].map(({ label, value, color }) => (
          <div key={label} className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl p-4 text-center">
            <p className="text-[10px] font-mono text-slate-500 uppercase mb-1">{label}</p>
            <p className={`font-mono text-3xl font-bold ${color}`}>{value}</p>
          </div>
        ))}
      </div>

      <div className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl p-5">
        <p className="font-mono text-slate-400 text-xs uppercase mb-2">Tasa de autorización</p>
        <p className="font-mono text-5xl font-bold text-[#00ff88]">{authPct}%</p>
        <p className="font-mono text-xs text-slate-500 mt-1">de las detecciones son vehículos autorizados</p>
      </div>
    </div>
  );
}
