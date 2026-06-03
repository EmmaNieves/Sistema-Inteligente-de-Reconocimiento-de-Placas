import { api } from "@/lib/api";

export const dynamic = "force-dynamic";

export default async function CamerasPage() {
  const cameras = await api.cameras();

  return (
    <div className="space-y-5 max-w-2xl">
      <h1 className="font-mono text-[#00d4ff] text-xl font-bold tracking-wide">Cámaras</h1>

      {cameras.length === 0 ? (
        <div className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl p-8 text-center font-mono text-slate-500">
          Sin cámaras registradas en Supabase
        </div>
      ) : (
        <div className="grid gap-3">
          {cameras.map((c) => (
            <div
              key={c.id}
              className="bg-[#1a2235] border border-[#1e3a5f] rounded-xl px-5 py-4 flex items-center justify-between"
            >
              <div>
                <p className="font-mono font-bold text-slate-200">{c.name}</p>
                {c.location && (
                  <p className="font-mono text-xs text-slate-500">{c.location}</p>
                )}
              </div>
              <span className={`font-mono text-xs px-3 py-1 rounded-full border ${
                c.active
                  ? "text-[#00ff88] border-green-900/50 bg-green-900/20"
                  : "text-slate-500 border-slate-700 bg-slate-800/30"
              }`}>
                {c.active ? "● ACTIVA" : "○ INACTIVA"}
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
