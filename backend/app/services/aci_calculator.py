"""
Lógica de diseño de mezcla ACI 2025 (ACI 211.1), portada 1:1 desde el
prototipo original (app_v3.py / Streamlit) para que el backend produzca
exactamente los mismos resultados.
"""
import math

from app.schemas.aci import DisenoMezclaInput

_TABLA_CONTENIDO_AGUA = {
    0.375: {1: 207, 2: 207, 3: 228, 4: 228, 5: 243, 6: 243, 7: 243},
    0.5: {1: 199, 2: 199, 3: 216, 4: 216, 5: 228, 6: 228, 7: 228},
    0.75: {1: 190, 2: 190, 3: 205, 4: 205, 5: 205, 6: 216, 7: 216},
    1: {1: 179, 2: 179, 3: 193, 4: 193, 5: 202, 6: 202, 7: 202},
    1.5: {1: 166, 2: 166, 3: 181, 4: 181, 5: 190, 6: 190, 7: 190},
    2: {1: 154, 2: 154, 3: 169, 4: 169, 5: 178, 6: 178, 7: 178},
    3: {1: 130, 2: 130, 3: 145, 4: 145, 5: 160, 6: 160, 7: 160},
    6: {1: 113, 2: 113, 3: 124, 4: 124, 5: None, 6: None, 7: None},
}

_MAPEO_AGREGADO_GRUESO = {
    0.375: 0.74,
    0.5: 0.83,
    0.75: 0.90,
    1.0: 0.95,
    1.5: 0.99,
    2.0: 1.02,
    3.0: 1.06,
    6.0: 1.11,
}

_PUNTOS_RELACION_AC = [
    (100, 0.70), (150, 0.64), (200, 0.58), (250, 0.52), (300, 0.48),
    (350, 0.45), (400, 0.42), (450, 0.39), (500, 0.37), (600, 0.35),
]


def _obtener_contenido_agua(asentamiento_in: float, tamano_nominal_in: float) -> float:
    tamano_cercano = min(_TABLA_CONTENIDO_AGUA.keys(), key=lambda x: abs(x - tamano_nominal_in))
    fila = _TABLA_CONTENIDO_AGUA[tamano_cercano]
    valores_validos = {k: v for k, v in fila.items() if v is not None}
    asentamiento_cercano = min(valores_validos.keys(), key=lambda x: abs(x - asentamiento_in))
    return valores_validos[asentamiento_cercano]


def _interpolar_relacion_agua_cemento(resistencia_kgcm2: float) -> float:
    xs, ys = zip(*_PUNTOS_RELACION_AC)
    if resistencia_kgcm2 <= xs[0]:
        return round(ys[0], 3)
    if resistencia_kgcm2 >= xs[-1]:
        return round(ys[-1], 3)
    for i in range(len(xs) - 1):
        if xs[i] <= resistencia_kgcm2 <= xs[i + 1]:
            frac = (resistencia_kgcm2 - xs[i]) / (xs[i + 1] - xs[i])
            return round(ys[i] + frac * (ys[i + 1] - ys[i]), 3)
    return round(ys[-1], 3)


def _contenido_agregado_grueso(modulo_finura: float, tamano_nominal_in: float) -> float:
    base = _MAPEO_AGREGADO_GRUESO.get(round(tamano_nominal_in, 3))
    if base is None:
        tamano_cercano = min(_MAPEO_AGREGADO_GRUESO.keys(), key=lambda x: abs(x - tamano_nominal_in))
        base = _MAPEO_AGREGADO_GRUESO[tamano_cercano]
    return round(-0.1 * modulo_finura + base, 4)


