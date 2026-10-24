"use client";

import { useState } from "react";
import type { Rol, Usuario } from "@/lib/types";

export default function UsuariosPanel({
  usuarioActualId,
  usuariosIniciales,
}: {
  usuarioActualId: number;
  usuariosIniciales: Usuario[];
}) {
  const [usuarios, setUsuarios] = useState(usuariosIniciales);
  const [error, setError] = useState<string | null>(null);

  async function actualizar(u: Usuario, cambios: Partial<Pick<Usuario, "is_admin" | "rol">>) {
    setError(null);
    const res = await fetch(`/api/usuarios/${u.id}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(cambios),
    });
    const data = await res.json();
    if (!res.ok) {
      setError(data.detail ?? "No se pudo actualizar el usuario");
      return;
    }
    setUsuarios((prev) => prev.map((x) => (x.id === u.id ? data : x)));
  }

  async function eliminar(u: Usuario) {
    if (u.id === usuarioActualId) {
      setError("No puedes eliminar tu propia cuenta");
      return;
    }
    if (!confirm(`¿Eliminar al usuario ${u.username}?`)) return;
    const res = await fetch(`/api/usuarios/${u.id}`, { method: "DELETE" });
    if (res.ok) setUsuarios((prev) => prev.filter((x) => x.id !== u.id));
  }

  return (
    <div className="bg-white rounded-lg shadow overflow-x-auto">
      {error && <p className="text-red-600 p-4">{error}</p>}
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-slate-100 text-left">
            <th className="px-3 py-2">Nombre</th>
            <th className="px-3 py-2">Código</th>
            <th className="px-3 py-2">Usuario</th>
            <th className="px-3 py-2">Correo</th>
            <th className="px-3 py-2">Rol</th>
            <th className="px-3 py-2">Admin</th>
            <th className="px-3 py-2">Acciones</th>
          </tr>
        </thead>
        <tbody>
          {usuarios.map((u) => (
            <tr key={u.id} className="border-t">
              <td className="px-3 py-2">{u.nombre_completo}</td>
              <td className="px-3 py-2 font-mono text-xs">{u.codigo}</td>
              <td className="px-3 py-2">{u.username}</td>
              <td className="px-3 py-2">{u.email}</td>
              <td className="px-3 py-2">
                <select
                  className="border rounded px-2 py-1 text-sm"
                  value={u.rol}
                  onChange={(e) => actualizar(u, { rol: e.target.value as Rol })}
                >
                  <option value="estudiante">Estudiante</option>
                  <option value="profesor">Profesor</option>
                </select>
              </td>
              <td className="px-3 py-2">{u.is_admin ? "Sí" : "No"}</td>
              <td className="px-3 py-2 space-x-3 whitespace-nowrap">
                <button
                  onClick={() => actualizar(u, { is_admin: !u.is_admin })}
                  className="text-blue-900 hover:underline"
                >
                  {u.is_admin ? "Quitar admin" : "Hacer admin"}
                </button>
                <button onClick={() => eliminar(u)} className="text-red-600 hover:underline">
                  Eliminar
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
