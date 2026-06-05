from fastapi import FastAPI
from routes import heroes_router, teams_router

app = FastAPI()

app.include_router(heroes_router)
app.include_router(teams_router)

@app.get("/")
async def root():
    return {"message": "Hello World - Heroes"}


