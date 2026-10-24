from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Prediccion(Base):
    """
    Una estimación del modelo de IA para una edad de curado, generada a
    partir de un DisenoMezcla ya calculado (ver routers/prediccion.py).
    """

    __tablename__ = "predicciones"

    id = Column(Integer, primary_key=True, index=True)
    diseno_id = Column(Integer, ForeignKey("disenos_mezcla.id", ondelete="CASCADE"), nullable=False)

    escoria = Column(Float, default=0, nullable=False)
    cenizas = Column(Float, default=0, nullable=False)
    superplastificante = Column(Float, default=0, nullable=False)
    edad_dias = Column(Integer, nullable=False)
    resistencia_predicha_mpa = Column(Float, nullable=False)
    # True si alguna variable de entrada tuvo que acotarse al rango de
    # entrenamiento del modelo (ver ml_service.FEATURE_RANGES); la predicción
    # es menos confiable cuando esto ocurre.
    extrapolado = Column(Boolean, default=False, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    diseno = relationship("DisenoMezcla", back_populates="predicciones")
