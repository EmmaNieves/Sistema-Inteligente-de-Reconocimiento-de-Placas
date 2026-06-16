import { useEffect, useState } from "react";
import { Layout } from "@/components/Layout";
import { api } from "@/lib/api";
import { Loader2, AlertCircle } from "lucide-react";

type Badge = "Residente" | "Visitante" | "Tránsito";

interface PlacaAudiencia {
  plate_text: string;
  count: number;
  badge: Badge;
  vehicle_type: string;
  authorized: boolean;
  peak_hour: string;
  top_camera_id: string;
  modelo: string;
  precio_estimado: number;
  first_seen: string;
  last_seen: string;
}

interface AudienciasData {
  total_placas: number;
  residentes: number;
  visitantes: number;
  transito: number;
  recurrence_rate: number;
  placas: PlacaAudiencia[];
}

const BADGE_STYLES: Record<Badge, string> = {
  Residente: "bg-[#DCFCE7] text-[#15803D] border border-[#BBF7D0]",
  Visitante: "bg-[#E0F2FE] text-[#0369A1] border border-[#BAE6FD]",
  Tránsito:  "bg-[#F3F4F6] text-[#4B5563] border border-[#E5E7EB]",
};

const BADGE_DOT: Record<Badge, string> = {
  Residente: "bg-[#22C55E]",
  Visitante: "bg-[#0EA5E9]",
  Tránsito:  "bg-[#9CA3AF]",
};

const NIVEL_STYLES = {
  Alta:  "bg-[#DCFCE7] text-[#15803D] border border-[#BBF7D0]",
  Media: "bg-[#FEF9C3] text-[#854D0E] border border-[#FEF08A]",
  Baja:  "bg-[#F3F4F6] text-[#4B5563] border border-[#E5E7EB]",
};

function fmt(iso: string): string {
  if (!iso) return "—";
  return new Date(iso).toLocaleString("es-CO", {
    day: "2-digit", month: "short", hour: "2-digit", minute: "2-digit",
  });
}

function formatCOP(value: number): string {
  if (!value) return "—";
  return new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(value);
}

function getSegmentoByPrecio(precio: number): { label: string; color: string } {
  if (precio >= 80000000) return { label: "Alto", color: "text-[#15803D]" };
  if (precio >= 50000000) return { label: "Medio-Alto", color: "text-[#0369A1]" };
  if (precio >= 30000000) return { label: "Medio", color: "text-[#FC6C03]" };
  if (precio >= 10000000) return { label: "Bajo-Medio", color: "text-[#854D0E]" };
  if (precio > 0) return { label: "Bajo", color: "text-[#B91C1C]" };
  return { label: "Sin datos", color: "text-[#9CA3AF]" };
}

const VEHICLE_FACTOR: Record<string, number> = {
  automovil: 1.4,
  motocicleta: 1.0,
  bus: 8.0,
  camion: 1.2,
  otro: 1.2,
};

interface ImpresionHora {
  hour: string;
  impresiones: number;
  cpm: number;
  nivel: "Alta" | "Media" | "Baja";
}

function calcImpacto(placas: PlacaAudiencia[]): ImpresionHora[] {
  const hourMap = new Map<string, { imp: number; recurrentes: number }>();
  for (const p of placas) {
    const h = p.peak_hour;
    if (!h) continue;
    const factor = VEHICLE_FACTOR[p.vehicle_type] ?? 1.2;
    const bonus = p.badge === "Residente" ? 1.5 : p.badge === "Visitante" ? 1.15 : 1.0;
    const imp = p.count * factor * bonus;
    const prev = hourMap.get(h) ?? { imp: 0, recurrentes: 0 };
    prev.imp += imp;
    if (p.badge !== "Tránsito") prev.recurrentes += 1;
    hourMap.set(h, prev);
  }
  return Array.from(hourMap.entries())
    .map(([hour, v]) => {
      const impresiones = Math.round(v.imp);
      const cpm = Number((2 + v.recurrentes * 0.3).toFixed(2));
      const nivel: "Alta" | "Media" | "Baja" = impresiones >= 50 ? "Alta" : impresiones >= 20 ? "Media" : "Baja";
      return { hour, impresiones, cpm, nivel };
    })
    .sort((a, b) => b.impresiones - a.impresiones);
}

