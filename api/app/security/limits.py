"""Limite simples de tentativas de login.

É melhor-esforço e vale para um processo: sem Redis, cada worker tem a própria
contagem. Serve para encarecer força bruta, não como garantia distribuída.
"""

from __future__ import annotations

from collections import deque
from time import monotonic


class LoginLimiter:
    def __init__(self, max_attempts: int = 10, window_seconds: int = 900) -> None:
        self._max_attempts = max_attempts
        self._window = window_seconds
        self._failures: dict[str, deque[float]] = {}

    def _recent(self, key: str) -> deque[float]:
        now = monotonic()
        bucket = self._failures.setdefault(key, deque())
        while bucket and now - bucket[0] > self._window:
            bucket.popleft()
        return bucket

    def blocked(self, key: str) -> bool:
        return len(self._recent(key)) >= self._max_attempts

    def record_failure(self, key: str) -> None:
        self._recent(key).append(monotonic())

    def reset(self, key: str) -> None:
        self._failures.pop(key, None)


login_limiter = LoginLimiter()
