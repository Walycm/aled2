from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta

# Importa tus modelos y configuración desde su ubicación real
from models import User, UserCreate, UserPublic, UserUpdate, PasswordUpdate
from database.db import get_db
from services.user_services import (
    obtener_password_hash,
    verificar_password,
    crear_token_acceso,
    get_current_user,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

router = APIRouter(prefix="/users", tags=["Users"])


# ─── ENDPOINTS PÚBLICOS (SIN AUTORIZACIÓN) ───

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def registrar_usuario(
    usuario_in: UserCreate, 
    db: Annotated[Session, Depends(get_db)]
):
    """Permite el registro de nuevos usuarios en el sistema. (PÚBLICO)"""
    # Validar si el username ya existe
    statement_username = select(User).where(User.username == usuario_in.username)
    if db.exec(statement_username).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El nombre de usuario ya está registrado.",
        )

    # Validar si el email ya existe
    statement_email = select(User).where(User.email == usuario_in.email)
    if db.exec(statement_email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo electrónico ya está registrado.",
        )

    # Encriptar y guardar
    nuevo_usuario = User(
        username=usuario_in.username,
        email=usuario_in.email,
        nombre=usuario_in.nombre,
        apellido=usuario_in.apellido,
        password_hashed=obtener_password_hash(usuario_in.password),
        role=usuario_in.role,
        disabled=False,
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    
    return {"mensaje": "Usuario registrado exitosamente"}


@router.post("/token")
async def login_para_obtener_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Annotated[Session, Depends(get_db)],
):
    """Endpoint para autenticarse e intercambiar credenciales por un JWT. (PÚBLICO)"""
    statement = select(User).where(User.username == form_data.username)
    user = db.exec(statement).first()

    if not user or not verificar_password(form_data.password, user.password_hashed):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_token_acceso(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return {"access_token": access_token, "token_type": "bearer"}


# ─── ENDPOINTS PROTEGIDOS (REQUIEREN TOKEN JWT) ───

@router.get("/me", response_model=UserPublic)
async def leer_perfil_propio(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Devuelve la información del usuario actualmente logueado. (PROTEGIDO)"""
    return current_user


@router.get("/", response_model=list[UserPublic])
async def listar_usuarios(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Devuelve la lista completa de usuarios. (PROTEGIDO)"""
    statement = select(User)
    usuarios = db.exec(statement).all()
    return usuarios

@router.patch("/update", response_model=UserPublic)
async def actualizar_datos_perfil(
    datos_actualizados: UserUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Actualiza los datos del usuario autenticado (nombre, apellido o email).
    Los campos que no se envíen en el JSON se mantendrán intactos.
    """
    # Convertimos los datos entrantes a un diccionario, ignorando los que vengan como None
    update_data = datos_actualizados.model_dump(exclude_unset=True)
    
    # Asignamos los nuevos valores dinámicamente al usuario actual
    for key, value in update_data.items():
        setattr(current_user, key, value)
        
    # Guardamos los cambios en la base de datos
    db.add(current_user)
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.patch("/me/change-password")
async def cambiar_contrasena(
    datos_password: PasswordUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    """
    Cambia la contraseña del usuario autenticado.
    Verifica primero que la contraseña vieja sea correcta y luego hashea la nueva.
    """
    # 1. Validar que la contraseña anterior sea la correcta antes de hacer cambios
    if not verificar_password(datos_password.old_password, current_user.password_hashed):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña actual es incorrecta."
        )
        
    # 2. Hashear la nueva contraseña con el bcrypt nativo que creamos
    nueva_password_hashed = obtener_password_hash(datos_password.new_password)
    
    # 3. Asignar el nuevo hash y guardar
    current_user.password_hashed = nueva_password_hashed
    db.add(current_user)
    db.commit()
    
    return {"mensaje": "Contraseña actualizada exitosamente."}

@router.get("/public", response_model=list[UserPublic])
async def listar_usuarios_publico(db: Annotated[Session, Depends(get_db)]):
    """Devuelve la lista de todos los usuarios registrados de forma abierta.

    (PÚBLICO - No requiere Token JWT de autorización)
    """
    # 1. Traer todos los registros de la tabla 'user'
    statement = select(User)
    usuarios = db.exec(statement).all()

    # 2. Retornar la lista (FastAPI remueve 'password_hashed' usando el esquema UserPublic)
    return usuarios