function buildInsight(d: AudienciasData): string {
  if (!d || d.total_placas === 0) return "Sin datos suficientes para generar un insight.";
  const dominant = d.residentes >= d.visitantes && d.residentes >= d.transito
    ? "residentes" : d.visitantes >= d.transito ? "visitantes" : "tránsito de paso";
  const topType = d.placas.reduce((acc, p) => {
    acc[p.vehicle_type] = (acc[p.vehicle_type] ?? 0) + 1;
    return acc;
  }, {} as Record<string, number>);
  const topVehicle = Object.entries(topType).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "vehículos";
  const recRate = d.recurrence_rate;
  if (dominant === "residentes" && recRate > 60)
    return `Zona de alta recurrencia (${recRate}%). Flujo dominante: ${topVehicle}. Perfil ideal para negocios de servicios frecuentes: talleres, tiendas de conveniencia o estaciones de servicio.`;
  if (dominant === "visitantes")
    return `Zona mixta con ${recRate}% de recurrencia. Predominan visitantes con vehículos tipo ${topVehicle}. Adecuada para comercio ocasional o puntos de paso con oferta diversa.`;
  return `Zona de tránsito (recurrencia ${recRate}%). Alta rotación de ${topVehicle}. Oportunidad para publicidad exterior o servicios rápidos orientados a conductores en paso.`;
}

