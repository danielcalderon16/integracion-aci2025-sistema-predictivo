"use client";

import { useState } from "react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { DisenoMezcla, DisenoMezclaInput, Prediccion } from "@/lib/types";
import { formatApiError } from "@/lib/errors";

const TIPOS_CONSTRUCCION = [
  "Muros de cimentación reforzados",
  "Zapatas",
  "Cimentación Concreto Reforzado",
  "Vigas",
  "Muros reforzados",
  "Columnas de construcción",
  "Pavimentos",
  "Losas",
  "Hormigón en masa",
];
const CONDICIONES_AGRESIVAS = ["Sí", "No", "Moderado", "Severo"];
const TIPOS_CEMENTO = ["UT", "ART", "RS", "MS", "BL", "Otros"];
const PORCENTAJES_LODO = [5, 10, 15, 20, 25];

const DEFAULTS: DisenoMezclaInput = {
  tipo_construccion: "Vigas",
  condiciones_agresivas: "No",
  resistencia_kgcm2: 324,
  densidad_cemento: 3.15,
  tipo_cemento: "UT",
  tamano_nominal_in: 0.5,
  masa_unitaria_grueso: 1667,
  densidad_aparente_grueso: 2610,
  absorcion_grueso: 2.8,
  humedad_grueso: 1.7,
  modulo_finura: 2.6,
  masa_unitaria_fino: 1770,
  densidad_aparente_fino: 2750,
  absorcion_fino: 5.7,
  humedad_fino: 2.5,
  asentamiento_in: 4,
  contenido_aire: 1,
  altura_cilindro: 0.3,
  diametro_cilindro: 0.15,
  num_cilindros: 1,
  porcentaje_lodo: 5,
};

function NumberField({
  label,
  value,
  onChange,
  step = "any",
  min,
}: {
  label: string;
  value: number;
  onChange: (v: number) => void;
  step?: string;
  min?: number;
}) {
  return (
    <label className="block">
      <span className="block text-sm font-medium mb-1">{label}</span>
      <input
        type="number"
        step={step}
        min={min}
        className="w-full border rounded px-3 py-2"
        value={Number.isNaN(value) ? "" : value}
        onChange={(e) => {
          const parsed = parseFloat(e.target.value);
          onChange(Number.isNaN(parsed) ? 0 : parsed);
        }}
        required
      />
    </label>
  );
}

