import uvicorn
from fastapi import FastAPI
from src.app.api.routers.heroes_router import router as hero

app = FastAPI()

app.include_router(hero)


if __name__ == "__main__":
    uvicorn.run(app)