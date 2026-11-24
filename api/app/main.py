"""Ponto de entrada da API.

As rotas são servidas na raiz (`/health`, `/auth/...`). O Next faz proxy de
`/api/*` para cá, removendo o prefixo — assim o navegador fala sempre com a
mesma origem e os cookies `httpOnly` funcionam sem CORS.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.base import RequestResponseEndpoint
from starlette.responses import Response

from . import __version__
from .auth.deps import SessionDep
from .auth.router import router as auth_router
from .config import settings
from .content.router import router as content_router
from .db import dispose_engine
from .gamification.router import router as gamification_router
from .providers.router import router as providers_router
from .tutor.router import router as tutor_router
from .users.router import router as users_router


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    settings.ensure_secret_key()
    yield
    await dispose_engine()


app = FastAPI(
    title="Tangerine Talk API",
    version=__version__,
    docs_url="/docs",
    redoc_url=None,
    lifespan=lifespan,
)


@app.middleware("http")
async def origin_guard(request: Request, call_next: RequestResponseEndpoint) -> Response:
    """Bloqueia escrita vinda de origem desconhecida (defesa extra contra CSRF).

    Navegadores enviam `Origin` em POST/PATCH/DELETE. Requisições sem `Origin`
    (curl, testes, jobs) passam — a proteção real continua sendo o cookie
    `httpOnly` + `SameSite=Lax`.
    """
    if request.method in {"POST", "PUT", "PATCH", "DELETE"}:
        origin = request.headers.get("origin")
        if origin is not None and origin not in settings.allowed_origins:
            return JSONResponse(
                {"detail": "Origem não permitida."},
                status_code=status.HTTP_403_FORBIDDEN,
            )
    return await call_next(request)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Liveness: a API está de pé? Não toca no banco."""
    return {"status": "ok", "env": settings.app_env, "version": __version__}


@app.get("/ready", tags=["meta"])
async def ready(session: SessionDep) -> dict[str, str]:
    """Readiness: a API consegue falar com o banco?"""
    await session.execute(text("SELECT 1"))
    return {"status": "ready"}


app.include_router(auth_router)
app.include_router(users_router)
app.include_router(providers_router)
app.include_router(content_router)
app.include_router(gamification_router)
app.include_router(tutor_router)
