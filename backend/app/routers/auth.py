from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import create_access_token, hash_password, verify_password
from app.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas.auth import RecuperarPasswordInput, Token, UsuarioLogin, UsuarioOut, UsuarioRegistro

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UsuarioOut, status_code=status.HTTP_201_CREATED)
def registrar(datos: UsuarioRegistro, db: Session = Depends(get_db)):
    if db.query(Usuario).filter(Usuario.username == datos.username).first():
        raise HTTPException(status_code=400, detail="El nombre de usuario ya está en uso")
    if db.query(Usuario).filter(Usuario.email == datos.email).first():
        raise HTTPException(status_code=400, detail="El correo ya está registrado")
    if db.query(Usuario).filter(Usuario.codigo == datos.codigo).first():
        raise HTTPException(status_code=400, detail="Ese código ya está registrado")

    es_primer_usuario = db.query(Usuario).count() == 0
    usuario = Usuario(
        username=datos.username,
        email=datos.email,
        password_hash=hash_password(datos.password),
        nombre_completo=datos.nombre_completo.strip(),
        codigo=datos.codigo.strip(),
        rol=datos.rol,
        is_admin=es_primer_usuario,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router.post("/login", response_model=Token)
def iniciar_sesion(datos: UsuarioLogin, db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.username == datos.username).first()
    if usuario is None or not verify_password(datos.password, usuario.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    token = create_access_token(subject=usuario.username, is_admin=usuario.is_admin)
    return Token(access_token=token)


@router.post("/recuperar-password", status_code=status.HTTP_200_OK)
def recuperar_password(datos: RecuperarPasswordInput, db: Session = Depends(get_db)):
    """
    Recuperación sin correo: exige coincidencia exacta de usuario + código +
    nombre completo (los tres a la vez) antes de permitir fijar una nueva
    contraseña. No revela cuál de los tres datos fue incorrecto.
    """
    usuario = (
        db.query(Usuario)
        .filter(
            func.lower(Usuario.username) == datos.username.strip().lower(),
            func.lower(Usuario.codigo) == datos.codigo.strip().lower(),
            func.lower(Usuario.nombre_completo) == datos.nombre_completo.strip().lower(),
        )
        .first()
    )
    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No se encontró una cuenta con ese usuario, código y nombre completo",
        )

    usuario.password_hash = hash_password(datos.nueva_password)
    db.commit()
    return {"status": "ok", "message": "Contraseña actualizada correctamente"}


@router.get("/me", response_model=UsuarioOut)
def usuario_actual(usuario: Usuario = Depends(get_current_user)):
    return usuario
