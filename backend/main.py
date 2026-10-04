"""FastAPI app entry point — Phase 5."""
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from .config import get_settings
from .database import Base, engine
from .routers import (
    auth, docs, sheets, slides, export, solver, import_legacy,
    ai, collab, admin,
)

settings = get_settings()

app = FastAPI(title=settings.app_name, version="0.5.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
    return response


app.include_router(auth.router)
app.include_router(docs.router)
app.include_router(sheets.router)
app.include_router(slides.router)
app.include_router(export.router)
app.include_router(solver.router)
app.include_router(import_legacy.router)
app.include_router(ai.router)
app.include_router(collab.router)
app.include_router(admin.router)


@app.get("/healthz")
def healthz():
    return {"status": "ok", "version": "0.5.0"}


@app.get("/readyz")
def readyz():
    return {"status": "ready"}


Base.metadata.create_all(bind=engine)

frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")