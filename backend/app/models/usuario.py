from sqlalchemy import Boolean, Column, DateTime, Integer, String, func
from sqlalchemy.orm import relationship

from app.core.database import Base


class Usuario(Base):
    """
    Cuenta de la plataforma. El rol ("estudiante" o "profesor") controla qué
    tanto historial puede ver cada quien (deps/historial.py): un estudiante
    solo ve sus propios diseños, un profesor ve los de todos. `codigo` y
    `nombre_completo` son los datos que se piden, junto al usuario, para la
    recuperación de contraseña sin correo (ver routers/auth.py).
    """

    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    nombre_completo = Column(String(150), nullable=False)
    codigo = Column(String(30), unique=True, nullable=False, index=True)
    rol = Column(String(20), nullable=False, default="estudiante")
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    disenos = relationship("DisenoMezcla", back_populates="usuario", cascade="all, delete-orphan")
