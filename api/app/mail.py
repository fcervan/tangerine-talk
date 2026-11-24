"""Envio de e-mail transacional.

SMTP é opcional. Sem ele, a API devolve o link do convite para o owner copiar
e enviar pelo canal que quiser — a instância continua funcional.
"""

from __future__ import annotations

import asyncio
import smtplib
import sys
from datetime import datetime
from email.message import EmailMessage

from .config import settings


def smtp_configured() -> bool:
    return bool(settings.smtp_host)


def _send_sync(to_email: str, subject: str, body: str) -> None:
    message = EmailMessage()
    message["From"] = settings.smtp_from
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=20) as smtp:
        if settings.smtp_tls:
            smtp.starttls()
        if settings.smtp_user:
            smtp.login(settings.smtp_user, settings.smtp_password)
        smtp.send_message(message)


async def send_invite(to_email: str, invite_url: str, expires_at: datetime) -> bool:
    if not smtp_configured():
        return False

    body = (
        "Você foi convidada(o) para usar o Tangerine Talk.\n\n"
        f"Abra o link para criar sua conta:\n{invite_url}\n\n"
        f"O convite expira em {expires_at:%d/%m/%Y às %H:%M} (UTC).\n\n"
        "Se você não esperava este convite, ignore esta mensagem."
    )
    try:
        await asyncio.to_thread(
            _send_sync, to_email, "Convite para o Tangerine Talk", body
        )
    except (OSError, smtplib.SMTPException) as exc:
        print(f"AVISO: falha ao enviar convite por e-mail: {exc}", file=sys.stderr)
        return False
    return True
