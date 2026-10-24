"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { formatApiError } from "@/lib/errors";
import type { Rol } from "@/lib/types";

export default function RegistroPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [nombreCompleto, setNombreCompleto] = useState("");
  const [codigo, setCodigo] = useState("");
  const [rol, setRol] = useState<Rol>("estudiante");
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setCargando(true);
    try {
      const res = await fetch("/api/auth/register", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          email,
          password,
          nombre_completo: nombreCompleto,
          codigo,
          rol,
        }),
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        setError(formatApiError(data.detail, "No se pudo completar el registro"));
        return;
      }

      const loginRes = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }),
      });
      if (loginRes.ok) {
        router.push("/calculadora");
        router.refresh();
      } else {
        router.push("/login");
      }
    } finally {
      setCargando(false);
    }
  }

  return (
    <div className="max-w-sm mx-auto px-4 py-16">
      <h1 className="text-2xl font-bold mb-6">Crear cuenta</h1>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Nombre completo</label>
          <input
            className="w-full border rounded px-3 py-2"
            value={nombreCompleto}
            onChange={(e) => setNombreCompleto(e.target.value)}
            minLength={3}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Código institucional</label>
          <input
            className="w-full border rounded px-3 py-2"
            value={codigo}
            onChange={(e) => setCodigo(e.target.value)}
            minLength={3}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Tipo de cuenta</label>
          <select
            className="w-full border rounded px-3 py-2"
            value={rol}
            onChange={(e) => setRol(e.target.value as Rol)}
          >
            <option value="estudiante">Estudiante</option>
            <option value="profesor">Profesor</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Usuario</label>
          <input
            className="w-full border rounded px-3 py-2"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            minLength={3}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Correo</label>
          <input
            type="email"
            className="w-full border rounded px-3 py-2"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Contraseña</label>
          <input
            type="password"
            className="w-full border rounded px-3 py-2"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            minLength={8}
            required
          />
        </div>
        {error && <p className="text-red-600 text-sm whitespace-pre-line">{error}</p>}
        <button
          type="submit"
          disabled={cargando}
          className="w-full bg-blue-900 text-white py-2 rounded font-semibold hover:bg-blue-800 disabled:opacity-50"
        >
          {cargando ? "Creando cuenta..." : "Registrarme"}
        </button>
      </form>
      <p className="text-sm text-slate-600 mt-4">
        ¿Ya tienes cuenta?{" "}
        <Link href="/login" className="text-blue-900 font-medium hover:underline">
          Inicia sesión
        </Link>
      </p>
    </div>
  );
}
