from contextlib import asynccontextmanager

from fastapi import FastAPI

from app import models  # noqa: F401  (import registers the tables)
from app.database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Doomsday Ready API", lifespan=lifespan)


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
