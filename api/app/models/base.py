"""Tipos e utilitários compartilhados pelos modelos.

UUIDv7 é gerado localmente (sem dependência) e guardado em `BINARY(16)` no
MySQL — 16 bytes em vez dos 36 de uma string. Datas são UTC "naive", como o
MySQL armazena em `DATETIME(6)`.
"""

from __future__ import annotations

import secrets
import time
import uuid
from datetime import UTC, datetime
from typing import Any

from sqlalchemy import DateTime
from sqlalchemy.dialects import mysql
from sqlalchemy.engine import Dialect
from sqlalchemy.types import LargeBinary, TypeDecorator


def utcnow() -> datetime:
    """Agora em UTC, sem tzinfo (formato que o MySQL guarda)."""
    return datetime.now(UTC).replace(tzinfo=None)


def uuid7() -> uuid.UUID:
    """UUID versão 7: ordenável por tempo, seguro para índice de banco."""
    millis = time.time_ns() // 1_000_000
    rand = secrets.token_bytes(10)
    raw = bytearray(16)
    raw[0:6] = millis.to_bytes(6, "big")
    raw[6] = 0x70 | (rand[0] & 0x0F)
    raw[7] = rand[1]
    raw[8] = 0x80 | (rand[2] & 0x3F)
    raw[9:16] = rand[3:10]
    return uuid.UUID(bytes=bytes(raw))


class UUIDBinary(TypeDecorator[uuid.UUID]):
    """UUID em 16 bytes no MySQL; BLOB equivalente nos demais dialetos."""

    impl = LargeBinary(16)
    cache_ok = True

    def load_dialect_impl(self, dialect: Dialect) -> Any:
        if dialect.name == "mysql":
            return dialect.type_descriptor(mysql.BINARY(16))
        return dialect.type_descriptor(LargeBinary(16))

    def process_bind_param(self, value: Any, dialect: Dialect) -> bytes | None:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value.bytes
        return bytes(value)

    def process_result_value(self, value: Any, dialect: Dialect) -> uuid.UUID | None:
        if value is None:
            return None
        if isinstance(value, uuid.UUID):
            return value
        return uuid.UUID(bytes=value)


Timestamp = DateTime(timezone=False).with_variant(mysql.DATETIME(fsp=6), "mysql")
