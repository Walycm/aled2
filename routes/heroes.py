from fastapi import APIRouter, HTTPException
from models import Hero, HeroUpdate
from repositories.hero_db import create_hero, get_all_heroes, get_hero_by_name, get_hero_by_id, remove_hero, commit_update_to_db

router = APIRouter(prefix="/heroes", tags=["Heroes"])

@router.get("/")
async def obtener_todos_los_heroes():
    #Obtener todos los heroes
    heroes = get_all_heroes()

    for hero in heroes:
        print(hero)
    return (heroes)

@router.post("/")
async def agregar_hero(datos : Hero):
    create_hero(datos)
    return {f"Se está agregando {datos}"}


@router.get("/{name}")
def leer_hero_por_nombre(name: str) -> Hero:
    hero = get_hero_by_name(name)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@router.get("/{id}")
def leer_hero_por_id(id: int) -> Hero:
    hero = get_hero_by_id(id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@router.delete("/{hero_id}")
def eliminar_hero(hero_id: int):
    hero = get_hero_by_id(hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return {remove_hero(hero)}

@router.patch("/{hero_id}")
def actualizar_hero(hero_id: int, hero: HeroUpdate):

    hero_db = get_hero_by_id(hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    updated_hero = commit_update_to_db(hero, hero_db)
    
    return updated_hero