from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from fastapi import FastAPI
from routes import heroes_router, teams_router, users_router
from database.db import engine
from models import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    # ─── LO QUE SUCEDE AL INICIAR LA APP ───
    print("Iniciando la aplicación: Creando tablas si no existen...")

    # SQLModel buscará todos los modelos importados y creará las tablas faltantes
    SQLModel.metadata.create_all(engine)

    yield  # Aquí es donde FastAPI "corre" y atiende peticiones

    # ─── LO QUE SUCEDE AL APAGAR LA APP ───
    print("Apagando la aplicación: Limpiando recursos...")
    # Aquí podrías cerrar conexiones persistentes si fuera necesario


# Pasamos el lifespan al inicializar FastAPI
app = FastAPI(lifespan=lifespan)

app.include_router(heroes_router)
app.include_router(teams_router)
app.include_router(users_router)



@app.get("/")
async def root():
    return {"message": "Hello World - Heroes"}


