"""Cookies de autenticação.

`httpOnly` impede leitura por JavaScript (mitiga XSS). `SameSite=Lax` impede
envio em requisições cross-site de escrita. `Secure` é ligado fora do dev —
em produção o app deve estar atrás de HTTPS.
"""

from __future__ import annotations

from fastapi import Response

from ..config import settings

ACCESS_COOKIE = "tt_access"
REFRESH_COOKIE = "tt_refresh"


def set_auth_cookies(response: Response, access_token: str, refresh_token: str) -> None:
    secure = not settings.is_dev
    response.set_cookie(
        ACCESS_COOKIE,
        access_token,
        max_age=settings.access_token_ttl_minutes * 60,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )
    response.set_cookie(
        REFRESH_COOKIE,
        refresh_token,
        max_age=settings.refresh_token_ttl_days * 24 * 60 * 60,
        httponly=True,
        samesite="lax",
        secure=secure,
        path="/",
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/")
