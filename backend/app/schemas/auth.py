from typing import Literal

from pydantic import BaseModel, EmailStr, Field

Rol = Literal["estudiante", "profesor"]


class UsuarioRegistro(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    nombre_completo: str = Field(min_length=3, max_length=150)
    codigo: str = Field(min_length=3, max_length=30)
    rol: Rol = "estudiante"


class UsuarioLogin(BaseModel):
    username: str
    password: str


class RecuperarPasswordInput(BaseModel):
    username: str
    codigo: str
    nombre_completo: str
    nueva_password: str = Field(min_length=8, max_length=128)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    nombre_completo: str
    codigo: str
    rol: Rol
    is_admin: bool

    class Config:
        from_attributes = True
