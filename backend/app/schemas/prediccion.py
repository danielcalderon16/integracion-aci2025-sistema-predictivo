from pydantic import BaseModel, Field


class PrediccionInput(BaseModel):
    diseno_id: int
    edades_dias: list[int] = Field(default=[3, 7, 14, 28], min_length=1, max_length=12)
    escoria: float = Field(default=0, ge=0)
    cenizas: float = Field(default=0, ge=0)
    superplastificante: float = Field(default=0, ge=0)


class PrediccionOut(BaseModel):
    id: int
    edad_dias: int
    escoria: float
    cenizas: float
    superplastificante: float
    resistencia_predicha_mpa: float
    extrapolado: bool

    class Config:
        from_attributes = True
