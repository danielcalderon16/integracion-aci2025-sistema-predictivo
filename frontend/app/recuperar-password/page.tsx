"use client";

import { useState, FormEvent } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { formatApiError } from "@/lib/errors";

export default function RecuperarPasswordPage() {
  const router = useRouter();
  const [username, setUsername] = useState("");
  const [codigo, setCodigo] = useState("");
  const [nombreCompleto, setNombreCompleto] = useState("");
  const [nuevaPassword, setNuevaPassword] = useState("");
  const [confirmar, setConfirmar] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [exito, setExito] = useState(false);
  const [cargando, setCargando] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (nuevaPassword !== confirmar) {
      setError("Las contraseñas no coinciden");
      return;
    }

    setCargando(true);
    try {
      const res = await fetch("/api/auth/recuperar-password", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          username,
          codigo,
          nombre_completo: nombreCompleto,
          nueva_password: nuevaPassword,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(formatApiError(data.detail, "No se pudo recuperar la cuenta."));
        return;
      }
      setExito(true);
      setTimeout(() => router.push("/login"), 2000);
    } finally {
      setCargando(false);
    }
  }

  if (exito) {
    return (
      <div className="max-w-sm mx-auto px-4 py-16 text-center">
        <h1 className="text-2xl font-bold mb-4">Contraseña actualizada</h1>
        <p className="text-slate-600">Ya puedes iniciar sesión con tu nueva contraseña. Redirigiendo…</p>
      </div>
    );
  }

  return (
    <div className="max-w-sm mx-auto px-4 py-16">
      <h1 className="text-2xl font-bold mb-2">Recuperar contraseña</h1>
      <p className="text-sm text-slate-600 mb-6">
        Ingresa tu usuario, tu código institucional y tu nombre completo tal como quedaron
        registrados. Si los tres coinciden, podrás definir una nueva contraseña.
      </p>
      <form onSubmit={onSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-1">Usuario</label>
          <input
            className="w-full border rounded px-3 py-2"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Código institucional</label>
          <input
            className="w-full border rounded px-3 py-2"
            value={codigo}
            onChange={(e) => setCodigo(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Nombre completo</label>
          <input
            className="w-full border rounded px-3 py-2"
            value={nombreCompleto}
            onChange={(e) => setNombreCompleto(e.target.value)}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Nueva contraseña</label>
          <input
            type="password"
            className="w-full border rounded px-3 py-2"
            value={nuevaPassword}
            onChange={(e) => setNuevaPassword(e.target.value)}
            minLength={8}
            required
          />
        </div>
        <div>
          <label className="block text-sm font-medium mb-1">Confirmar nueva contraseña</label>
          <input
            type="password"
            className="w-full border rounded px-3 py-2"
            value={confirmar}
            onChange={(e) => setConfirmar(e.target.value)}
            minLength={8}
            required
          />
        </div>
        {error && <p className="text-red-600 text-sm">{error}</p>}
        <button
          type="submit"
          disabled={cargando}
          className="w-full bg-blue-900 text-white py-2 rounded font-semibold hover:bg-blue-800 disabled:opacity-50"
        >
          {cargando ? "Verificando..." : "Restablecer contraseña"}
        </button>
      </form>
      <p className="text-sm text-slate-600 mt-4">
        <Link href="/login" className="text-blue-900 font-medium hover:underline">
          Volver a iniciar sesión
        </Link>
      </p>
    </div>
  );
}
