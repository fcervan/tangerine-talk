"""Esquemas de BYOK. Nenhum esquema de saída expõe a chave cadastrada."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator, model_validator

from .catalog import ProviderSlug, ProviderSpec, get_spec

TestStatus = Literal["ok", "invalid_key", "quota", "provider_error", "network"]


def clean_url(value: str | None) -> str | None:
    if value is None:
        return None
    url = value.strip().rstrip("/")
    if not url:
        return None
    if "@" in url:
        raise ValueError("A URL não pode conter credenciais.")
    if not url.startswith(("http://", "https://")):
        raise ValueError("Use uma URL http:// ou https://.")
    return url


def clean_model(value: str | None) -> str | None:
    return value.strip() if value else None


def validate_fields(spec: ProviderSpec, api_key: str | None, base_url: str | None) -> None:
    """Regras compartilhadas pela criação e pela atualização."""
    key = (api_key or "").strip()
    if spec.needs_key and not key:
        raise ValueError("Informe a chave de API deste provedor.")
    if not spec.needs_key and key:
        raise ValueError("Este provedor não usa chave de API.")
    if spec.cloud and base_url and not base_url.startswith("https://"):
        raise ValueError("Provedores em nuvem exigem HTTPS.")


class ProviderIn(BaseModel):
    provider: ProviderSlug
    api_key: str | None = Field(default=None, max_length=512)
    base_url: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, min_length=1, max_length=120)
    is_active: bool = True

    @field_validator("base_url")
    @classmethod
    def check_url(cls, value: str | None) -> str | None:
        return clean_url(value)

    @field_validator("model")
    @classmethod
    def check_model(cls, value: str | None) -> str | None:
        return clean_model(value)

    @model_validator(mode="after")
    def check_provider_fields(self) -> ProviderIn:
        spec = get_spec(self.provider)
        if spec is None:  # O Literal já garante; defesa em profundidade.
            raise ValueError("Provedor desconhecido.")
        validate_fields(spec, self.api_key, self.base_url)
        if self.api_key is not None:
            self.api_key = self.api_key.strip()
        return self


class ProviderUpdateIn(BaseModel):
    api_key: str | None = Field(default=None, max_length=512)
    base_url: str | None = Field(default=None, max_length=255)
    model: str | None = Field(default=None, min_length=1, max_length=120)
    is_active: bool | None = None

    @field_validator("base_url")
    @classmethod
    def check_url(cls, value: str | None) -> str | None:
        return clean_url(value)

    @field_validator("model")
    @classmethod
    def check_model(cls, value: str | None) -> str | None:
        return clean_model(value)


class ProviderOut(BaseModel):
    id: uuid.UUID
    provider: str
    label: str
    key_hint: str | None
    base_url: str
    model: str
    capabilities: list[str]
    is_active: bool
    last_tested_at: datetime | None = None
    last_used_at: datetime | None = None
    last_error: str | None = None
    created_at: datetime


class ProviderListOut(BaseModel):
    items: list[ProviderOut]
    catalog: list[dict[str, object]]
    fallback_order: list[str]
    offline_mode: bool


class ProviderTestOut(BaseModel):
    provider: str
    ok: bool
    status: TestStatus
    message: str
    latency_ms: int | None = None


class RouteItem(BaseModel):
    provider: str
    label: str
    model: str


class RouteOut(BaseModel):
    task: str
    chain: list[RouteItem]
    offline_mode: bool
