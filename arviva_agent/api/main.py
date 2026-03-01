"""API entrypoint."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from arviva_agent.api.routes import router

app = FastAPI(
    title="Arviva Agent API",
    version="1.0.0",
    description=(
        "Detta API låter klienter köra agentmål och läsa status för "
        "Agent-S- och SuperAGI-integrationerna."
    ),
)
app.include_router(router, prefix="/api")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_: Request, exc: RequestValidationError) -> JSONResponse:
    """Mapper FastAPI validation errors to 400 according to API contract."""
    return JSONResponse(status_code=400, content={"detail": exc.errors()})
