"""Configuração central, carregada de variáveis de ambiente.

Nenhum segredo tem valor padrão utilizável: o que falta é tratado como erro
nos pontos que dependem dele, nunca substituído por um valor "conveniente".
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_env: str = "dev"
    app_secret_key: str = ""

    database_url: str = ""

    smtp_host: str = ""
    smtp_port: int = 587
    smtp_from: str = "Tangerine Talk <no-reply@localhost>"

    redis_url: str = ""
    storage_backend: str = "local"
    audio_retention_days: int = 0
    offline_mode: bool = False
    ollama_base_url: str = ""


settings = Settings()
