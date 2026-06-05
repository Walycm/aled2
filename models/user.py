from pydantic import EmailStr
from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    """Modelo de la tabla 'user' que se añadirá a tu BD existente."""

    __tablename__: str = "user"  # Asegura el nombre de la tabla

    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    email: EmailStr = Field(unique=True, index=True)
    nombre: str
    apellido: str
    role: str  | None = Field(default="basic")
    password_hashed: str  # Aquí se guarda la clave encriptada
    disabled: bool = Field(default=False)

class UserCreate(SQLModel):
    """Modelo para validar los datos que envía el cliente al registrarse."""
    username: str
    email: EmailStr
    nombre: str
    apellido: str
    role: str | None
    password: str  # Contraseña en texto plano que envía el usuario

class UserPublic(SQLModel):
    """Modelo para exponer los datos del usuario de forma segura."""
    id: int
    username: str
    email: EmailStr
    nombre: str
    apellido: str
    role: str | None
    disabled: bool

class UserUpdate(SQLModel):
    """Modelo para actualizar datos básicos. Todo es opcional."""
    email: EmailStr | None = None
    nombre: str | None = None
    apellido: str | None = None
    role: str | None = None


class PasswordUpdate(SQLModel):
    """Modelo estricto para la actualización de contraseña."""
    old_password: str  # Por seguridad, pedimos la contraseña actual
    new_password: str  # La nueva contraseña en texto plano