export default function Audiencias() {
  const [data, setData] = useState<AudienciasData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<Badge | "Todos">("Todos");
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    setError(null);
    api.audiencias()
      .then(d => { setData(d); setLoading(false); })
      .catch(() => { setError("Error al cargar audiencias"); setLoading(false); });
  }, []);

  const placas = (data?.placas ?? []).filter(p => {
    const matchBadge = filter === "Todos" || p.badge === filter;
    const matchSearch = p.plate_text.toLowerCase().includes(search.toLowerCase());
    return matchBadge && matchSearch;
  });

  if (loading) {
    return (
      <Layout>
        <div className="flex h-[80vh] flex-col items-center justify-center gap-4 text-[#6B7280]">
          <Loader2 className="w-10 h-10 animate-spin text-[#FC6C03]" />
          <p className="font-medium text-lg">Analizando audiencias...</p>
        </div>
      </Layout>
    );
  }

  if (error || !data) {
    return (
      <Layout>
        <div className="p-8">
          <div className="flex flex-col gap-2 p-6 text-red-600 bg-red-50 rounded-2xl border border-red-200">
            <AlertCircle className="w-8 h-8" />
            <h2 className="font-bold text-lg">Error de conexión</h2>
            <p>{error ?? "Sin datos disponibles."}</p>
          </div>
        </div>
      </Layout>
    );
  }

  const insight = buildInsight(data);
  const impactoRows = calcImpacto(data.placas);
  const totalImpresiones = impactoRows.reduce((s, r) => s + r.impresiones, 0);
  const topHora = impactoRows[0];
  const cpmPromedio = impactoRows.length > 0
    ? Number((impactoRows.reduce((s, r) => s + r.cpm, 0) / impactoRows.length).toFixed(2))
    : 0;

  // Análisis por precio
  const placasConPrecio = data.placas.filter(p => p.precio_estimado > 0);
  const precioPromedio = placasConPrecio.length > 0
    ? Math.round(placasConPrecio.reduce((s, p) => s + p.precio_estimado, 0) / placasConPrecio.length)
    : 0;

  const segmentoCounts = { Alto: 0, "Medio-Alto": 0, Medio: 0, "Bajo-Medio": 0, Bajo: 0 };
  for (const p of data.placas) {
    const seg = getSegmentoByPrecio(p.precio_estimado).label;
    if (seg in segmentoCounts) segmentoCounts[seg as keyof typeof segmentoCounts] += 1;
  }
  const totalSegmentos = Object.values(segmentoCounts).reduce((a, b) => a + b, 0) || 1;
  const segmentoDominante = Object.entries(segmentoCounts).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "Medio";

  const modeloMasFrecuente = data.placas
    .filter(p => p.modelo)
    .reduce((acc, p) => {
      acc[p.modelo] = (acc[p.modelo] ?? 0) + 1;
      return acc;
    }, {} as Record<string, number>);
  const topModelo = Object.entries(modeloMasFrecuente).sort((a, b) => b[1] - a[1])[0]?.[0] ?? "—";

  // Contar tipos
  const motos = data.placas.filter(p => p.vehicle_type === "motocicleta").length;
  const autos = data.placas.filter(p => p.vehicle_type === "automovil").length;
  const otros = data.placas.filter(p => !["motocicleta", "automovil"].includes(p.vehicle_type)).length;
  const total = data.total_placas || 1;

  return (
    <Layout>
      <div className="max-w-[1040px] mx-auto pt-4 pb-20 flex flex-col gap-8">

        {/* Header */}
        <div className="flex flex-col gap-1">
          <h1 style={{ fontFamily: "'Fredoka One', cursive" }} className="text-[36px] font-bold text-[#111827]">
            Audiencias y Perfilamiento
          </h1>
          <p className="text-[14px] text-[#6B7280]">
            Análisis de recurrencia, tipo de usuarios y poder adquisitivo por zona.
          </p>
        </div>

        {/* KPIs */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "Total placas únicas", value: data.total_placas, color: "text-[#111827]" },
            { label: "Residentes", value: data.residentes, color: "text-[#15803D]" },
            { label: "Visitantes", value: data.visitantes, color: "text-[#0369A1]" },
            { label: "Tránsito", value: data.transito, color: "text-[#4B5563]" },
          ].map(k => (
            <div key={k.label} className="bg-white border border-[#F3F4F6] shadow-sm rounded-2xl p-5">
              <span className="text-[13px] text-[#6B7280] block mb-1">{k.label}</span>
              <div style={{ fontFamily: "'Geist', sans-serif" }} className={`font-bold text-3xl ${k.color}`}>
                {k.value}
              </div>
            </div>
          ))}
        </div>

        {/* Perfil de vehículos por zona */}
        <div className="bg-white border border-[#F3F4F6] shadow-sm rounded-2xl p-6 flex flex-col gap-4">
          <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }} className="font-bold text-[18px] text-[#1F2937]">
            Perfil de vehículos por zona
          </h2>
          <p className="text-[13px] text-[#6B7280]">
            Distribución de tipos de vehículos detectados.
          </p>
          <div className="grid grid-cols-3 gap-4 mt-2">
            {[
              { label: "Motos", value: motos, pct: Math.round((motos / total) * 100) },
              { label: "Automóviles", value: autos, pct: Math.round((autos / total) * 100) },
              { label: "Otros", value: otros, pct: Math.round((otros / total) * 100) },
            ].map(item => (
              <div key={item.label} className="bg-[#F9FAFB] border border-[#F3F4F6] rounded-xl p-4">
                <span className="text-[11px] text-[#6B7280] uppercase tracking-widest block mb-2">{item.label}</span>
                <span style={{ fontFamily: "'Geist', sans-serif" }} className="text-2xl font-bold text-[#111827]">{item.value}</span>
                <span className="text-[12px] text-[#9CA3AF] ml-2">{item.pct}%</span>
              </div>
            ))}
          </div>
        </div>

        {/* Análisis de poder adquisitivo */}
        <div className="bg-white border border-[#F3F4F6] shadow-sm rounded-2xl p-6 flex flex-col gap-5">
          <div>
            <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }} className="font-bold text-[18px] text-[#1F2937]">
              Análisis de poder adquisitivo
            </h2>
            <p className="text-[13px] text-[#6B7280] mt-1">
              Estimado con base en el precio promedio de los vehículos detectados.
            </p>
          </div>

          {/* KPIs de precio */}
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-[#F9FAFB] border border-[#F3F4F6] rounded-xl p-4">
              <span className="text-[11px] text-[#6B7280] uppercase tracking-widest block mb-1">Precio promedio</span>
              <span style={{ fontFamily: "'Geist', sans-serif" }} className="text-xl font-bold text-[#111827]">
                {formatCOP(precioPromedio)}
              </span>
            </div>
            <div className="bg-[#F9FAFB] border border-[#F3F4F6] rounded-xl p-4">
              <span className="text-[11px] text-[#6B7280] uppercase tracking-widest block mb-1">Segmento dominante</span>
              <span style={{ fontFamily: "'Geist', sans-serif" }} className="text-xl font-bold text-[#FC6C03]">
                {segmentoDominante}
              </span>
            </div>
            <div className="bg-[#F9FAFB] border border-[#F3F4F6] rounded-xl p-4">
              <span className="text-[11px] text-[#6B7280] uppercase tracking-widest block mb-1">Modelo más frecuente</span>
              <span style={{ fontFamily: "'Geist', sans-serif" }} className="text-[15px] font-bold text-[#111827]">
                {topModelo}
              </span>
            </div>
          </div>

          {/* Barras por segmento */}
          <div className="flex flex-col gap-3">
            {Object.entries(segmentoCounts).map(([seg, count]) => {
              const pct = Math.round((count / totalSegmentos) * 100);
              const colors: Record<string, string> = {
                Alto: "bg-[#15803D]",
                "Medio-Alto": "bg-[#0369A1]",
                Medio: "bg-[#FC6C03]",
                "Bajo-Medio": "bg-[#854D0E]",
                Bajo: "bg-[#9CA3AF]",
              };
              return (
                <div key={seg} className="flex items-center gap-4">
                  <span className="w-24 text-[13px] font-medium text-[#4B5563] shrink-0">{seg}</span>
                  <div className="flex-1 h-2 bg-[#F3F4F6] rounded-full overflow-hidden">
                    <div className={`h-full ${colors[seg]} rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
                  </div>
                  <span style={{ fontFamily: "'Geist', sans-serif" }} className="w-10 text-[13px] font-semibold text-[#1F2937] text-right">{count}</span>
                </div>
              );
            })}
          </div>

          {/* Insight de segmento */}
          <div className="bg-[#FFF7ED] border border-[#FC6C03] rounded-xl p-4">
            <span className="text-[11px] font-semibold uppercase text-[#FC6C03] block mb-2">Perfil de usuario de zona</span>
            <p className="text-[14px] text-[#1F2937] leading-relaxed">
              {segmentoDominante === "Alto"
                ? `Zona de alto poder adquisitivo. Precio promedio de vehículos: ${formatCOP(precioPromedio)}. Perfil ideal para marcas premium, servicios especializados y experiencias exclusivas.`
                : segmentoDominante === "Medio-Alto"
                ? `Zona de poder adquisitivo medio-alto. Precio promedio: ${formatCOP(precioPromedio)}. Adecuada para comercio establecido, servicios financieros y tecnología de consumo.`
                : segmentoDominante === "Medio"
                ? `Zona de clase media. Precio promedio: ${formatCOP(precioPromedio)}. Oportunidad para supermercados, restaurantes familiares y servicios cotidianos.`
                : segmentoDominante === "Bajo-Medio"
                ? `Zona popular con vehículos de precio promedio ${formatCOP(precioPromedio)}. Enfocarse en precios competitivos, productos de alta rotación y movilidad.`
                : `Zona de movilidad activa. Predominan motos y vehículos de bajo costo. Precio promedio: ${formatCOP(precioPromedio)}. Servicios rápidos y económicos tienen alta demanda aquí.`}
            </p>
          </div>
        </div>

        {/* Recurrencia + Insight */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white border border-[#F3F4F6] shadow-sm rounded-2xl p-6 flex flex-col justify-center gap-3">
            <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }} className="font-bold text-[18px] text-[#1F2937]">Tasa de recurrencia</h2>
            <p style={{ fontFamily: "'Geist', sans-serif" }} className="text-4xl font-bold text-[#111827] flex items-baseline">
              {data.recurrence_rate}
              <span className="text-lg text-[#6B7280] font-normal ml-1">%</span>
            </p>
            <div className="w-full h-2 bg-[#F3F4F6] rounded-full overflow-hidden">
              <div
                className="h-full bg-gradient-to-r from-[#0EA5E9] to-[#22C55E] rounded-full transition-all duration-700"
                style={{ width: `${data.recurrence_rate}%` }}
              />
            </div>
            <p className="text-[13px] text-[#6B7280]">
              {data.residentes + data.visitantes} placas vistas más de una vez de {data.total_placas} únicas.
            </p>
          </div>

          <div className="bg-white border border-[#F3F4F6] shadow-sm rounded-2xl p-6 flex flex-col gap-4">
            <div className="bg-[#F9FAFB] border border-[#F3F4F6] rounded-xl p-4 border-l-4 border-l-[#FC6C03] h-full flex flex-col justify-center">
              <span className="text-[11px] font-semibold uppercase text-[#FC6C03] block mb-2">Insight comercial generado</span>
              <p className="text-[14px] text-[#1F2937] leading-relaxed">{insight}</p>
            </div>
          </div>
        </div>

        {/* Distribución visual por badge */}
        <div className="bg-white border border-[#F3F4F6] shadow-sm rounded-2xl p-6">
          <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }} className="font-bold text-[18px] text-[#1F2937] mb-6">Distribución de audiencias</h2>
          <div className="flex flex-col gap-4">
            {(["Residente", "Visitante", "Tránsito"] as Badge[]).map(b => {
              const count = b === "Residente" ? data.residentes : b === "Visitante" ? data.visitantes : data.transito;
              const pct = data.total_placas > 0 ? (count / data.total_placas) * 100 : 0;
              const barColor = b === "Residente" ? "bg-[#22C55E]" : b === "Visitante" ? "bg-[#0EA5E9]" : "bg-[#9CA3AF]";
              return (
                <div key={b} className="flex items-center gap-4">
                  <span className="w-20 text-[13px] font-medium text-[#4B5563] shrink-0">{b}</span>
                  <div className="flex-1 h-2 bg-[#F3F4F6] rounded-full overflow-hidden">
                    <div className={`h-full ${barColor} rounded-full transition-all duration-700`} style={{ width: `${pct}%` }} />
                  </div>
                  <span style={{ fontFamily: "'Geist', sans-serif" }} className="w-10 text-[13px] font-semibold text-[#1F2937] text-right">{count}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Impacto publicitario */}
        <div className="bg-white border border-[#F3F4F6] shadow-sm rounded-2xl p-6 flex flex-col gap-6">
          <div>
            <h2 style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }} className="font-bold text-[18px] text-[#1F2937]">
              Impacto publicitario estimado
            </h2>
            <p className="text-[13px] text-[#6B7280] mt-1">
              Impresiones por hora pico según tipo de vehículo y recurrencia. CPM en USD.
            </p>
          </div>
          <div className="grid grid-cols-3 gap-4">
            <div className="bg-[#F9FAFB] border border-[#F3F4F6] rounded-xl p-4">
              <span className="text-[11px] text-[#6B7280] uppercase tracking-widest block mb-1">Total impresiones</span>
              <span style={{ fontFamily: "'Geist', sans-serif" }} className="text-2xl font-bold text-[#111827]">
                {totalImpresiones.toLocaleString("es-CO")}
              </span>
            </div>
            <div className="bg-[#F9FAFB] border border-[#F3F4F6] rounded-xl p-4">
              <span className="text-[11px] text-[#6B7280] uppercase tracking-widest block mb-1">Hora pico</span>
              <span style={{ fontFamily: "'Geist', sans-serif" }} className="text-2xl font-bold text-[#FC6C03]">
                {topHora?.hour ?? "—"}
              </span>
            </div>
            <div className="bg-[#F9FAFB] border border-[#F3F4F6] rounded-xl p-4">
              <span className="text-[11px] text-[#6B7280] uppercase tracking-widest block mb-1">CPM promedio</span>
              <span style={{ fontFamily: "'Geist', sans-serif" }} className="text-2xl font-bold text-[#0369A1]">
                ${cpmPromedio}
              </span>
            </div>
          </div>
          {impactoRows.length === 0 ? (
            <p className="text-[13px] text-[#6B7280] text-center py-6">Sin datos para calcular impacto.</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr>
                    {["Hora pico", "Impresiones est.", "CPM (USD)", "Nivel de tráfico"].map(h => (
                      <th key={h} className="text-[11px] font-semibold text-[#9CA3AF] uppercase px-4 py-3 border-b border-[#F3F4F6]">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {impactoRows.map((row, i) => (
                    <tr key={row.hour} className={`border-b border-[#F9FAFB] hover:bg-gray-50/50 transition-colors ${i === 0 ? "bg-[#FFF7ED]" : ""}`}>
                      <td style={{ fontFamily: "'Geist', sans-serif" }} className="px-4 py-3 text-[14px] font-bold text-[#1F2937]">
                        {row.hour}
                        {i === 0 && <span className="ml-2 text-[10px] font-semibold bg-[#FC6C03] text-white px-1.5 py-0.5 rounded">TOP</span>}
                      </td>
                      <td style={{ fontFamily: "'Geist', sans-serif" }} className="px-4 py-3 text-[13px] font-semibold text-[#1F2937]">{row.impresiones.toLocaleString("es-CO")}</td>
                      <td style={{ fontFamily: "'Geist', sans-serif" }} className="px-4 py-3 text-[13px] text-[#0369A1] font-medium">${row.cpm}</td>
                      <td className="px-4 py-3">
                        <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${NIVEL_STYLES[row.nivel]}`}>{row.nivel}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
          <p className="text-[11px] text-[#9CA3AF] border-t border-[#F3F4F6] pt-4">
            Metodología: impresiones = detecciones × factor de ocupación × bonificación por recurrencia. CPM base $2 USD. Estimados con fines de inteligencia comercial.
          </p>
        </div>

        {/* Filtros + Búsqueda */}
        <div className="flex flex-col sm:flex-row gap-4 items-start sm:items-center justify-between">
          <div className="flex gap-2 flex-wrap">
            {(["Todos", "Residente", "Visitante", "Tránsito"] as const).map(b => (
              <button
                key={b}
                onClick={() => setFilter(b)}
                className={`text-[13px] font-medium px-4 py-1.5 rounded-full border transition-colors ${
                  filter === b ? "bg-[#FC6C03] border-[#FC6C03] text-white shadow-sm" : "bg-white border-[#D1D5DB] text-[#4B5563] hover:bg-gray-50"
                }`}
              >
                {b}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-4 w-full sm:w-auto">
            <span className="text-[13px] text-[#6B7280] hidden sm:inline-block">
              Mostrando {placas.length} registro{placas.length !== 1 ? "s" : ""}
            </span>
            <input
              type="text"
              placeholder="Buscar placa..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="bg-white border border-[#D1D5DB] text-[#111827] text-[13px] rounded-lg px-4 py-2 outline-none focus:border-[#FC6C03] focus:ring-1 focus:ring-[#FC6C03] w-full sm:w-64"
            />
          </div>
        </div>

        {/* Tabla de placas */}
        <div className="bg-white border border-[#F3F4F6] shadow-sm rounded-2xl overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr>
                  {["Placa", "Tipo", "Modelo", "Precio est.", "Segmento", "Perfil", "Detecciones", "Hora pico", "Autorizado"].map(h => (
                    <th key={h} className="text-[11px] font-semibold text-[#9CA3AF] uppercase px-4 py-4 border-b border-[#F3F4F6]">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {placas.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="text-center text-[#6B7280] py-10 text-[13px]">
                      No se encontraron placas que coincidan con los filtros.
                    </td>
                  </tr>
                ) : (
                  placas.map(p => {
                    const seg = getSegmentoByPrecio(p.precio_estimado);
                    return (
                      <tr key={p.plate_text} className="border-b border-[#F9FAFB] hover:bg-gray-50/50 transition-colors">
                        <td style={{ fontFamily: "'Geist', sans-serif" }} className="px-4 py-3 text-[14px] font-semibold tracking-wider text-[#1F2937]">{p.plate_text}</td>
                        <td className="px-4 py-3 text-[13px] text-[#4B5563] capitalize">{p.vehicle_type}</td>
                        <td className="px-4 py-3 text-[13px] text-[#4B5563]">{p.modelo || "—"}</td>
                        <td style={{ fontFamily: "'Geist', sans-serif" }} className="px-4 py-3 text-[13px] text-[#1F2937] font-medium">{formatCOP(p.precio_estimado)}</td>
                        <td className="px-4 py-3">
                          <span className={`text-[12px] font-semibold ${seg.color}`}>{seg.label}</span>
                        </td>
                        <td className="px-4 py-3">
                          <span className={`inline-flex items-center gap-1.5 text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${BADGE_STYLES[p.badge]}`}>
                            <span className={`w-1.5 h-1.5 rounded-full ${BADGE_DOT[p.badge]}`} />
                            {p.badge}
                          </span>
                        </td>
                        <td style={{ fontFamily: "'Geist', sans-serif" }} className="px-4 py-3 text-[13px] font-bold text-[#FC6C03]">{p.count}</td>
                        <td style={{ fontFamily: "'Geist', sans-serif" }} className="px-4 py-3 text-[13px] text-[#1F2937]">{p.peak_hour}</td>
                        <td className="px-4 py-3">
                          <span className={`text-[11px] font-semibold px-2.5 py-0.5 rounded-full ${p.authorized ? "bg-[#DCFCE7] text-[#15803D] border border-[#BBF7D0]" : "bg-[#FEE2E2] text-[#B91C1C] border border-[#FECACA]"}`}>
                            {p.authorized ? "Sí" : "No"}
                          </span>
                        </td>
                      </tr>
                    );
                  })
                )}
              </tbody>
            </table>
          </div>
        </div>

      </div>
    </Layout>
  );
}
