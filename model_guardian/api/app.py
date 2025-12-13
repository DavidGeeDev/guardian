from __future__ import annotations

from fastapi import FastAPI

from .routes import router

app = FastAPI(title="Model Guardian (Phase 0)")
app.include_router(router)
