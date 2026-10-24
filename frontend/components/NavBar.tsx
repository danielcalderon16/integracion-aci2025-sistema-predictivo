"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import type { Usuario } from "@/lib/types";

export default function NavBar({ usuario }: { usuario: Usuario | null }) {
  const router = useRouter();

  async function cerrarSesion() {
    await fetch("/api/auth/logout", { method: "POST" });
    router.push("/login");
    router.refresh();
  }

  return (
    <header className="bg-blue-900 text-white shadow">
      <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="font-bold text-lg">
          ACI 2025 + Predicción IA
        </Link>
        <nav className="flex items-center gap-4 text-sm">
          {usuario ? (
            <>
              <Link href="/calculadora" className="hover:underline">
                Calculadora
              </Link>
              <Link href="/historial" className="hover:underline">
                Historial
              </Link>
              {usuario.is_admin && (
                <Link href="/usuarios" className="hover:underline">
                  Usuarios
                </Link>
              )}
              <span className="text-blue-200">{usuario.username}</span>
              <button
                onClick={cerrarSesion}
                className="bg-red-600 hover:bg-red-700 px-3 py-1.5 rounded font-medium"
              >
                Cerrar sesión
              </button>
            </>
          ) : (
            <>
              <Link href="/login" className="hover:underline">
                Iniciar sesión
              </Link>
              <Link
                href="/registro"
                className="bg-white text-blue-900 px-3 py-1.5 rounded font-medium hover:bg-blue-50"
              >
                Registrarse
              </Link>
            </>
          )}
        </nav>
      </div>
    </header>
  );
}
