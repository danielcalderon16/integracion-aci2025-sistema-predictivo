import { redirect } from "next/navigation";
import { backendFetch, getCurrentUser } from "@/lib/api";
import type { Usuario } from "@/lib/types";
import UsuariosPanel from "./UsuariosPanel";

export default async function UsuariosPage() {
  const usuario = await getCurrentUser();
  if (!usuario) redirect("/login?next=/usuarios");
  if (!usuario.is_admin) redirect("/calculadora");

  const res = await backendFetch("/usuarios");
  const usuarios: Usuario[] = res.ok ? await res.json() : [];

  return (
    <div className="max-w-4xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-6">Gestión de Usuarios</h1>
      <UsuariosPanel usuarioActualId={usuario.id} usuariosIniciales={usuarios} />
    </div>
  );
}
