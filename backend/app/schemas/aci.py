from datetime import datetime

from pydantic import BaseModel, Field


class DisenoMezclaInput(BaseModel):
    # Condiciones generales
    tipo_construccion: str
    condiciones_agresivas: str
    resistencia_kgcm2: float = Field(gt=0)
    densidad_cemento: float = Field(gt=0, description="g/cm3")
    tipo_cemento: str

    # Agregado grueso
    tamano_nominal_in: float = Field(gt=0)
    masa_unitaria_grueso: float = Field(gt=0)
    densidad_aparente_grueso: float = Field(gt=0)
    absorcion_grueso: float = Field(ge=0)
    humedad_grueso: float = Field(ge=0)

    # Agregado fino
    modulo_finura: float = Field(gt=0)
    masa_unitaria_fino: float = Field(gt=0)
    densidad_aparente_fino: float = Field(gt=0)
    absorcion_fino: float = Field(ge=0)
    humedad_fino: float = Field(ge=0)

    # Mezcla
    asentamiento_in: float = Field(gt=0)
    contenido_aire: float = Field(ge=0)

    # Espécimen
    altura_cilindro: float = Field(gt=0, default=0.30)
    diametro_cilindro: float = Field(gt=0, default=0.15)
    num_cilindros: int = Field(ge=1, default=1)

    # Proporción cemento / lodo
    porcentaje_lodo: float = Field(ge=0, le=100, default=5)


class DisenoMezclaOut(BaseModel):
    id: int
    folio: str
    created_at: datetime
    usuario_id: int
    autor_username: str | None = None
    autor_nombre: str | None = None
    tipo_construccion: str
    condiciones_agresivas: str
    resistencia_teorica_kgcm2: float
    resistencia_teorica_mpa: float
    resistencia_teorica_psi: float
    densidad_cemento: float
    tipo_cemento: str

    tamano_nominal_in: float
    tamano_nominal_mm: float
    masa_unitaria_grueso: float
    densidad_aparente_grueso: float
    absorcion_grueso: float
    humedad_grueso: float

    modulo_finura: float
    masa_unitaria_fino: float
    densidad_aparente_fino: float
    absorcion_fino: float
    humedad_fino: float

    asentamiento_in: float
    contenido_aire: float
    altura_cilindro: float
    diametro_cilindro: float
    num_cilindros: int
    porcentaje_lodo: float

    volumen_unitario_agua: float
    relacion_agua_cemento: float
    contenido_agregado_grueso: float
    factor_cemento: float
    peso_agregado_grueso: float
    peso_agregado_fino: float
    peso_real_grueso: float
    peso_real_fino: float
    agua_mezclado: float

    cemento_cant: float
    lodo_cant: float
    arena_cant: float
    grava_cant: float
    agua_cant: float

    class Config:
        from_attributes = True
