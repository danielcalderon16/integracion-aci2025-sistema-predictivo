from pydantic import BaseModel, EmailStr, Field

from app.schemas.auth import Rol


class UsuarioUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    nombre_completo: str | None = Field(default=None, min_length=3, max_length=150)
    codigo: str | None = Field(default=None, min_length=3, max_length=30)
    rol: Rol | None = None
    is_admin: bool | None = None
