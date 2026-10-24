import Link from "next/link";
import { getCurrentUser } from "@/lib/api";

export default async function HomePage() {
  const usuario = await getCurrentUser();

  return (
    <div className="max-w-4xl mx-auto px-4 py-16 text-center">
      <h1 className="text-3xl font-bold mb-4">
        Plataforma Unificada ACI 2025 + Predicción de Resistencia por IA
      </h1>
      <p className="text-slate-600 mb-8">
        Calcula el diseño de mezcla según la norma ACI 2025 y obtén, en el mismo flujo, la
        predicción de resistencia a distintas edades de curado — entrenada con el UCI Concrete
        Compressive Strength Data Set (1030 ensayos reales de laboratorio).
      </p>
      <Link
        href={usuario ? "/calculadora" : "/login"}
        className="inline-block bg-blue-900 text-white px-6 py-3 rounded font-semibold hover:bg-blue-800"
      >
        {usuario ? "Ir a la calculadora" : "Iniciar sesión para comenzar"}
      </Link>
    </div>
  );
}
