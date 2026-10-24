# Integración de una Herramienta de Cálculo Normativo ACI 2025 y un Sistema de Predicción de Concreto en una Plataforma Web

Trabajo de grado — Ingeniería de Software, Universidad de Santander (UDES).

Plataforma web que integra, mediante una API REST, una calculadora de diseño de mezclas de
concreto basada en la norma **ACI 2025** con un sistema de **predicción de resistencia del
concreto por Inteligencia Artificial**. El diseño calculado alimenta automáticamente al modelo
predictivo, eliminando la transferencia manual de datos entre ambas herramientas.

## Arquitectura

```
┌──────────────┐      REST (JSON)      ┌──────────────┐      SQL      ┌──────────────┐
│   Frontend   │ ───────────────────▶ │   Backend    │ ───────────▶ │  PostgreSQL  │
│  Next.js 16  │ ◀─────────────────── │   FastAPI    │ ◀─────────── │              │
└──────────────┘                       └──────┬───────┘               └──────────────┘
                                               │
                                               ▼
                                     Modelo de IA (TensorFlow/Keras)
                                     entrenado con el UCI Concrete
                                     Compressive Strength Data Set
```

- **Backend** (`/backend`): API en FastAPI. Calcula el diseño de mezcla (ACI 211.1), ejecuta la
  inferencia del modelo predictivo, gestiona usuarios/autenticación y el historial de diseños.
- **Frontend** (`/frontend`): aplicación Next.js (App Router) que consume la API — calculadora,
  historial, panel de administración de usuarios y login con roles (estudiante/profesor).
- **Base de datos**: PostgreSQL, accedida vía SQLAlchemy, con migraciones versionadas en Alembic.
- **Modelo de IA** (`/ml_models`): red neuronal entrenada con el *Concrete Compressive Strength
  Data Set* (Yeh, 1998) — 1030 ensayos reales de laboratorio. El script de entrenamiento está en
  `ml_models/train_uci_model.py`; los artefactos entrenados (`.h5` y `.pkl`) se copian a
  `backend/app/ml_artifacts/` para que el backend los sirva.

## Mecanismo de integración

1. El usuario calcula un diseño de mezcla en la calculadora (`POST /aci/calcular`). El backend
   aplica la dosificación ACI 211.1 y guarda el resultado con un folio único.
2. Al pedir la predicción de resistencia (`POST /prediccion`), el frontend envía únicamente el
   identificador del diseño. El backend recupera el factor cemento, el agua de mezclado y los
   pesos de agregados ya calculados, y los usa directamente como entrada del modelo predictivo —
   sin que el usuario vuelva a escribir ningún valor.
3. El modelo acota automáticamente las variables fuera del rango con el que fue entrenado (ver
   `backend/app/services/ml_service.py`) y marca esas predicciones como `extrapolado: true`, para
   que quede trazable cuándo un resultado tiene menor confiabilidad.

## Cómo correrlo localmente

### Con Docker (recomendado)

```bash
cp .env.example .env   # ajusta las variables si lo necesitas
docker compose up --build
```

- Frontend: http://localhost:3000
- Backend / documentación interactiva de la API (Swagger): http://localhost:8000/docs
- PostgreSQL: localhost:5432

### Sin Docker (desarrollo)

**Backend**
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

**Frontend**
```bash
cd frontend
npm install
npm run dev
```

Variables de entorno relevantes están documentadas en `.env.example`.

## Estructura del backend

```
backend/app/
├── main.py           # Punto de entrada de FastAPI, registro de routers
├── core/              # Configuración, conexión a BD, seguridad (JWT, hashing)
├── models/            # Entidades SQLAlchemy: Usuario, DisenoMezcla, Prediccion
├── schemas/           # Esquemas Pydantic de entrada/salida (validación)
├── routers/           # Endpoints HTTP: auth, usuarios, aci, prediccion, historial
├── services/           # Lógica de negocio: cálculo ACI 211.1, inferencia del modelo, reportes
└── ml_artifacts/       # Modelo entrenado (.h5) y escalador (.pkl) que sirve el backend
```

La documentación completa y probada de cada endpoint está disponible en `/docs` (Swagger UI) una
vez el backend está corriendo.

## Migraciones de base de datos

```bash
cd backend
alembic revision -m "descripcion"   # crear una nueva migración
alembic upgrade head                # aplicar migraciones pendientes
```

## Modelo de Inteligencia Artificial

Entrenado con el *Concrete Compressive Strength Data Set* (Yeh, 1998), alcanzando un Error
Absoluto Medio (MAE) de 3.92 MPa en el conjunto de prueba. Para reentrenarlo:

```bash
cd ml_models
python train_uci_model.py
# copiar los artefactos generados a backend/app/ml_artifacts/
```

## Contexto académico

Este repositorio corresponde al desarrollo del trabajo de grado *"Integración de una herramienta
de cálculo normativo ACI 2025 y un sistema de predicción de concreto en una plataforma web"*
(Universidad de Santander, Ingeniería de Software). El sistema predictivo original fue
desarrollado por el compañero Daniel Romero Moreno (*Liquid Strength Sensor*, trabajo de grado
2024); este proyecto lo analiza, lo integra automáticamente con la calculadora ACI 2025 y
reconstruye su componente de IA sobre un dataset científico validado.
