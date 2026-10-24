from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import decode_access_token
from app.models.usuario import Usuario

# tokenUrl es solo documentación para /docs; el token real se obtiene vía
# /auth/login y se reenvía como "Authorization: Bearer <token>" desde el
# backend-for-frontend de Next.js (cookie httpOnly del lado del navegador,
# nunca expuesta a JS de cliente).
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> Usuario:
    credenciales_invalidas = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No autenticado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credenciales_invalidas

    payload = decode_access_token(token)
    if payload is None:
        raise credenciales_invalidas

    usuario = db.query(Usuario).filter(Usuario.username == payload.get("sub")).first()
    if usuario is None:
        raise credenciales_invalidas

    return usuario


def require_admin(usuario: Usuario = Depends(get_current_user)) -> Usuario:
    if not usuario.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requiere privilegios de administrador")
    return usuario
