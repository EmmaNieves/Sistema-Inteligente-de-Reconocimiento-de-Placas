"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const NAV = [
  { href: "/dashboard",   icon: "⬡", label: "Dashboard" },
  { href: "/vehicles",    icon: "🚗", label: "Vehículos" },
  { href: "/detections",  icon: "📷", label: "Detecciones" },
  { href: "/cameras",     icon: "🎥", label: "Cámaras" },
  { href: "/stats",       icon: "📊", label: "Estadísticas" },
  { href: "/alerts",      icon: "🚨", label: "Alertas" },
];

export default function Sidebar() {
  const path = usePathname();

  return (
    <aside className="w-56 shrink-0 bg-[#111827] border-r border-[#1e3a5f] flex flex-col min-h-screen">
      {/* Logo */}
      <div className="px-5 py-5 border-b border-[#1e3a5f]">
        <span className="text-[#00d4ff] font-mono font-bold text-sm tracking-widest">
          ◈ PLACACONTROL
        </span>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-4 space-y-1 px-2">
        {NAV.map(({ href, icon, label }) => {
          const active = path.startsWith(href);
          return (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-mono transition-colors
                ${active
                  ? "bg-[#00d4ff]/10 text-[#00d4ff] border border-[#00d4ff]/30"
                  : "text-slate-400 hover:bg-[#1a2235] hover:text-slate-200"
                }`}
            >
              <span>{icon}</span>
              <span>{label}</span>
            </Link>
          );
        })}
      </nav>

      {/* Footer */}
      <div className="px-5 py-4 border-t border-[#1e3a5f]">
        <p className="text-[10px] font-mono text-slate-600">YOLOv8 · PaddleOCR · FastAPI</p>
      </div>
    </aside>
  );
}
