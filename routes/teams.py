from fastapi import APIRouter, HTTPException
from models import Team
from repositories.team_db import create_team, get_all_teams, get_team_by_name, get_team_by_id, remove_team

router = APIRouter(prefix="/teams", tags=["Teams"])

@router.get("/")
async def obtener_Teams():
    #Obtener todos los heroes
    teams = get_all_teams()

    for team in teams:
        print(team)
    return (teams)

@router.post("/")
async def agregar_team(datos : Team):
    create_team(datos)
    return {f"Se está agregando {datos}"}


@router.get("/{name}")
def leer_team_por_nombre(name: str) -> Team:
    team = get_team_by_name(name)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.get("/{id}")
def leer_team_por_id(id: int) -> Team:
    team = get_team_by_id(id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@router.delete("/{hero_id}")
def eliminar_team(hero_id: int):
    team = get_team_by_id(hero_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return {remove_team(team)}