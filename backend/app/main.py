from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.routers import aci, auth, historial, prediccion, usuarios

app = FastAPI(
    title="Plataforma ACI 2025 + Predicción IA",
    description=(
        "Backend unificado: calculadora de diseño de mezcla ACI 2025 y "
        "predicción de resistencia del concreto por edad de curado, "
        "entrenada con el UCI Concrete Compressive Strength Data Set."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(aci.router)
app.include_router(prediccion.router)
app.include_router(historial.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
