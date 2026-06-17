##corta los intentos de login: max 5 fallidos por IP en 15 min, sino tira 429
##solo cuenta los fallidos, si entras bien no suma nada
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
        ##si la IP ya se paso del limite, tira 429
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
        ##anota un intento fallido de esa IP
        ahora = time.monotonic()
        with self._lock:
            self._purge(ip, ahora)
            self._attempts[ip].append(ahora)

    def reset(self) -> None:
        ##limpia todo, lo usan los tests entre casos
        with self._lock:
            self._attempts.clear()


login_rate_limiter = RateLimiter()


def get_client_ip(request: Request) -> str:
    return request.client.host if request.client else "unknown"