export default function CalculadoraForm() {
  const [form, setForm] = useState<DisenoMezclaInput>(DEFAULTS);
  const [diseno, setDiseno] = useState<DisenoMezcla | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(false);

  const [escoria, setEscoria] = useState(0);
  const [cenizas, setCenizas] = useState(0);
  const [superplastificante, setSuperplastificante] = useState(0);
  const [predicciones, setPredicciones] = useState<Prediccion[] | null>(null);
  const [errorPrediccion, setErrorPrediccion] = useState<string | null>(null);
  const [cargandoPrediccion, setCargandoPrediccion] = useState(false);

  function set<K extends keyof DisenoMezclaInput>(campo: K, valor: DisenoMezclaInput[K]) {
    setForm((f) => ({ ...f, [campo]: valor }));
  }

  async function calcular() {
    setError(null);
    setCargando(true);
    setDiseno(null);
    setPredicciones(null);
    try {
      const res = await fetch("/api/aci/calcular", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      const data = await res.json();
      if (!res.ok) {
        setError(formatApiError(data.detail, "No se pudo calcular el diseño. Revisa los valores ingresados."));
        return;
      }
      setDiseno(data);
    } finally {
      setCargando(false);
    }
  }

  async function generarCurva() {
    if (!diseno) return;
    setErrorPrediccion(null);
    setCargandoPrediccion(true);
    try {
      const res = await fetch("/api/prediccion", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          diseno_id: diseno.id,
          edades_dias: [3, 7, 14, 28],
          escoria,
          cenizas,
          superplastificante,
        }),
      });
      const data = await res.json();
      if (!res.ok) {
        setErrorPrediccion(formatApiError(data.detail, "No se pudo generar la predicción."));
        return;
      }
      setPredicciones(data);
    } finally {
      setCargandoPrediccion(false);
    }
  }

  const chartData = predicciones
    ? [...predicciones]
        .sort((a, b) => a.edad_dias - b.edad_dias)
        .map((p) => ({ edad: `${p.edad_dias}d`, resistencia: p.resistencia_predicha_mpa }))
    : [];

  return (
    <div className="space-y-8">
      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="font-semibold text-lg mb-4">Condiciones generales</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <label className="block">
            <span className="block text-sm font-medium mb-1">Tipo de construcción</span>
            <select
              className="w-full border rounded px-3 py-2"
              value={form.tipo_construccion}
              onChange={(e) => set("tipo_construccion", e.target.value)}
            >
              {TIPOS_CONSTRUCCION.map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </label>
          <label className="block">
            <span className="block text-sm font-medium mb-1">¿Expuesto a condiciones agresivas?</span>
            <select
              className="w-full border rounded px-3 py-2"
              value={form.condiciones_agresivas}
              onChange={(e) => set("condiciones_agresivas", e.target.value)}
            >
              {CONDICIONES_AGRESIVAS.map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </label>
          <NumberField
            label="Resistencia requerida f'c (Kg/cm²)"
            value={form.resistencia_kgcm2}
            onChange={(v) => set("resistencia_kgcm2", v)}
            min={0.01}
          />
          <NumberField
            label="Densidad del cemento (g/cm³)"
            value={form.densidad_cemento}
            onChange={(v) => set("densidad_cemento", v)}
            min={0.01}
          />
          <label className="block">
            <span className="block text-sm font-medium mb-1">Tipo de cemento</span>
            <select
              className="w-full border rounded px-3 py-2"
              value={form.tipo_cemento}
              onChange={(e) => set("tipo_cemento", e.target.value)}
            >
              {TIPOS_CEMENTO.map((t) => (
                <option key={t}>{t}</option>
              ))}
            </select>
          </label>
        </div>
      </section>

      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="font-semibold text-lg mb-4">Agregado grueso</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <NumberField
            label="Tamaño máx. nominal (in)"
            value={form.tamano_nominal_in}
            onChange={(v) => set("tamano_nominal_in", v)}
            min={0.01}
          />
          <NumberField
            label="Masa unitaria compacta (Kg/m³)"
            value={form.masa_unitaria_grueso}
            onChange={(v) => set("masa_unitaria_grueso", v)}
            min={0.01}
          />
          <NumberField
            label="Densidad aparente (Kg/m³)"
            value={form.densidad_aparente_grueso}
            onChange={(v) => set("densidad_aparente_grueso", v)}
            min={0.01}
          />
          <NumberField
            label="Absorción (%)"
            value={form.absorcion_grueso}
            onChange={(v) => set("absorcion_grueso", v)}
            min={0}
          />
          <NumberField
            label="Humedad natural (%)"
            value={form.humedad_grueso}
            onChange={(v) => set("humedad_grueso", v)}
            min={0}
          />
        </div>
      </section>

      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="font-semibold text-lg mb-4">Agregado fino</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <NumberField
            label="Módulo de finura"
            value={form.modulo_finura}
            onChange={(v) => set("modulo_finura", v)}
            min={0.01}
          />
          <NumberField
            label="Masa unitaria compacta (Kg/m³)"
            value={form.masa_unitaria_fino}
            onChange={(v) => set("masa_unitaria_fino", v)}
            min={0.01}
          />
          <NumberField
            label="Densidad aparente (Kg/m³)"
            value={form.densidad_aparente_fino}
            onChange={(v) => set("densidad_aparente_fino", v)}
            min={0.01}
          />
          <NumberField
            label="Absorción (%)"
            value={form.absorcion_fino}
            onChange={(v) => set("absorcion_fino", v)}
            min={0}
          />
          <NumberField
            label="Humedad natural (%)"
            value={form.humedad_fino}
            onChange={(v) => set("humedad_fino", v)}
            min={0}
          />
        </div>
      </section>

      <section className="bg-white rounded-lg shadow p-6">
        <h2 className="font-semibold text-lg mb-4">Mezcla, espécimen y proporción cemento/lodo</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <NumberField
            label="Asentamiento (in)"
            value={form.asentamiento_in}
            onChange={(v) => set("asentamiento_in", v)}
            min={0.01}
          />
          <NumberField
            label="Contenido de aire atrapado (%)"
            value={form.contenido_aire}
            onChange={(v) => set("contenido_aire", v)}
            min={0}
          />
          <NumberField
            label="Altura del cilindro (m)"
            value={form.altura_cilindro}
            onChange={(v) => set("altura_cilindro", v)}
            min={0.01}
          />
          <NumberField
            label="Diámetro del cilindro (m)"
            value={form.diametro_cilindro}
            onChange={(v) => set("diametro_cilindro", v)}
            min={0.01}
          />
          <NumberField
            label="Número de cilindros"
            value={form.num_cilindros}
            onChange={(v) => set("num_cilindros", v)}
            step="1"
            min={1}
          />
          <label className="block">
            <span className="block text-sm font-medium mb-1">Porcentaje de lodo (%)</span>
            <select
              className="w-full border rounded px-3 py-2"
              value={form.porcentaje_lodo}
              onChange={(e) => set("porcentaje_lodo", parseInt(e.target.value, 10))}
            >
              {PORCENTAJES_LODO.map((p) => (
                <option key={p} value={p}>
                  {p}%
                </option>
              ))}
            </select>
          </label>
        </div>
      </section>

      {error && (
        <div className="bg-amber-50 border border-amber-300 text-amber-800 rounded-lg p-4 whitespace-pre-line text-sm">
          ⚠️ {error}
        </div>
      )}

      <button
        onClick={calcular}
        disabled={cargando}
        className="bg-blue-900 text-white px-6 py-3 rounded font-semibold hover:bg-blue-800 disabled:opacity-50"
      >
        {cargando ? "Calculando..." : "🧮 Calcular"}
      </button>

      {diseno && (
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold text-lg mb-4">Resultados — Folio {diseno.folio}</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-1 text-sm mb-4">
            <p>f&apos;c teórico: <b>{diseno.resistencia_teorica_kgcm2} Kg/cm²</b> ({diseno.resistencia_teorica_mpa} MPa)</p>
            <p>Relación agua/cemento: <b>{diseno.relacion_agua_cemento}</b></p>
            <p>Factor cemento: <b>{diseno.factor_cemento} Kg/m³</b></p>
            <p>Agua de mezclado: <b>{diseno.agua_mezclado} Lt/m³</b></p>
            <p>Peso real agregado grueso: <b>{diseno.peso_real_grueso} Kg/m³</b></p>
            <p>Peso real agregado fino: <b>{diseno.peso_real_fino} Kg/m³</b></p>
          </div>
          <table className="w-full text-sm border-collapse">
            <thead>
              <tr className="bg-slate-100">
                <th className="border px-2 py-1 text-left">Cantidades para ensayo</th>
                <th className="border px-2 py-1 text-right">Valor</th>
              </tr>
            </thead>
            <tbody>
              <tr><td className="border px-2 py-1">Cemento (Kg)</td><td className="border px-2 py-1 text-right">{diseno.cemento_cant}</td></tr>
              <tr><td className="border px-2 py-1">Lodo (Kg)</td><td className="border px-2 py-1 text-right">{diseno.lodo_cant}</td></tr>
              <tr><td className="border px-2 py-1">Arena (Kg)</td><td className="border px-2 py-1 text-right">{diseno.arena_cant}</td></tr>
              <tr><td className="border px-2 py-1">Grava (Kg)</td><td className="border px-2 py-1 text-right">{diseno.grava_cant}</td></tr>
              <tr><td className="border px-2 py-1">Agua (L)</td><td className="border px-2 py-1 text-right">{diseno.agua_cant}</td></tr>
            </tbody>
          </table>

          <div className="flex gap-3 mt-4">
            <a
              href={`/api/historial/${diseno.id}/export/excel`}
              className="bg-emerald-700 text-white px-4 py-2 rounded text-sm font-medium hover:bg-emerald-800"
            >
              💾 Exportar Excel
            </a>
            <a
              href={`/api/historial/${diseno.id}/export/pdf`}
              className="bg-slate-700 text-white px-4 py-2 rounded text-sm font-medium hover:bg-slate-800"
            >
              🧾 Exportar PDF
            </a>
          </div>
        </section>
      )}

      {diseno && (
        <section className="bg-white rounded-lg shadow p-6">
          <h2 className="font-semibold text-lg mb-2">🤖 Predicción de resistencia por IA</h2>
          <p className="text-sm text-slate-600 mb-4">
            Usa el cemento, agua y agregados ya calculados arriba y estima la resistencia a 3, 7,
            14 y 28 días de curado (modelo entrenado con el UCI Concrete Compressive Strength
            Data Set).
          </p>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-4">
            <NumberField label="Escoria (Kg/m³, opcional)" value={escoria} onChange={setEscoria} min={0} />
            <NumberField
              label="Cenizas volantes (Kg/m³, opcional)"
              value={cenizas}
              onChange={setCenizas}
              min={0}
            />
            <NumberField
              label="Superplastificante (Kg/m³, opcional)"
              value={superplastificante}
              onChange={setSuperplastificante}
              min={0}
            />
          </div>
          {errorPrediccion && (
            <div className="bg-amber-50 border border-amber-300 text-amber-800 rounded-lg p-4 whitespace-pre-line text-sm mb-3">
              ⚠️ {errorPrediccion}
            </div>
          )}
          <button
            onClick={generarCurva}
            disabled={cargandoPrediccion}
            className="bg-indigo-700 text-white px-6 py-3 rounded font-semibold hover:bg-indigo-800 disabled:opacity-50"
          >
            {cargandoPrediccion ? "Prediciendo..." : "🔮 Generar curva de resistencia"}
          </button>

          {predicciones && (
            <div className="mt-6">
              {predicciones.some((p) => p.extrapolado) && (
                <div className="bg-amber-50 border border-amber-300 text-amber-800 rounded-lg p-4 text-sm mb-4">
                  ⚠️ Uno o más puntos de esta curva (marcados con *) usan variables fuera del
                  rango de combinaciones con el que se entrenó el modelo de IA (UCI Concrete
                  Compressive Strength Data Set). El sistema acotó esos valores al límite
                  conocido para evitar una predicción errática, pero esos puntos específicos
                  tienen menor confiabilidad que el resto de la curva.
                </div>
              )}
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="edad" />
                    <YAxis label={{ value: "MPa", angle: -90, position: "insideLeft" }} />
                    <Tooltip />
                    <Legend />
                    <ReferenceLine
                      y={diseno.resistencia_teorica_mpa}
                      stroke="#dc2626"
                      strokeDasharray="4 4"
                      label={{ value: "f'c teórico", position: "insideTopRight", fill: "#dc2626" }}
                    />
                    <Line
                      type="monotone"
                      dataKey="resistencia"
                      name="Resistencia predicha (MPa)"
                      stroke="#4338ca"
                      strokeWidth={2}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <table className="w-full text-sm border-collapse mt-4">
                <thead>
                  <tr className="bg-slate-100">
                    <th className="border px-2 py-1">Edad (días)</th>
                    <th className="border px-2 py-1">Resistencia predicha (MPa)</th>
                  </tr>
                </thead>
                <tbody>
                  {[...predicciones]
                    .sort((a, b) => a.edad_dias - b.edad_dias)
                    .map((p) => (
                      <tr key={p.id} className={p.extrapolado ? "bg-amber-50" : undefined}>
                        <td className="border px-2 py-1 text-center">{p.edad_dias}</td>
                        <td className="border px-2 py-1 text-center">
                          {p.resistencia_predicha_mpa}
                          {p.extrapolado && <span className="text-amber-600"> *</span>}
                        </td>
                      </tr>
                    ))}
                </tbody>
              </table>
            </div>
          )}
        </section>
      )}
    </div>
  );
}
