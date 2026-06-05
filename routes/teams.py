from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from models import Team, User  # Asegúrate de importar el modelo User para el tipado

# Importa tu dependencia de autenticación
from services.user_services import get_current_user
from repositories.team_db import (
    create_team,
    get_all_teams,
    get_team_by_name,
    get_team_by_id,
    remove_team,
)

router = APIRouter(prefix="/teams", tags=["Teams"])


@router.get("/")
async def obtener_Teams(
    current_user: Annotated[User, Depends(get_current_user)]
):
    """Obtener todos los equipos (Solo usuarios autenticados)."""
    teams = get_all_teams()
    return teams


@router.post("/", status_code=status.HTTP_201_CREATED)
async def agregar_team(
    datos: Team, current_user: Annotated[User, Depends(get_current_user)]
):
    """Agregar un nuevo equipo (Solo usuarios autenticados)."""
    create_team(datos)
    return {"message": f"Se está agregando el equipo {datos.name}"}


# --- PREVENCIÓN DE CONFLICTOS EN RUTAS DINÁMICAS ---


@router.get("/id/{id}")
def leer_team_por_id(
    id: int, current_user: Annotated[User, Depends(get_current_user)]
) -> Team:
    """Buscar equipo por ID (Solo usuarios autenticados)."""
    team = get_team_by_id(id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/name/{name}")
def leer_team_por_nombre(
    name: str, current_user: Annotated[User, Depends(get_current_user)]
) -> Team:
    """Buscar equipo por nombre (Solo usuarios autenticados)."""
    team = get_team_by_name(name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


# ────────────────────────────────────────────────────────────────────────


@router.delete("/{team_id}")
def eliminar_team(
    team_id: int, current_user: Annotated[User, Depends(get_current_user)]
):
    """Eliminar un equipo por su ID (Solo usuarios autenticados)."""
    team = get_team_by_id(team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    remove_team(team)
    return {"message": "Equipo eliminado con éxito"}