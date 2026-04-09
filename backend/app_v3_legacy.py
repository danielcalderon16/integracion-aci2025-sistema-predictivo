# app_v2.py
import streamlit as st
import pandas as pd
import numpy as np
import os
import io
import base64
from datetime import datetime

# módulos internos (asegúrate que están en la misma carpeta)
import data_io
import database

# ---------------------------------------------------------
# CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="Automatización ACI 2025 - v2", layout="wide", page_icon="🧱")

# ---------------------------------------------------------
# CSS (copiado/adaptado de tu versión)
# ---------------------------------------------------------
st.markdown("""
<style>
.logo-container {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: -25px;
    margin-bottom: 25px;
}
.header {
    background-color: #1f4a93;
    color: white;
    padding: 20px;
    border-radius: 10px;
    font-size: 26px;
    font-weight: bold;
    text-align: center;
    margin-bottom: 25px;
}
section[data-testid="stSidebar"] {
    background-color: #2f56d6 !important;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
div.stButton > button {
    background-color: #2f56d6;
    color: white;
    font-weight: bold;
    border-radius: 6px;
    border: none;
}
div.stButton > button:hover {
    background-color: #1f4a93;
}
.table-style {
    border-collapse: collapse;
    width: 100%;
    margin-bottom: 30px;
}
.table-style th {
    background-color: #f4f4f4;
    color: black;
    text-align: center;
    border: 1px solid black;
    font-weight: bold;
}
.table-style td {
    border: 1px solid black;
    text-align: center;
    padding: 6px;
}
.section-title {
    background-color: #fde9d9;
    font-weight: bold;
    font-style: italic;
    text-align: center;
    border: 1px solid black;
}
.value-red {
    color: red;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# LOGO
# ---------------------------------------------------------
logo_path = "logo_udes.png"
def mostrar_logo_superior():
    if os.path.exists(logo_path):
        with open(logo_path, "rb") as img:
            logo_bytes = base64.b64encode(img.read()).decode()
        st.markdown(f"""
        <div class="logo-container">
            <img src="data:image/png;base64,{logo_bytes}" alt="Logo UDES" width="140" style="border-radius:12px;">
        </div>
        """, unsafe_allow_html=True)
mostrar_logo_superior()

st.markdown('<div class="header">AUTOMATIZACIÓN ACI 2025 - UNIVERSIDAD DE SANTANDER</div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# PATHS: usa aci2025 como nombre de base de datos (según pediste)
# ---------------------------------------------------------
EXCEL_FILE = "ACI2025.xlsm"
DB_FILE = "aci2025.db"   # manteniendo el nombre que pediste

# inicializar DB (creará archivo si no existe)
database.init_db()

# ---------------------------------------------------------
# CACHÉ: lectura del archivo excel TABLAS
# ---------------------------------------------------------
@st.cache_data(show_spinner=False)
def cargar_tablas_excel(path=EXCEL_FILE):
    """
    Intenta leer la hoja 'TABLAS' del archivo ACI2025.xlsm.
    Devuelve DataFrame completo (limpio) o None si falla.
    """
    if not os.path.exists(path):
        return None
    try:
        df = pd.read_excel(path, sheet_name="TABLAS", engine="openpyxl", header=0)
        # limpieza básica: strip a headers
        df.columns = df.columns.astype(str).str.strip()
        return df
    except Exception as e:
        st.warning(f"No se pudo leer {path}: {e}")
        return None

df_tablas = cargar_tablas_excel()

# ---------------------------------------------------------
# UTILIDADES: replicar fórmulas de excel que pediste
# ---------------------------------------------------------
# Mapeo aproximado de tamaños (inches) a rótulos comunes en la tabla
TAMANOS_MAP = {
    0.375: ['3/8', '3/8"', '3/8 in', '3/8in', '0.375'],
    0.5:   ['1/2', '1/2"', '1/2 in', '1/2in', '0.5'],
    0.75:  ['3/4', '3/4"', '3/4 in', '3/4in', '0.75'],
    1.0:   ['1', '1"', '1 in', '1in', '1.0'],
    1.5:   ['1 1/2', '1-1/2', '1.5', '1 1/2"', '1.5"'],
    2.0:   ['2', '2"', '2 in', '2in', '2.0'],
    3.0:   ['3', '3"', '3 in', '3in', '3.0'],
    6.0:   ['6', '6"', '6 in', '6in', '6.0']
}

def encontrar_columna_por_tamano(df, tamano_in):
    """Busca la columna en df que mejor coincida con el tamaño (tratando nombres comunes)."""
    if df is None:
        return None
    posibles = df.columns.astype(str).tolist()
    candidatos = TAMANOS_MAP.get(float(tamano_in), [])
    # Buscar coincidencia exacta (strip)
    for c in candidatos:
        for col in posibles:
            if c.lower() == col.strip().lower():
                return col
    # Si no encontró por nombres comunes, intenta columnas convertibles a número y comparar
    for col in posibles:
        try:
            val = float(col)
            if abs(val - float(tamano_in)) < 0.01:
                return col
        except Exception:
            continue
    # fallback: devuelve la columna numérica con menor diferencia si existen columnas numericas
    numeric_cols = []
    for col in posibles:
        try:
            numeric_cols.append((col, float(col)))
        except Exception:
            pass
    if numeric_cols:
        numeric_cols.sort(key=lambda x: abs(x[1] - float(tamano_in)))
        return numeric_cols[0][0]
    return None

def obtener_contenido_agua(asentamiento, tamaño_nominal):
    # Tabla aproximada ACI 211.1 (contenido de agua en kg/m³)
    # Filas = tamaño nominal (in), columnas = asentamiento (pulg)
    tabla = {
        0.375: {1: 207, 2: 207, 3: 228, 4: 228, 5: 243, 6: 243, 7: 243},
        0.5:   {1: 199, 2: 199, 3: 216, 4: 216, 5: 228, 6: 228, 7: 228},
        0.75:  {1: 190, 2: 190, 3: 205, 4: 205, 5: 205, 6: 216, 7: 216},
        1:     {1: 179, 2: 179, 3: 193, 4: 193, 5: 202, 6: 202, 7: 202},
        1.5:   {1: 166, 2: 166, 3: 181, 4: 181, 5: 190, 6: 190, 7: 190},
        2:     {1: 154, 2: 154, 3: 169, 4: 169, 5: 178, 6: 178, 7: 178},
        3:     {1: 130, 2: 130, 3: 145, 4: 145, 5: 160, 6: 160, 7: 160},
        6:     {1: 113, 2: 113, 3: 124, 4: 124, 5: None, 6: None, 7: None}

    }
    # Buscar tamaño más cercano
    tamaño_nominal_cercano = min(tabla.keys(), key=lambda x: abs(x - tamaño_nominal))
    # Buscar asentamiento más cercano
    asentamiento_cercano = min(tabla[tamaño_nominal_cercano].keys(), key=lambda x: abs(x - asentamiento))
    return tabla[tamaño_nominal_cercano][asentamiento_cercano]


def is_number_like(x):
    try:
        float(x)
        return True
    except Exception:
        return False

def interpolar_relacion_agua_cemento(resistencia):
    # Basado en valores típicos ACI (kg/cm² vs relación a/c)
    puntos = [
        (100, 0.70),
        (150, 0.64),
        (200, 0.58),
        (250, 0.52),
        (300, 0.48),
        (350, 0.45),
        (400, 0.42),
        (450, 0.39),
        (500, 0.37),
        (600, 0.35)
    ]
    x, y = zip(*puntos)
    return float(np.interp(resistencia, x, y))

def contenido_agregado_grueso(modulo_finura, tamano_in, df_tab=None):
    """
    Replica:
    = -0,1*C25 + (SI(C16=TABLAS!X16;0,74; SI(C16=TABLAS!Y16;0,83; ... )))
    Implementación:
     - usamos una tabla de valores por tamano
     - retornamos -0.1 * modulo_finura + valor_base
    """
    mapping = {
        0.375: 0.74,
        0.5:   0.83,
        0.75:  0.90,
        1.0:   0.95,
        1.5:   0.99,
        2.0:   1.02,
        3.0:   1.06,
        6.0:   1.11
    }
    base = mapping.get(float(tamano_in), 1.0)
    try:
        return round(-0.1 * float(modulo_finura) + base, 4)
    except Exception:
        return round(-0.1 * float(modulo_finura) + base, 4)

# ---------------------------------------------------------
# SIDEBAR: menu
# ---------------------------------------------------------
st.sidebar.title("Menú Principal")
opcion = st.sidebar.radio("Seleccione una opción:", ["🏗️ Entrada de Datos", "📊 Historial de Cálculos", "📁 Exportar Resultados"])

# ---------------------------------------------------------
# PÁGINA: Entrada de Datos (manteniendo tu formulario)
# ---------------------------------------------------------
if opcion == "🏗️ Entrada de Datos":
    st.subheader("Formulario de Entrada de Parámetros")

    # --- CONDICIONES GENERALES ---
    st.markdown("### Condiciones Generales")
    col1, col2 = st.columns(2)
    with col1:
        tipo_construccion = st.selectbox("Tipo de construcción",
            ["Muros de cimentación reforzados", "Zapatas", "Cimentación Concreto Reforzado",
             "Vigas", "Muros reforzados", "Columnas de construcción", "Pavimentos", "Losas", "Hormigón en masa"])
        condiciones_agresivas = st.selectbox("¿Expuesto a condiciones agresivas?", ["Sí", "No", "Moderado", "Severo"])
        resistencia_kgcm2 = st.number_input("Resistencia requerida a la compresión (Kg/cm²)", min_value=0.0, value=324.0)
    with col2:
        densidad_cemento = st.number_input("Densidad del cemento (g/cm³)", min_value=0.0, value=3.15)
        densidad_cemento_kgm3 = densidad_cemento * 1000
        tipo_cemento = st.selectbox("Tipo de cemento", ["UT", "ART", "RS", "MS", "BL", "Otros"])

    resistencia_mpa = round((resistencia_kgcm2 / 10) * 0.98, 2)
    resistencia_psi = round(resistencia_mpa * 145, 2)

    # --- AGREGADO GRUESO ---
    st.markdown("### Datos del Agregado Grueso")
    col3, col4 = st.columns(2)
    with col3:
        # conservar los mismos valores que tenías: tamano_nominal_in default 0.5
        tamano_nominal_in = st.number_input("Tamaño Máx. Nominal (in)", min_value=0.0, value=0.5)
        masa_unitaria_grueso = st.number_input("Masa unitaria compacta (Kg/m³)", min_value=0.0, value=1667.0)
    with col4:
        densidad_aparente_grueso = st.number_input("Densidad aparente (Kg/m³)", min_value=0.0, value=2610.0)
        absorcion_grueso = st.number_input("Absorción (%)", min_value=0.0, value=2.8)
        humedad_grueso = st.number_input("Humedad natural (%)", min_value=0.0, value=1.7)

    tamano_nominal_mm = round(tamano_nominal_in * 25.4, 2)
    absorcion_grueso_dec = round(absorcion_grueso / 100, 3)
    humedad_grueso_dec = round(humedad_grueso / 100, 3)

    # --- AGREGADO FINO ---
    st.markdown("### Datos del Agregado Fino")
    col5, col6 = st.columns(2)
    with col5:
        modulo_finura = st.number_input("Módulo de finura", min_value=0.0, value=2.6)
        masa_unitaria_fino = st.number_input("Masa unitaria compacta (Kg/m³)", min_value=0.0, value=1770.0)
    with col6:
        densidad_aparente_fino = st.number_input("Densidad aparente (Kg/m³)", min_value=0.0, value=2750.0)
        absorcion_fino = st.number_input("Absorción (%)", min_value=0.0, value=5.7)
        humedad_fino = st.number_input("Humedad natural (%)", min_value=0.0, value=2.5)

    absorcion_fino_dec = round(absorcion_fino / 100, 3)
    humedad_fino_dec = round(humedad_fino / 100, 3)

    # --- CALCULOS ---
    st.markdown("### Tabla de Cálculos")
    col7, col8 = st.columns(2)
    with col7:
        asentamiento_in = st.number_input("Asentamiento (in)", min_value=0.0, value=4.0)
    with col8:
        contenido_aire = st.number_input("Contenido de aire atrapado (%)", min_value=0.0, value=1.0)

    asentamiento_mm = round(asentamiento_in * 25.4, 2)
    contenido_aire_m3 = round(contenido_aire / 100, 4)
    
    st.markdown("### Volumen del espécimen (cilindros)")

    colA, colB, colC = st.columns(3)
    with colA:
        altura = st.number_input("Altura del cilindro (m)", min_value=0.0, value=0.30, format="%.3f")
    with colB:
        diametro = st.number_input("Diámetro del cilindro (m)", min_value=0.0, value=0.15, format="%.3f")
    with colC:
        num_cilindros = st.number_input("Número de cilindros", min_value=1, value=1)

    st.markdown("### Configuración de proporción Cemento / Lodo")

    porcentaje_lodo = st.selectbox(
        "Seleccione porcentaje de LODO (%)",
        [5,10, 15, 20, 25],
        index=0
    )

    porcentaje_cemento_real = 100 - porcentaje_lodo
    # === BUSCAR VALOR UNITARIO DE AGUA (de la TABLAS) ===
    volumen_unitario_agua = None
    if df_tablas is not None:
        try:
            # aquí replicamos la fórmula BUSCARV + COINCIDIR
            valor = obtener_contenido_agua(asentamiento_in, tamano_nominal_in)
            if valor is not None and not np.isnan(valor):
                volumen_unitario_agua = float(valor)
        except Exception as e:
            st.warning(f"⚠️ Error obteniendo contenido de agua desde TABLAS: {e}")

    if volumen_unitario_agua is None:
        volumen_unitario_agua = 216  # fallback
        st.info("ℹ️ No se encontró valor exacto en TABLAS, se usó 216 L/m³ como referencia.")

    # === RELACION AGUA/CEMENTO (interpolar) ===
    relacion_agua_cemento = interpolar_relacion_agua_cemento(resistencia_kgcm2)
    relacion_agua_cemento = round(relacion_agua_cemento, 3)

    # === CONTENIDO AGREGADO GRUESO (fórmula que compartiste) ===
    contenido_agregado_grueso_val = contenido_agregado_grueso(modulo_finura, tamano_nominal_in, df_tablas)
    contenido_agregado_grueso_val = round(contenido_agregado_grueso_val, 4)

    # === RESTO DE CÁLCULOS (igual que tu versión original) ===
    volumen_abs_agua = round(volumen_unitario_agua / 1000, 5)
    relacion_agua_cemento_uso = relacion_agua_cemento if relacion_agua_cemento else 0.516
    factor_cemento = round(volumen_unitario_agua / relacion_agua_cemento_uso, 2) if relacion_agua_cemento_uso != 0 else 0
    vol_abs_cemento = round(factor_cemento / densidad_cemento_kgm3, 5) if densidad_cemento_kgm3 != 0 else 0
    peso_agregado_grueso = round(contenido_agregado_grueso_val * masa_unitaria_grueso, 2)
    vol_abs_agregado_grueso = round(peso_agregado_grueso / densidad_aparente_grueso, 5) if densidad_aparente_grueso else 0
    vol_agregado_fino = round(1 - (volumen_abs_agua + vol_abs_cemento + vol_abs_agregado_grueso + contenido_aire_m3), 5)
    peso_agregado_fino = round(vol_agregado_fino * densidad_aparente_fino, 3)

    # === BOTÓN CALCULAR ===
    if st.button("🧮 Calcular"):
        st.success("✅ Cálculo completado correctamente")

        # Mostrar tablas (manteniendo tu formato HTML)
        # (1) Condiciones Generales
        st.markdown(f"""
        <table class="table-style">
        <tr><th colspan="2" class="section-title">CONDICIONES GENERALES</th></tr>
        <tr><td>Tipo de construcción</td><td class="value-red">{tipo_construccion}</td></tr>
        <tr><td>Expuesto condiciones agresivas?</td><td class="value-red">{condiciones_agresivas}</td></tr>
        <tr><td>f'c (Kg/cm²)</td><td class="value-red">{resistencia_kgcm2}</td></tr>
        <tr><td>f'c (MPa)</td><td>{resistencia_mpa}</td></tr>
        <tr><td>f'c (PSI)</td><td>{resistencia_psi}</td></tr>
        <tr><td>Densidad del cemento (g/cm³)</td><td class="value-red">{densidad_cemento}</td></tr>
        <tr><td>Peso específico (Kg/m³)</td><td>{densidad_cemento_kgm3}</td></tr>
        <tr><td>Tipo de cemento</td><td class="value-red">{tipo_cemento}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        # (2) Agregado Grueso
        st.markdown(f"""
        <table class="table-style">
        <tr><th colspan="2" class="section-title">DATOS DEL AGREGADO GRUESO</th></tr>
        <tr><td>Tamaño Máx. Nominal (in)</td><td>{tamano_nominal_in}</td></tr>
        <tr><td>Tamaño Máx. Nominal (mm)</td><td>{tamano_nominal_mm}</td></tr>
        <tr><td>Masa unitaria compacta (Kg/m³)</td><td>{masa_unitaria_grueso}</td></tr>
        <tr><td>Densidad aparente (Kg/m³)</td><td>{densidad_aparente_grueso}</td></tr>
        <tr><td>Absorción (%)</td><td>{absorcion_grueso}</td></tr>
        <tr><td>Absorción (#)</td><td>{absorcion_grueso_dec}</td></tr>
        <tr><td>Humedad Natural (%)</td><td>{humedad_grueso}</td></tr>
        <tr><td>Humedad Natural (#)</td><td>{humedad_grueso_dec}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        # (3) Agregado Fino
        st.markdown(f"""
        <table class="table-style">
        <tr><th colspan="2" class="section-title">DATOS DEL AGREGADO FINO</th></tr>
        <tr><td>Módulo de finura</td><td>{modulo_finura}</td></tr>
        <tr><td>Masa unitaria compacta (Kg/m³)</td><td>{masa_unitaria_fino}</td></tr>
        <tr><td>Densidad aparente (Kg/m³)</td><td>{densidad_aparente_fino}</td></tr>
        <tr><td>Absorción (%)</td><td>{absorcion_fino}</td></tr>
        <tr><td>Absorción (#)</td><td>{absorcion_fino_dec}</td></tr>
        <tr><td>Humedad Natural (%)</td><td>{humedad_fino}</td></tr>
        <tr><td>Humedad Natural (#)</td><td>{humedad_fino_dec}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        # (4) Tabla de Cálculos
        st.markdown(f"""
        <table class="table-style">
        <tr><th colspan="3" class="section-title">CÁLCULOS</th></tr>
        <tr><td>Asentamiento</td><td>(mm)</td><td>{asentamiento_mm}</td></tr>
        <tr><td></td><td>(in)</td><td>{asentamiento_in}</td></tr>
        <tr><td>Contenido de aire atrapado</td><td>(%)</td><td>{contenido_aire}</td></tr>
        <tr><td></td><td>(m³)</td><td>{contenido_aire_m3}</td></tr>
        <tr><td>Contenido de agua</td><td>Lt/m³ mezcla</td><td>{volumen_unitario_agua}</td></tr>
        <tr><td>Volumen absoluto del agua</td><td>m³/m³ mezcla</td><td>{volumen_abs_agua}</td></tr>
        <tr><td>Relación agua/cemento</td><td>Interpolación</td><td>{relacion_agua_cemento}</td></tr>
        <tr><td>Factor cemento</td><td>Lt/m³ mezcla</td><td>{factor_cemento}</td></tr>
        <tr><td>Volumen absoluto del cemento</td><td>m³/m³ mezcla</td><td>{vol_abs_cemento}</td></tr>
        <tr><td>Contenido agregado grueso</td><td>m³/m³ mezcla</td><td>{contenido_agregado_grueso_val}</td></tr>
        <tr><td>Peso agregado grueso seco</td><td>Kg/m³ mezcla</td><td>{peso_agregado_grueso}</td></tr>
        <tr><td>Volumen abs. agr. grueso seco</td><td>m³/m³ mezcla</td><td>{vol_abs_agregado_grueso}</td></tr>
        <tr><td>Volumen agregado fino</td><td>m³/m³ mezcla</td><td>{vol_agregado_fino}</td></tr>
        <tr><td>Peso agregado fino seco</td><td>Kg/m³ mezcla</td><td>{peso_agregado_fino}</td></tr>
        </table>
        """, unsafe_allow_html=True)
                # ==========================================================
        #  TABLA – AJUSTE POR HUMEDAD (AGREGADO GRUESO)
        # ==========================================================

        humedad_superficial_grueso = round(humedad_grueso - absorcion_grueso, 2)
        aporte_humedad_grueso = round(peso_agregado_grueso * humedad_superficial_grueso / 100, 8)
        peso_humedo_grueso = round(peso_agregado_grueso * (humedad_grueso / 100), 8)
        peso_real_grueso = round(peso_agregado_grueso + peso_humedo_grueso, 8)

        st.markdown(f"""
        <br><br>
        <table class="table-style">
        <tr><th colspan="3" class="section-title">CÁLCULOS AJUSTE POR HUMEDAD - AGREGADO GRUESO</th></tr>

        <tr><td>Humedad Superficial Agr. Grueso</td><td>(%)</td><td>{humedad_superficial_grueso}</td></tr>
        <tr><td>Aporte humedad</td><td>(Lt)</td><td>{aporte_humedad_grueso}</td></tr>
        <tr><td>Peso Húmedo</td><td>(Kg)</td><td>{peso_humedo_grueso}</td></tr>
        <tr><td>Peso Real</td><td>(Kg)</td><td>{peso_real_grueso}</td></tr>

        </table>
        """, unsafe_allow_html=True)


        # ==========================================================
        #  TABLA – AJUSTE POR HUMEDAD (AGREGADO FINO)
        # ==========================================================

        humedad_superficial_fino = round(humedad_fino - absorcion_fino, 3)
        aporte_humedad_fino = round(peso_agregado_fino * humedad_superficial_fino / 100, 8)
        peso_humedo_fino = round(peso_agregado_fino * (humedad_fino / 100), 8)
        peso_real_fino = round(peso_agregado_fino + peso_humedo_fino, 8)

        st.markdown(f"""
        <br><br>
        <table class="table-style">
        <tr><th colspan="3" class="section-title">CÁLCULOS AJUSTE POR HUMEDAD - AGREGADO FINO</th></tr>

        <tr><td>Humedad Superficial Agr. Fino</td><td>(%)</td><td>{humedad_superficial_fino}</td></tr>
        <tr><td>Aporte humedad</td><td>(Lt)</td><td>{aporte_humedad_fino}</td></tr>
        <tr><td>Peso Húmedo</td><td>(Kg)</td><td>{peso_humedo_fino}</td></tr>
        <tr><td>Peso Real</td><td>(Kg)</td><td>{peso_real_fino}</td></tr>

        </table>
        """, unsafe_allow_html=True)


        # ==========================================================
        #  TABLA – AGUA EN EXCESO Y AGUA DE MEZCLADO
        # ==========================================================

        total_agua_exceso = round(aporte_humedad_grueso + aporte_humedad_fino, 8)
        agua_mezclado = round(volumen_unitario_agua - total_agua_exceso, 2)

        st.markdown(f"""
        <br><br>
        <table class="table-style">
        <tr><th colspan="3" class="section-title">AJUSTE FINAL DE AGUA</th></tr>

        <tr><td>Total agua en exceso</td><td>(Lt)</td><td>{total_agua_exceso}</td></tr>
        <tr><td>Agua de mezclado</td><td>(Lt/m³ mezcla)</td><td>{agua_mezclado}</td></tr>

        </table>
        """, unsafe_allow_html=True)

        cemento_kg_m3 = round(factor_cemento, 2)
        agua_kg_m3 = round(agua_mezclado, 2)   # litros ≈ kg
        agregado_fino_kg_m3 = round(peso_real_fino, 3)
        agregado_grueso_kg_m3 = round(peso_real_grueso, 3)

        # Relación material/peso cemento
        rel_cemento = 1.000
        rel_aire = 0.000
        rel_agua = round(agua_kg_m3 / 7, 3) if cemento_kg_m3 else 0
        rel_fin = round(agregado_fino_kg_m3 / cemento_kg_m3, 3) if cemento_kg_m3 else 0
        rel_grueso = round(agregado_grueso_kg_m3 / cemento_kg_m3, 3) if cemento_kg_m3 else 0

        st.markdown(f"""
        <br><br>
        <table class="table-style">
        <tr><th colspan="3" class="section-title">CANTIDAD DE MATERIALES TOTALES PARA 1 m³</th></tr>

        <tr><th>MATERIAL</th><th>Kg/m³</th><th>RELACIÓN<br>(Material / Peso Cemento)</th></tr>

        <tr><td>Cemento</td><td>{cemento_kg_m3}</td><td>{rel_cemento}</td></tr>
        <tr><td>Aire</td><td>0</td><td>{rel_aire}</td></tr>
        <tr><td>Agua</td><td>{agua_kg_m3}</td><td>{rel_agua}</td></tr>
        <tr><td>Agregado Fino</td><td>{agregado_fino_kg_m3}</td><td>{rel_fin}</td></tr>
        <tr><td>Agregado Grueso</td><td>{agregado_grueso_kg_m3}</td><td>{rel_grueso}</td></tr>
        </table>
        """, unsafe_allow_html=True)

        # ==========================================================
        #  CUADRO 2 – VOLUMEN ESPECIMEN
        # ==========================================================

        volumen_cilindro = round(3.1416 * (diametro/2)**2 * altura, 8)
        volumen_total = round(volumen_cilindro * num_cilindros, 8)

        st.markdown(f"""
        <br><br>
        <table class="table-style">
        <tr><th colspan="2" class="section-title">VOLUMEN ESPECIMEN</th></tr>

        <tr><td>ALTURA (m)</td><td>{altura}</td></tr>
        <tr><td>DIÁMETRO (m)</td><td>{diametro}</td></tr>
        <tr><td>VOLUMEN (m³)</td><td>{volumen_cilindro}</td></tr>
        <tr><td>NÚMERO DE CILINDROS</td><td>{num_cilindros}</td></tr>
        <tr><td>VOL. TOTAL CILINDROS (m³)</td><td>{volumen_total}</td></tr>

        </table>
        """, unsafe_allow_html=True)
        # ==========================================================
        #  CALCULO INTERNO – CANTIDAD MATERIALES PARA CILINDROS 6"
        #  (NO SE MUESTRA EN PANTALLA)
        # ==========================================================

        # Kg/m³ obtenidos de la tabla azul:
        cemento_kg_m3 = round(factor_cemento, 2)
        agua_kg_m3 = round(volumen_unitario_agua, 2)              # Agua en L = Kg aprox
        agregado_fino_kg_m3 = round(peso_agregado_fino, 3)
        agregado_grueso_kg_m3 = round(peso_agregado_grueso, 3)

        # === 1. ESPECÍMENES (kg/m³ * volumen_cilindro) ===
        esp_cemento = round(cemento_kg_m3 * volumen_total, 6)
        esp_aire = 0
        esp_agua = round(agua_kg_m3 * volumen_total, 6)
        esp_fino = round(agregado_fino_kg_m3 * volumen_total, 6)
        esp_grueso = round(agregado_grueso_kg_m3 * volumen_total, 6)

        # === 2. DESPERDICIO (5%) ===
        desp_cemento = round(esp_cemento * 0.05, 6)
        desp_aire = 0
        desp_agua = round(esp_agua * 0.05, 6)
        desp_fino = round(esp_fino * 0.05, 6)
        desp_grueso = round(esp_grueso * 0.05, 6)

        # === 3. CANTIDAD TOTAL = ESPECIMENES + DESPERDICIO ===
        tot_cemento = round(esp_cemento + desp_cemento, 4)
        tot_aire = 0
        tot_agua = round(esp_agua + desp_agua, 4)
        tot_fino = round(esp_fino + desp_fino, 4)
        tot_grueso = round(esp_grueso + desp_grueso, 4)

        # ==========================================================
        #  CUADRO 3 – CANTIDADES PARA ENSAYO (por volumen total)
        # ==========================================================
        cemento_cant = round(tot_cemento * (porcentaje_cemento_real / 100), 4)
        lodo_cant = round(tot_cemento * (porcentaje_lodo / 100), 4)
        arena_cant = tot_fino
        grava_cant = tot_grueso
        agua_l_cant = tot_agua

        st.markdown(f"""
        <br><br>
        <table class="table-style">
        <tr><th colspan="2" class="section-title">CANTIDADES PARA ENSAYO</th></tr>

        <tr><td>CEMENTO (Kg)</td><td>{cemento_cant}</td></tr>
        <tr><td>LODO (Kg)</td><td>{lodo_cant}</td></tr>
        <tr><td>ARENA (Kg)</td><td>{arena_cant}</td></tr>
        <tr><td>GRAVA (Kg)</td><td>{grava_cant}</td></tr>
        <tr><td>AGUA (L)</td><td>{agua_l_cant}</td></tr>

        </table>
        """, unsafe_allow_html=True)

        # === GUARDAR EN BASE DE DATOS (CRUD: CREATE) ===
        registro = {
            "tipo_construccion": tipo_construccion,
            "condiciones_agresivas": condiciones_agresivas,
            "resistencia_kgcm2": resistencia_kgcm2,
            "densidad_cemento": densidad_cemento,
            "tipo_cemento": tipo_cemento,
            "tamano_nominal_in": tamano_nominal_in,
            "tamano_nominal_mm": tamano_nominal_mm,
            "modulo_finura": modulo_finura,
            "masa_unitaria_grueso": masa_unitaria_grueso,
            "masa_unitaria_fino": masa_unitaria_fino,
            "contenido_aire": contenido_aire,
            "asentamiento": asentamiento_in,
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        try:
            database.insertar_calculo(registro)
            st.info("Registro guardado en historial")
        except Exception as e:
            st.warning(f"No se pudo guardar en DB: {e}")

        # === OPCIONES DE EXPORTACIÓN (excel y pdf) usando data_io.py ===
        resultados_resumen = {
            "Contenido agua (Lt/m3)": volumen_unitario_agua,
            "Relación agua/cemento": relacion_agua_cemento,
            "Contenido agregado grueso (m3/m3)": contenido_agregado_grueso_val,
            "Peso agregado fino (Kg/m3)": peso_agregado_fino,
            "Peso agregado grueso (Kg/m3)": peso_agregado_grueso,
            "Factor cemento (Lt/m3)": factor_cemento
        }

        # Exportar a Excel: genera archivo y ofrece descarga
        try:
            ruta_excel = data_io.export_to_excel(resultados_resumen, base_name="resultado_aci2025")
            with open(ruta_excel, "rb") as f:
                data = f.read()
            st.download_button("💾 Descargar Excel (resultado)", data=data, file_name=os.path.basename(ruta_excel), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            st.warning(f"No se pudo exportar a Excel: {e}")

        # Exportar a PDF
        try:
            ruta_pdf = data_io.export_to_pdf(registro, resultados_resumen)
            with open(ruta_pdf, "rb") as f:
                data_pdf = f.read()
            st.download_button("🧾 Descargar PDF (resultado)", data=data_pdf, file_name=os.path.basename(ruta_pdf), mime="application/pdf")
        except Exception as e:
            st.warning(f"No se pudo exportar a PDF: {e}")

# ---------------------------------------------------------
# PÁGINA: Historial de Cálculos (CRUD: READ + DELETE)
# ---------------------------------------------------------
elif opcion == "📊 Historial de Cálculos":
    st.subheader("Historial de Cálculos")

    filas = database.obtener_calculos()
    if not filas:
        st.info("No hay registros guardados.")
    else:
        # convertir a DataFrame para mostrar
        df_hist = pd.DataFrame(filas, columns=["id","tipo_construccion","condiciones_agresivas","resistencia_kgcm2","densidad_cemento","tipo_cemento","tamano_nominal_in","tamano_nominal_mm","modulo_finura","masa_unitaria_grueso","masa_unitaria_fino","contenido_aire","asentamiento","fecha"])
        st.dataframe(df_hist)

        # permitir eliminar registros (CRUD: DELETE)
        st.markdown("### Eliminar registro")
        with st.form("form_eliminar"):
            id_eliminar = st.number_input("Id del registro a eliminar", min_value=1, value=int(df_hist.iloc[0]["id"]))
            submitted = st.form_submit_button("Eliminar")
            if submitted:
                try:
                    database.eliminar_calculo(int(id_eliminar))
                    st.success(f"Registro {id_eliminar} eliminado")
                except Exception as e:
                    st.error(f"No se pudo eliminar: {e}")

# ---------------------------------------------------------
# PÁGINA: Exportar Resultados (opcional: genera reportes desde historial)
# ---------------------------------------------------------
elif opcion == "📁 Exportar Resultados":
    st.subheader("Exportar resultados desde historial")

    filas = database.obtener_calculos()
    if not filas:
        st.info("No hay registros para exportar.")
    else:
        df_hist = pd.DataFrame(filas, columns=["id","tipo_construccion","condiciones_agresivas","resistencia_kgcm2","densidad_cemento","tipo_cemento","tamano_nominal_in","tamano_nominal_mm","modulo_finura","masa_unitaria_grueso","masa_unitaria_fino","contenido_aire","asentamiento","fecha"])
        st.dataframe(df_hist)

        st.markdown("### Exportar todo el historial a Excel / PDF")
        if st.button("Exportar historial a Excel"):
            try:
                ruta = data_io.export_to_excel(df_hist, base_name="historial_aci2025")
                with open(ruta, "rb") as f:
                    data = f.read()
                st.download_button("Descargar historial (Excel)", data=data, file_name=os.path.basename(ruta), mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.error(f"No se pudo exportar historial a Excel: {e}")

        if st.button("Exportar historial a PDF (resumen)"):
            try:
                # crear un resumen sencillo para pdf (primer registro)
                primera_fila = df_hist.iloc[0].to_dict()
                resumen = {k: primera_fila[k] for k in primera_fila if k not in ['id']}
                ruta_pdf = data_io.export_to_pdf(resumen, {"Nota": "Exportado historial (ejemplo)"})
                with open(ruta_pdf, "rb") as f:
                    data_pdf = f.read()
                st.download_button("Descargar historial (PDF)", data=data_pdf, file_name=os.path.basename(ruta_pdf), mime="application/pdf")
            except Exception as e:
                st.error(f"No se pudo exportar historial a PDF: {e}")
