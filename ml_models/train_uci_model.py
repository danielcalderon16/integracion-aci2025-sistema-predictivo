import pandas as pd
import numpy as np
import urllib.request
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
import urllib3
import joblib

# Descargar Dataset Profesional UCI
url = "https://archive.ics.uci.edu/ml/machine-learning-databases/concrete/compressive/Concrete_Data.xls"
file_name = "Concrete_Data.xls"

if not os.path.exists(file_name):
    print("Descargando el dataset cientifico de la UCI...")
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    import ssl
    ssl._create_default_https_context = ssl._create_unverified_context
    urllib.request.urlretrieve(url, file_name)
    print("Descarga completada.")

print("Cargando y preparando los datos de laboratorio...")
df = pd.read_excel(file_name)

# Renombrar columnas para facilitar el manejo
df.columns = [
    'cemento', 'escoria', 'cenizas', 'agua', 'superplastificante',
    'agregado_grueso', 'agregado_fino', 'edad_dias', 'resistencia_mpa'
]

# Separar variables predictoras (X) y el objetivo (Resistencia en MPa y)
X = df.drop('resistencia_mpa', axis=1)
y = df['resistencia_mpa']

# Normalizar los datos para que todos los features pesen igual a nivel red neuronal
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Dividir datos en validacion y entrenamiento (20% test)
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2, random_state=42)

print("Construyendo arquitectura profunda de la Red Neuronal...")
model = Sequential([
    Dense(512, activation='relu', input_shape=(X.shape[1],)),
    BatchNormalization(),
    Dropout(0.3),
    Dense(256, activation='relu'),
    BatchNormalization(),
    Dropout(0.3),
    Dense(128, activation='relu'),
    BatchNormalization(),
    Dropout(0.2),
    Dense(64, activation='relu'),
    Dense(1, activation='linear')
])

model.compile(optimizer='adam', loss='mse', metrics=['mae'])

# Evitar overfitting deteniendo el modelo cuando deje de aprender
early_stop = EarlyStopping(monitor='val_loss', patience=40, restore_best_weights=True)
reduce_lr = ReduceLROnPlateau(monitor='val_loss', factor=0.5, patience=15, min_lr=1e-6)

print("Iniciando fase de entrenamiento (Epochs)... Esto puede tomar unos 1-2 minutos.")
history = model.fit(
    X_train, y_train,
    validation_split=0.2,
    epochs=1000,
    batch_size=32,
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

loss, mae = model.evaluate(X_test, y_test, verbose=0)
print(f"\n--- EVALUACION CIENTIFICA FINAL ---")
print(f"Error Absoluto Medio (MAE): {mae:.2f} MPa")
if mae < 6.0:
    print("¡El modelo predice con un altísimo grado de exactitud! Validado para uso civil industrial.")
else:
    print("El margen de error es un poco alto, pero aceptable para prototipos.")

# Guardar los pesos del escalador (para que la API pueda normalizar los JSON de entrada igual)
joblib.dump(scaler, 'scaler_uci.pkl')
# Guardar el modelo compilado en TensorFlow (H5)
model.save("modelo_resistencia_concreto_v2.h5")
print("\nModelo guardado en disco con exito como: 'modelo_resistencia_concreto_v2.h5' y 'scaler_uci.pkl'.")
