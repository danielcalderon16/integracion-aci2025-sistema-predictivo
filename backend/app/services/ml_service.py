"""
Servicio de inferencia del modelo predictivo de resistencia del concreto,
entrenado con el "UCI Concrete Compressive Strength Data Set" (1030
ensayos reales de laboratorio). Ver ml_models/train_uci_model.py.

Orden de features de entrenamiento (fijo, no reordenar):
cemento, escoria, cenizas, agua, superplastificante, agregado_grueso,
agregado_fino, edad_dias -> resistencia_mpa

Las redes neuronales extrapolan de forma poco confiable fuera del rango de
valores con el que fueron entrenadas. Para evitar devolver predicciones
físicamente inconsistentes, cada variable de entrada se acota (clip) al
rango observado en el dataset de entrenamiento antes de escalar/predecir,
y se informa si alguna variable tuvo que ajustarse (extrapolación).
"""
import os

import joblib
import pandas as pd
import tensorflow as tf

_ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "..", "ml_artifacts")
MODEL_PATH = os.path.join(_ARTIFACTS_DIR, "modelo_resistencia_concreto_v2.h5")
SCALER_PATH = os.path.join(_ARTIFACTS_DIR, "scaler_uci.pkl")

FEATURE_ORDER = [
    "cemento", "escoria", "cenizas", "agua", "superplastificante",
    "agregado_grueso", "agregado_fino", "edad_dias",
]

# Rango observado en el UCI Concrete Compressive Strength Data Set (1030
# ensayos). Calculado con pandas.DataFrame.describe() sobre Concrete_Data.xls.
FEATURE_RANGES = {
    "cemento": (102.0, 540.0),
    "escoria": (0.0, 359.4),
    "cenizas": (0.0, 200.1),
    "agua": (121.75, 247.0),
    "superplastificante": (0.0, 32.2),
    "agregado_grueso": (801.0, 1145.0),
    "agregado_fino": (594.0, 992.6),
    "edad_dias": (1.0, 365.0),
}

_model = None
_scaler = None


def _get_model():
    global _model
    if _model is None:
        _model = tf.keras.models.load_model(MODEL_PATH, compile=False)
    return _model


def _get_scaler():
    global _scaler
    if _scaler is None:
        _scaler = joblib.load(SCALER_PATH)
    return _scaler


def predecir_resistencia(
    cemento_kgm3: float,
    agua_kgm3: float,
    agregado_grueso_kgm3: float,
    agregado_fino_kgm3: float,
    edad_dias: int,
    escoria: float = 0.0,
    cenizas: float = 0.0,
    superplastificante: float = 0.0,
) -> dict:
    valores = {
        "cemento": float(cemento_kgm3),
        "escoria": float(escoria),
        "cenizas": float(cenizas),
        "agua": float(agua_kgm3),
        "superplastificante": float(superplastificante),
        "agregado_grueso": float(agregado_grueso_kgm3),
        "agregado_fino": float(agregado_fino_kgm3),
        "edad_dias": float(edad_dias),
    }

    variables_ajustadas = []
    for nombre, valor in valores.items():
        minimo, maximo = FEATURE_RANGES[nombre]
        if valor < minimo or valor > maximo:
            variables_ajustadas.append(nombre)
            valores[nombre] = min(max(valor, minimo), maximo)

    features_df = pd.DataFrame([[valores[c] for c in FEATURE_ORDER]], columns=FEATURE_ORDER)
    features_scaled = _get_scaler().transform(features_df)
    prediccion = _get_model().predict(features_scaled, verbose=0)[0][0]

    return {
        "resistencia_mpa": round(float(prediccion), 2),
        "extrapolado": len(variables_ajustadas) > 0,
        "variables_ajustadas": variables_ajustadas,
    }
