"""
Generación de reportes (Excel / PDF) de un diseño de mezcla + sus
predicciones, en memoria (sin escribir a disco), basado en data_io.py.
"""
import io

import pandas as pd
from fpdf import FPDF

from app.models.diseno import DisenoMezcla


def _filas_diseno(diseno: DisenoMezcla) -> list[tuple[str, object]]:
    return [
        ("Folio", diseno.folio),
        ("Tipo de construcción", diseno.tipo_construccion),
        ("f'c teórico (Kg/cm²)", diseno.resistencia_teorica_kgcm2),
        ("f'c teórico (MPa)", diseno.resistencia_teorica_mpa),
        ("Relación agua/cemento", diseno.relacion_agua_cemento),
        ("Factor cemento (Kg/m³)", diseno.factor_cemento),
        ("Agua de mezclado (Lt/m³)", diseno.agua_mezclado),
        ("Peso real agregado grueso (Kg/m³)", diseno.peso_real_grueso),
        ("Peso real agregado fino (Kg/m³)", diseno.peso_real_fino),
        ("Cemento para ensayo (Kg)", diseno.cemento_cant),
        ("Lodo para ensayo (Kg)", diseno.lodo_cant),
        ("Arena para ensayo (Kg)", diseno.arena_cant),
        ("Grava para ensayo (Kg)", diseno.grava_cant),
        ("Agua para ensayo (L)", diseno.agua_cant),
    ]


def exportar_excel(diseno: DisenoMezcla) -> io.BytesIO:
    df = pd.DataFrame(_filas_diseno(diseno), columns=["Parámetro", "Valor"])
    if diseno.predicciones:
        df_pred = pd.DataFrame(
            [
                {
                    "Edad (días)": p.edad_dias,
                    "Resistencia predicha (MPa)": p.resistencia_predicha_mpa,
                }
                for p in sorted(diseno.predicciones, key=lambda p: p.edad_dias)
            ]
        )
    else:
        df_pred = pd.DataFrame(columns=["Edad (días)", "Resistencia predicha (MPa)"])

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="Diseño ACI 2025", index=False)
        df_pred.to_excel(writer, sheet_name="Predicción IA", index=False)
    buffer.seek(0)
    return buffer


def exportar_pdf(diseno: DisenoMezcla) -> io.BytesIO:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Diseño de Mezcla ACI 2025", ln=1, align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)
    for etiqueta, valor in _filas_diseno(diseno):
        pdf.cell(0, 8, f"{etiqueta}: {valor}", ln=1)

    if diseno.predicciones:
        pdf.ln(4)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Predicción de resistencia por edad de curado (IA)", ln=1)
        pdf.set_font("Helvetica", "", 11)
        for p in sorted(diseno.predicciones, key=lambda p: p.edad_dias):
            pdf.cell(0, 8, f"{p.edad_dias} días: {p.resistencia_predicha_mpa} MPa", ln=1)

    buffer = io.BytesIO(pdf.output())
    buffer.seek(0)
    return buffer
