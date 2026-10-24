"""
CRUD de usuarios, exclusivo para administradores (ver deps.require_admin).

Permite ver, editar (incluido el rol estudiante/profesor y el permiso de
administrador) y eliminar cuentas. El primer usuario que se registra en la
plataforma queda como administrador automáticamente (ver routers/auth.py).
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.deps import require_admin
from app.models.usuario import Usuario
from app.schemas.auth import UsuarioOut
from app.schemas.usuario import UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["usuarios"], dependencies=[Depends(require_admin)])


@router.get("", response_model=list[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    """Lista todos los usuarios registrados en la plataforma."""
    return db.query(Usuario).order_by(Usuario.id).all()


@router.patch("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(usuario_id: int, datos: UsuarioUpdate, db: Session = Depends(get_db)):
    """Actualiza solo los campos enviados (ej. cambiar únicamente el rol)."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    if datos.username is not None:
        usuario.username = datos.username
    if datos.email is not None:
        usuario.email = datos.email
    if datos.password is not None:
        usuario.password_hash = hash_password(datos.password)
    if datos.nombre_completo is not None:
        usuario.nombre_completo = datos.nombre_completo
    if datos.codigo is not None:
        usuario.codigo = datos.codigo
    if datos.rol is not None:
        usuario.rol = datos.rol
    if datos.is_admin is not None:
        usuario.is_admin = datos.is_admin

    db.commit()
    db.refresh(usuario)
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Elimina una cuenta y, en cascada, sus diseños y predicciones guardados."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
