from sqlmodel import select

from models import Hero, HeroUpdate
from database.db import get_session


def create_hero(hero: Hero):
    with get_session() as session:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero

def get_all_heroes():
    with get_session() as session:
        statement = select(Hero)
        return session.exec(statement).all()

def get_hero_by_name(name: str):
    with get_session() as session:
        statement = select(Hero).where(Hero.name == name)
        return session.exec(statement).first()
    
def get_hero_by_id(id: int):
    with get_session() as session:
        statement = select(Hero).where(Hero.id == id)
        return session.exec(statement).first()

def remove_hero(hero: Hero):
    with get_session() as session:
        statement = session.delete(hero)
        session.commit()
        return f"{hero.name} ha sido ELIMINADO"
    
def commit_update_to_db(hero_update_data: HeroUpdate, hero_db: Hero):
    with get_session() as session:
        
        session.add(hero_db)
        
        update_data = hero_update_data.model_dump(exclude_unset=True)
        
        hero_db.sqlmodel_update(update_data)
        

        session.add(hero_db)
        session.commit()
        session.refresh(hero_db)
        
        print(f"{hero_db.name} ha sido ACTUALIZADO")
        return hero_db