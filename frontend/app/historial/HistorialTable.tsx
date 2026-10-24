"use client";

import { useState } from "react";
import type { DisenoMezcla } from "@/lib/types";

export default function HistorialTable({
  disenosIniciales,
  usuarioActualId,
  esAdmin,
  mostrarAutor,
}: {
  disenosIniciales: DisenoMezcla[];
  usuarioActualId: number;
  esAdmin: boolean;
  mostrarAutor: boolean;
}) {
  const [disenos, setDisenos] = useState(disenosIniciales);

  async function eliminar(id: number) {
    if (!confirm("¿Eliminar este diseño y sus predicciones?")) return;
    const res = await fetch(`/api/historial/${id}`, { method: "DELETE" });
    if (res.ok) setDisenos((prev) => prev.filter((d) => d.id !== id));
  }

  if (disenos.length === 0) {
    return <p className="text-slate-600">Aún no hay diseños guardados.</p>;
  }

  return (
    <div className="overflow-x-auto bg-white rounded-lg shadow">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-slate-100 text-left">
            <th className="px-3 py-2">Folio</th>
            {mostrarAutor && <th className="px-3 py-2">Estudiante</th>}
            <th className="px-3 py-2">Tipo</th>
            <th className="px-3 py-2">f&apos;c teórico (MPa)</th>
            <th className="px-3 py-2">Predicción 28d (MPa)</th>
            <th className="px-3 py-2">Fecha</th>
            <th className="px-3 py-2">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {disenos.map((d) => {
            const pred28 = d.predicciones.find((p) => p.edad_dias === 28);
            const puedeEliminar = esAdmin || d.usuario_id === usuarioActualId;
            return (
              <tr key={d.id} className="border-t">
                <td className="px-3 py-2 font-mono text-xs">{d.folio}</td>
                {mostrarAutor && (
                  <td className="px-3 py-2">{d.autor_nombre ?? d.autor_username ?? "—"}</td>
                )}
                <td className="px-3 py-2">{d.tipo_construccion}</td>
                <td className="px-3 py-2">{d.resistencia_teorica_mpa}</td>
                <td className="px-3 py-2">{pred28 ? pred28.resistencia_predicha_mpa : "—"}</td>
                <td className="px-3 py-2 text-xs text-slate-500">
                  {new Date(d.created_at).toLocaleString()}
                </td>
                <td className="px-3 py-2 space-x-2 whitespace-nowrap">
                  <a
                    href={`/api/historial/${d.id}/export/excel`}
                    className="text-emerald-700 hover:underline"
                  >
                    Excel
                  </a>
                  <a href={`/api/historial/${d.id}/export/pdf`} className="text-slate-700 hover:underline">
                    PDF
                  </a>
                  {puedeEliminar && (
                    <button onClick={() => eliminar(d.id)} className="text-red-600 hover:underline">
                      Eliminar
                    </button>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
