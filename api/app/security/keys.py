"""Criptografia das chaves de provedor guardadas por usuário.

A chave mestra é derivada de `APP_SECRET_KEY`. Nenhum segredo aparece em log,
resposta de API ou mensagem de erro. Trocar a chave mestra invalida as
credenciais salvas — o usuário cadastra a chave novamente.
"""

from __future__ import annotations

import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken

from ..config import settings


class SecretUnavailableError(Exception):
    """A credencial salva não pode ser lida com a chave mestra atual."""


def _fernet() -> Fernet:
    digest = hashlib.sha256(settings.app_secret_key.encode("utf-8")).digest()
    return Fernet(base64.urlsafe_b64encode(digest))


def encrypt_secret(plain: str) -> str:
    """Cifra um segredo e devolve o token em ASCII, pronto para o banco."""
    return _fernet().encrypt(plain.encode("utf-8")).decode("ascii")


def decrypt_secret(cipher: str) -> str:
    """Decifra um segredo. A mensagem de erro nunca contém o valor cifrado."""
    try:
        return _fernet().decrypt(cipher.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, UnicodeDecodeError) as exc:
        raise SecretUnavailableError(
            "Não foi possível ler a chave salva. A chave mestra pode ter mudado — "
            "cadastre a credencial novamente."
        ) from exc


def mask_secret(plain: str) -> str:
    """Dica visual para a UI: `sk-…a1b2`. Nunca é suficiente para autenticar."""
    value = plain.strip()
    if len(value) <= 8:
        return "…"
    return f"{value[:3]}…{value[-4:]}"
