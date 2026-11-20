from fastapi import FastAPI

app = FastAPI(title="Doomsday Ready API")


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}