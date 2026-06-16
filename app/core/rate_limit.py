"""Rate limiting simple en memoria para endpoints de autenticación.

Implementa el spec §4.3: máximo 5 intentos FALLIDOS por IP en una ventana de 15
minutos sobre login y registro. Al superarlo responde 429 con header Retry-After.
Solo cuenta los intentos fallidos (un login/registro exitoso no suma).
"""
from __future__ import annotations

import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request, status


class RateLimiter:
    def __init__(self, max_attempts: int = 5, window_seconds: int = 15 * 60) -> None:
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
        self._attempts: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def _purge(self, ip: str, ahora: float) -> None:
        cola = self._attempts[ip]
        limite = ahora - self.window_seconds
        while cola and cola[0] < limite:
            cola.popleft()

    def enforce(self, ip: str) -> None:
        """Lanza 429 si la IP ya superó el límite de intentos fallidos."""
        ahora = time.monotonic()
        with self._lock:
            self._purge(ip, ahora)
            cola = self._attempts[ip]
            if len(cola) >= self.max_attempts:
                retry_after = int(self.window_seconds - (ahora - cola[0])) + 1
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Demasiados intentos fallidos. Probá de nuevo más tarde.",
                    headers={"Retry-After": str(max(retry_after, 1))},
                )

    def record_failure(self, ip: str) -> None:
        """Registra un intento fallido para la IP."""
        ahora = time.monotonic()
        with self._lock:
            self._purge(ip, ahora)
            self._attempts[ip].append(ahora)

    def reset(self) -> None:
        """Limpia todo el estado (usado por los tests entre casos)."""
        with self._lock:
            self._attempts.clear()


login_rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"