def calcular_diseno(data: DisenoMezclaInput) -> dict:
    resistencia_mpa = round((data.resistencia_kgcm2 / 10) * 0.98, 2)
    resistencia_psi = round(resistencia_mpa * 145, 2)

    tamano_nominal_mm = round(data.tamano_nominal_in * 25.4, 2)
    densidad_cemento_kgm3 = data.densidad_cemento * 1000
    contenido_aire_m3 = round(data.contenido_aire / 100, 4)

    volumen_unitario_agua = _obtener_contenido_agua(data.asentamiento_in, data.tamano_nominal_in) or 216
    relacion_agua_cemento = _interpolar_relacion_agua_cemento(data.resistencia_kgcm2)
    contenido_agregado_grueso_val = _contenido_agregado_grueso(data.modulo_finura, data.tamano_nominal_in)

    volumen_abs_agua = round(volumen_unitario_agua / 1000, 5)
    relacion_agua_cemento_uso = relacion_agua_cemento or 0.516
    factor_cemento = round(volumen_unitario_agua / relacion_agua_cemento_uso, 2)
    vol_abs_cemento = round(factor_cemento / densidad_cemento_kgm3, 5)
    peso_agregado_grueso = round(contenido_agregado_grueso_val * data.masa_unitaria_grueso, 2)
    vol_abs_agregado_grueso = round(peso_agregado_grueso / data.densidad_aparente_grueso, 5)
    vol_agregado_fino = round(
        1 - (volumen_abs_agua + vol_abs_cemento + vol_abs_agregado_grueso + contenido_aire_m3), 5
    )
    peso_agregado_fino = round(vol_agregado_fino * data.densidad_aparente_fino, 3)

    # Ajuste por humedad - agregado grueso
    humedad_superficial_grueso = round(data.humedad_grueso - data.absorcion_grueso, 2)
    aporte_humedad_grueso = round(peso_agregado_grueso * humedad_superficial_grueso / 100, 8)
    peso_humedo_grueso = round(peso_agregado_grueso * (data.humedad_grueso / 100), 8)
    peso_real_grueso = round(peso_agregado_grueso + peso_humedo_grueso, 8)

    # Ajuste por humedad - agregado fino
    humedad_superficial_fino = round(data.humedad_fino - data.absorcion_fino, 3)
    aporte_humedad_fino = round(peso_agregado_fino * humedad_superficial_fino / 100, 8)
    peso_humedo_fino = round(peso_agregado_fino * (data.humedad_fino / 100), 8)
    peso_real_fino = round(peso_agregado_fino + peso_humedo_fino, 8)

    total_agua_exceso = round(aporte_humedad_grueso + aporte_humedad_fino, 8)
    agua_mezclado = round(volumen_unitario_agua - total_agua_exceso, 2)

    # Volumen del espécimen
    volumen_cilindro = round(math.pi * (data.diametro_cilindro / 2) ** 2 * data.altura_cilindro, 8)
    volumen_total = round(volumen_cilindro * data.num_cilindros, 8)

    # Cálculo interno (no se muestra en pantalla en el original): cantidades
    # para los cilindros de ensayo, a partir de los pesos secos y el agua
    # de diseño (sin ajuste de humedad) + 5% de desperdicio.
    cemento_kg_m3 = round(factor_cemento, 2)
    agua_kg_m3 = round(volumen_unitario_agua, 2)
    agregado_fino_kg_m3 = round(peso_agregado_fino, 3)
    agregado_grueso_kg_m3 = round(peso_agregado_grueso, 3)

    esp_cemento = round(cemento_kg_m3 * volumen_total, 6)
    esp_agua = round(agua_kg_m3 * volumen_total, 6)
    esp_fino = round(agregado_fino_kg_m3 * volumen_total, 6)
    esp_grueso = round(agregado_grueso_kg_m3 * volumen_total, 6)

    desp_cemento = round(esp_cemento * 0.05, 6)
    desp_agua = round(esp_agua * 0.05, 6)
    desp_fino = round(esp_fino * 0.05, 6)
    desp_grueso = round(esp_grueso * 0.05, 6)

    tot_cemento = round(esp_cemento + desp_cemento, 4)
    tot_agua = round(esp_agua + desp_agua, 4)
    tot_fino = round(esp_fino + desp_fino, 4)
    tot_grueso = round(esp_grueso + desp_grueso, 4)

    porcentaje_cemento_real = 100 - data.porcentaje_lodo
    cemento_cant = round(tot_cemento * (porcentaje_cemento_real / 100), 4)
    lodo_cant = round(tot_cemento * (data.porcentaje_lodo / 100), 4)

    return {
        "resistencia_teorica_kgcm2": data.resistencia_kgcm2,
        "resistencia_teorica_mpa": resistencia_mpa,
        "resistencia_teorica_psi": resistencia_psi,
        "tamano_nominal_mm": tamano_nominal_mm,
        "volumen_unitario_agua": volumen_unitario_agua,
        "relacion_agua_cemento": relacion_agua_cemento,
        "contenido_agregado_grueso": contenido_agregado_grueso_val,
        "factor_cemento": factor_cemento,
        "peso_agregado_grueso": peso_agregado_grueso,
        "peso_agregado_fino": peso_agregado_fino,
        "peso_real_grueso": peso_real_grueso,
        "peso_real_fino": peso_real_fino,
        "agua_mezclado": agua_mezclado,
        "cemento_cant": cemento_cant,
        "lodo_cant": lodo_cant,
        "arena_cant": tot_fino,
        "grava_cant": tot_grueso,
        "agua_cant": tot_agua,
    }
