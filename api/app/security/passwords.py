"""Hash de senha com Argon2id.

Nunca comparamos senha em texto puro, e sempre executamos uma verificação
contra um hash descartável quando o e-mail não existe — para que o tempo de
resposta não revele se a conta existe.
"""

from __future__ import annotations

import contextlib

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

_hasher = PasswordHasher()
_DUMMY_HASH = _hasher.hash("tangerine-dummy-password-for-timing")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password_hash: str, password: str) -> bool:
    try:
        return _hasher.verify(password_hash, password)
    except (VerificationError, InvalidHashError):
        return False


def burn_time() -> None:
    """Consome o mesmo esforço de uma verificação, sem revelar nada."""
    with contextlib.suppress(VerificationError, InvalidHashError):
        _hasher.verify(_DUMMY_HASH, "tangerine-dummy-password-for-timing-errada")


def needs_rehash(password_hash: str) -> bool:
    try:
        return _hasher.check_needs_rehash(password_hash)
    except InvalidHashError:
        return True
