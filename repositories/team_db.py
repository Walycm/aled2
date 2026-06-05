from sqlmodel import select

from models import Team
from database.db import get_session


def create_team(team: Team):
    with get_session() as session:
        session.add(team)
        session.commit()
        session.refresh(team)
        return team


def get_all_teams():
    with get_session() as session:
        statement = select(Team)
        return session.exec(statement).all()


def get_team_by_name(name: str):
    with get_session() as session:
        statement = select(Team).where(Team.name == name)
        return session.exec(statement).first()
    
def get_team_by_id(id: int):
    with get_session() as session:
        statement = select(Team).where(Team.id == id)
        return session.exec(statement).first()

def remove_team(team: Team):
    with get_session() as session:
        statement = session.delete(team)
        return f"{team.name} ha sido ELIMINADO"