from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app import models  # noqa: F401  (import registers the tables)
from app.database import Base, engine
from app.errors import register_error_handlers
from app.routers import cinemas, movies
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
app = FastAPI(title="Doomsday Ready API", lifespan=lifespan)
register_error_handlers(app)
app.include_router(movies.router)
app.include_router(cinemas.router)
@app.get("/", include_in_schema=False)
def root() -> RedirectResponse:
    return RedirectResponse("/docs")
@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
