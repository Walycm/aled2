
from models import Hero, Team
from repositories.hero_db import create_hero


def create_initial_data():
    deadpool = Hero(name="Juan", secret_name="DeadPool", age=24)
    spiderman = Hero(name="Peter", secret_name="Spiderman")

    team = Team(
        name="Ultras",
        headquarters="Blanco",
        heroes=[deadpool, spiderman]
    )

    create_hero(deadpool)
    create_hero(spiderman)

    return team