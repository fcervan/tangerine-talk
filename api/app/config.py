"""Configuração central, carregada de variáveis de ambiente.

Nenhum segredo tem valor padrão utilizável: o que falta é tratado como erro
nos pontos que dependem dele, nunca substituído por um valor "conveniente".
A única exceção é o ambiente de desenvolvimento, onde uma chave efêmera é
gerada em memória (e as sessões morrem quando o processo reinicia).
"""

from __future__ import annotations

import secrets
import sys

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    app_secret_key: str = ""
    public_base_url: str = "http://localhost:3000"
    allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:3110",
    ]

    database_url: str = ""

    access_token_ttl_minutes: int = 15
    refresh_token_ttl_days: int = 30
    invite_ttl_days: int = 7

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    smtp_from: str = "Tangerine Talk <no-reply@localhost>"
    smtp_tls: bool = True

    redis_url: str = ""
    storage_backend: str = "local"
    audio_retention_days: int = 0
    offline_mode: bool = False
    ollama_base_url: str = ""
    provider_timeout_seconds: float = 8.0

    # Qdrant (vetorial)
    qdrant_url: str = "http://127.0.0.1:6333"
    qdrant_api_key: str = ""
    qdrant_timeout: float = 10.0
    embedding_model: str = "BAAI/bge-m3"
    embedding_dim: int = 1024
    collection_prefix: str = "content_v1_"

    @property
    def is_dev(self) -> bool:
        return self.app_env in {"dev", "test"}

    def ensure_secret_key(self) -> None:
        """Garante uma chave utilizável, sem inventar segredo em produção."""
        if self.app_secret_key:
            return
        if not self.is_dev:
            raise RuntimeError(
                "APP_SECRET_KEY é obrigatório fora do ambiente de desenvolvimento. "
                "Gere com: openssl rand -hex 32"
            )
        self.app_secret_key = secrets.token_urlsafe(32)
        print(
            "AVISO: APP_SECRET_KEY não definida. Usando chave efêmera — "
            "as sessões serão invalidadas a cada reinício.",
            file=sys.stderr,
        )


settings = Settings()
