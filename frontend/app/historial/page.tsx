import { redirect } from "next/navigation";
import { backendFetch, getCurrentUser } from "@/lib/api";
import type { DisenoMezcla } from "@/lib/types";
import HistorialTable from "./HistorialTable";

export default async function HistorialPage() {
  const usuario = await getCurrentUser();
  if (!usuario) redirect("/login?next=/historial");

  const res = await backendFetch("/historial");
  const disenos: DisenoMezcla[] = res.ok ? await res.json() : [];
  const puedeVerTodo = usuario.is_admin || usuario.rol === "profesor";

  return (
    <div className="max-w-6xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-2">Historial de Diseños</h1>
      {puedeVerTodo && (
        <p className="text-sm text-slate-600 mb-4">
          Como {usuario.rol === "profesor" ? "profesor" : "administrador"}, estás viendo los
          diseños de todos los estudiantes.
        </p>
      )}
      <HistorialTable
        disenosIniciales={disenos}
        usuarioActualId={usuario.id}
        esAdmin={usuario.is_admin}
        mostrarAutor={puedeVerTodo}
      />
    </div>
  );
}
