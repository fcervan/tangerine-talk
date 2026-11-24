"""Ponto de entrada da API.

As rotas são servidas na raiz (`/health`, `/auth/...`). O Next faz proxy de
`/api/*` para cá, removendo o prefixo — assim o navegador fala sempre com a
mesma origem e os cookies `httpOnly` funcionam sem CORS.
"""

from __future__ import annotations

from fastapi import FastAPI

from . import __version__
from .config import settings

app = FastAPI(
    title="Tangerine Talk API",
    version=__version__,
    docs_url="/docs",
    redoc_url=None,
)


@app.get("/health", tags=["meta"])
def health() -> dict[str, str]:
    """Verificação de liveness usada pelo Docker e pelo CI."""
    return {"status": "ok", "env": settings.app_env, "version": __version__}
