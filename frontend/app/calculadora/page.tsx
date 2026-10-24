import { redirect } from "next/navigation";
import { getCurrentUser } from "@/lib/api";
import CalculadoraForm from "./CalculadoraForm";

export default async function CalculadoraPage() {
  const usuario = await getCurrentUser();
  if (!usuario) redirect("/login?next=/calculadora");

  return (
    <div className="max-w-5xl mx-auto px-4 py-10">
      <h1 className="text-2xl font-bold mb-6">Calculadora de Diseño de Mezcla ACI 2025</h1>
      <CalculadoraForm />
    </div>
  );
}
