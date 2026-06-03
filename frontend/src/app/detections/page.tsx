import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function DetectionsPage() {
  const detections = await api.detections(200);

  return (
    <div className="space-y-5">
      <h1 className="font-mono text-[#00d4ff] text-xl font-bold tracking-wide">
        Detecciones ({detections.length})
      </h1>

      <div className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl overflow-hidden">
        <table className="w-full text-sm font-mono">
          <thead className="bg-[#111827]">
            <tr className="text-[10px] text-slate-500 uppercase">
              <th className="text-left px-4 py-3">Placa</th>
              <th className="text-left px-4 py-3">Estado</th>
              <th className="text-left px-4 py-3">Confianza</th>
              <th className="text-left px-4 py-3">Cámara</th>
              <th className="text-left px-4 py-3">Fecha/Hora</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1e3a5f]">
            {detections.map((d) => (
              <tr key={d.id} className="hover:bg-[#111827]/50">
                <td className="px-4 py-2 text-[#00d4ff] font-bold">{d.plate}</td>
                <td className="px-4 py-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${
                    d.authorized
                      ? "bg-green-900/40 text-[#00ff88]"
                      : "bg-red-900/40 text-[#ff3860]"
                  }`}>
                    {d.authorized ? "AUTORIZADO" : "NO AUTORIZADO"}
                  </span>
                </td>
                <td className="px-4 py-2 text-slate-400">
                  {(d.confidence * 100).toFixed(0)}%
                </td>
                <td className="px-4 py-2 text-slate-500">Cam {d.camera_id}</td>
                <td className="px-4 py-2 text-slate-500 text-xs">
                  {d.timestamp.slice(0, 16).replace("T", " ")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
