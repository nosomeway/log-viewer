from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .routes_logs import router as logs_router
from .settings import repo_root

app = FastAPI(title="Log Viewer")
app.include_router(logs_router)

_frontend = repo_root() / "frontend"
if _frontend.is_dir():
    app.mount("/", StaticFiles(directory=str(_frontend), html=True), name="frontend")


@app.get("/api/health")
def health() -> dict:
    return {"ok": True}
