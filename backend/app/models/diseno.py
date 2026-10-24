from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class DisenoMezcla(Base):
    __tablename__ = "disenos_mezcla"

    id = Column(Integer, primary_key=True, index=True)
    usuario_id = Column(Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False)
    folio = Column(String(64), unique=True, nullable=False, index=True)

    # Condiciones generales
    tipo_construccion = Column(String(100))
    condiciones_agresivas = Column(String(50))
    resistencia_teorica_kgcm2 = Column(Float, nullable=False)
    resistencia_teorica_mpa = Column(Float, nullable=False)
    resistencia_teorica_psi = Column(Float, nullable=False)
    densidad_cemento = Column(Float)
    tipo_cemento = Column(String(20))

    # Agregado grueso
    tamano_nominal_in = Column(Float)
    tamano_nominal_mm = Column(Float)
    masa_unitaria_grueso = Column(Float)
    densidad_aparente_grueso = Column(Float)
    absorcion_grueso = Column(Float)
    humedad_grueso = Column(Float)

    # Agregado fino
    modulo_finura = Column(Float)
    masa_unitaria_fino = Column(Float)
    densidad_aparente_fino = Column(Float)
    absorcion_fino = Column(Float)
    humedad_fino = Column(Float)

    # Mezcla / espécimen
    asentamiento_in = Column(Float)
    contenido_aire = Column(Float)
    altura_cilindro = Column(Float)
    diametro_cilindro = Column(Float)
    num_cilindros = Column(Integer)
    porcentaje_lodo = Column(Float)

    # Resultados calculados (ACI 211.1)
    volumen_unitario_agua = Column(Float)
    relacion_agua_cemento = Column(Float)
    contenido_agregado_grueso = Column(Float)
    factor_cemento = Column(Float)
    peso_agregado_grueso = Column(Float)
    peso_agregado_fino = Column(Float)
    peso_real_grueso = Column(Float)
    peso_real_fino = Column(Float)
    agua_mezclado = Column(Float)

    # Cantidades para ensayo
    cemento_cant = Column(Float)
    lodo_cant = Column(Float)
    arena_cant = Column(Float)
    grava_cant = Column(Float)
    agua_cant = Column(Float)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    usuario = relationship("Usuario", back_populates="disenos")
    predicciones = relationship("Prediccion", back_populates="diseno", cascade="all, delete-orphan")

    @property
    def autor_username(self) -> str | None:
        return self.usuario.username if self.usuario else None

    @property
    def autor_nombre(self) -> str | None:
        return self.usuario.nombre_completo if self.usuario else None
