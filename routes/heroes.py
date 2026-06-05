from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from models import Hero, HeroUpdate, User  # Asegúrate de importar el modelo User

# Importa tu dependencia de autenticación desde tus servicios
from services.user_services import get_current_user, RoleChecker
from repositories.hero_db import (
    create_hero,
    get_all_heroes,
    get_hero_by_name,
    get_hero_by_id,
    remove_hero,
    commit_update_to_db,
)

router = APIRouter(prefix="/heroes", tags=["Heroes"], dependencies=[Depends(RoleChecker(["admin", "basic"]))])
# Creamos las instancias de los guardianes
allow_admin = RoleChecker(["admin"])
allow_all_authenticated = RoleChecker(["admin", "basic"])

@router.get("/")
async def obtener_todos_los_heroes(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Obtener todos los héroes (Solo usuarios autenticados)."""
    heroes = get_all_heroes()
    return heroes


@router.post("/", status_code=status.HTTP_201_CREATED)
async def agregar_hero(
    datos: Hero, current_user: Annotated[User, Depends(get_current_user)]
):
    """Agregar un nuevo héroe (Solo usuarios autenticados)."""
    create_hero(datos)
    return {"message": f"Se está agregando {datos.name}"}


# --- DETALLE IMPORTANTE CON LAS RUTAS DINÁMICAS (Ver explicación abajo) ---


@router.get("/id/{id}")
def leer_hero_por_id(
    id: int, current_user: Annotated[User, Depends(get_current_user)]
) -> Hero:
    """Buscar héroe por ID (Solo usuarios autenticados)."""
    hero = get_hero_by_id(id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@router.get("/name/{name}")
def leer_hero_por_nombre(
    name: str, current_user: Annotated[User, Depends(get_current_user)]
) -> Hero:
    """Buscar héroe por nombre (Solo usuarios autenticados)."""
    hero = get_hero_by_name(name)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


# ────────────────────────────────────────────────────────────────────────


@router.delete("/{hero_id}")
def eliminar_hero(
    hero_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    """Eliminar un héroe (Solo usuarios autenticados)."""
    hero = get_hero_by_id(hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    remove_hero(hero)
    return {"message": "Héroe eliminado con éxito"}


@router.patch("/{hero_id}")
def actualizar_hero(
    hero_id: int,
    hero: HeroUpdate,
    current_user: Annotated[User, Depends(get_current_user)],
):
    """Actualizar datos de un héroe (Solo usuarios autenticados)."""
    hero_db = get_hero_by_id(hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    updated_hero = commit_update_to_db(hero, hero_db)

    return updated_hero