##mide cuanto tarda cada request, lo muestra por consola y lo manda en el header X-Process-Time-ms
from __future__ import annotations

import logging
import time

from fastapi import FastAPI, Request

logger = logging.getLogger("foodstore.access")


def configure_logging() -> None:
    ##prende el log por consola sin duplicar handlers si ya esta
    root = logging.getLogger()
    if not any(getattr(h, "_foodstore", False) for h in root.handlers):
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)-7s | %(name)s | %(message)s")
        )
        handler._foodstore = True  # type: ignore[attr-defined]
        root.addHandler(handler)
    root.setLevel(logging.INFO)


def register_request_logging(app: FastAPI) -> None:
    ##engancha el middleware de timing en la app. se llama desde main.py
    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        inicio = time.perf_counter()
        response = await call_next(request)
        duracion_ms = (time.perf_counter() - inicio) * 1000

        logger.info(
            "%s %s -> %s (%.2f ms)",
            request.method,
            request.url.path,
            response.status_code,
            duracion_ms,
        )
        response.headers["X-Process-Time-ms"] = f"{duracion_ms:.2f}"
        return response
