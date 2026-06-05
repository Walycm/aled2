from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from pydantic import EmailStr
from sqlmodel import Session, select
import bcrypt

from models import User
from database.db import get_db

# --- CONFIGURACIÓN DE SEGURIDAD ---
SECRET_KEY = "TU_CLAVE_SECRETA_SUPER_SEGURA_CAMBIAME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


# --- FUNCIONES DE UTILIDAD (Seguridad y Hash Nativo) ---


def obtener_password_hash(password: str) -> str:
    """Genera un hash seguro utilizando Bcrypt nativo."""
    password_bytes = password.encode("utf-8")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password_bytes, salt).decode("utf-8")


def verificar_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def crear_token_acceso(data: dict, expires_delta: timedelta | None = None) -> str:
    """Genera un token JWT firmado."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# --- DEPENDENCIAS DE AUTENTICACIÓN ---


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Valida el token JWT y recupera al usuario real de la base de datos."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    # Buscar usuario en la base de datos real
    statement = select(User).where(User.username == username)
    user = db.exec(statement).first()

    if user is None:
        raise credentials_exception
    if user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario inactivo"
        )

    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        """Recibe la lista de roles permitidos para la ruta."""
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: Annotated[User, Depends(get_current_user)]) -> User:
        """Verifica si el usuario actual tiene uno de los roles permitidos."""
        if current_user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permisos suficientes para realizar esta acción."
            )
        return current_user