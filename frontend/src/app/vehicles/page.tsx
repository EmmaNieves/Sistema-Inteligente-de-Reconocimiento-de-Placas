"use client";
import { useEffect, useState } from "react";
import { api, Vehicle } from "@/lib/api";

export default function VehiclesPage() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [plate, setPlate] = useState("");
  const [owner, setOwner] = useState("");
  const [loading, setLoading] = useState(false);
  const [check, setCheck] = useState<{ plate: string; status: string; authorized: boolean } | null>(null);

  async function load() {
    setVehicles(await api.vehicles());
  }

  useEffect(() => { load(); }, []);

  async function handleAdd() {
    if (!plate.trim()) return;
    setLoading(true);
    await api.addVehicle(plate.trim().toUpperCase(), owner.trim() || undefined);
    setPlate(""); setOwner(""); setLoading(false);
    load();
  }

  async function handleRemove(p: string) {
    if (!confirm(`¿Eliminar ${p}?`)) return;
    await api.removeVehicle(p);
    load();
  }

  async function handleCheck() {
    if (!plate.trim()) return;
    const r = await api.checkVehicle(plate.trim().toUpperCase());
    setCheck(r);
  }

  return (
    <div className="space-y-6 max-w-3xl">
      <h1 className="font-mono text-[#00d4ff] text-xl font-bold tracking-wide">Vehículos autorizados</h1>

      {/* Add form */}
      <div className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl p-5 space-y-3">
        <h2 className="font-mono text-slate-400 text-xs uppercase">Registrar vehículo</h2>
        <div className="flex gap-3 flex-wrap">
          <input
            value={plate}
            onChange={e => setPlate(e.target.value.toUpperCase())}
            placeholder="ABC123"
            maxLength={6}
            className="bg-[#0a0d14] border border-[#1e3a5f] rounded-lg px-3 py-2 font-mono text-[#00d4ff] text-sm w-32 focus:outline-none focus:border-[#00d4ff]"
          />
          <input
            value={owner}
            onChange={e => setOwner(e.target.value)}
            placeholder="Propietario (opcional)"
            className="bg-[#0a0d14] border border-[#1e3a5f] rounded-lg px-3 py-2 font-mono text-slate-300 text-sm flex-1 focus:outline-none focus:border-[#00d4ff]"
          />
          <button
            onClick={handleAdd}
            disabled={loading}
            className="bg-[#00d4ff]/10 border border-[#00d4ff]/40 text-[#00d4ff] font-mono text-sm px-4 py-2 rounded-lg hover:bg-[#00d4ff]/20 transition"
          >
            + Agregar
          </button>
          <button
            onClick={handleCheck}
            className="bg-[#1e3a5f]/40 border border-[#1e3a5f] text-slate-300 font-mono text-sm px-4 py-2 rounded-lg hover:bg-[#1e3a5f] transition"
          >
            Verificar
          </button>
        </div>
        {check && (
          <p className={`font-mono text-sm ${check.authorized ? "text-[#00ff88]" : "text-[#ff3860]"}`}>
            {check.plate} → {check.status}
          </p>
        )}
      </div>

      {/* Table */}
      <div className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl overflow-hidden">
        <table className="w-full text-sm font-mono">
          <thead className="bg-[#111827]">
            <tr className="text-[10px] text-slate-500 uppercase">
              <th className="text-left px-4 py-3">Placa</th>
              <th className="text-left px-4 py-3">Propietario</th>
              <th className="text-left px-4 py-3">Registrado</th>
              <th className="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-[#1e3a5f]">
            {vehicles.map((v) => (
              <tr key={v.id} className="hover:bg-[#111827]/50">
                <td className="px-4 py-3 text-[#00d4ff] font-bold">{v.plate}</td>
                <td className="px-4 py-3 text-slate-300">{v.owner ?? "—"}</td>
                <td className="px-4 py-3 text-slate-500 text-xs">{v.created_at?.slice(0, 10)}</td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={() => handleRemove(v.plate)}
                    className="text-[#ff3860] text-xs hover:underline"
                  >
                    Eliminar
                  </button>
                </td>
              </tr>
            ))}
            {vehicles.length === 0 && (
              <tr>
                <td colSpan={4} className="px-4 py-6 text-slate-600 text-center">
                  Sin vehículos registrados
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
