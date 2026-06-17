##manejo de errores en un solo lugar. todos los errores salen igual:
##{ "detail": "...", "code": "...", "field": "..." }
##son 3 handlers: HTTPException (errores nuestros), validacion de pydantic (422) y el resto (500)
from __future__ import annotations

import logging
from http import HTTPStatus
from typing import Any, Optional

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger("foodstore.errors")


def _code_desde_status(status_code: int) -> str:
    ##pasa el numero a texto (404 -> NOT_FOUND)
    try:
        return HTTPStatus(status_code).name
    except ValueError:
        return "ERROR"


def _problem(
    status_code: int,
    detail: Any,
    *,
    code: Optional[str] = None,
    field: Optional[str] = None,
    headers: Optional[dict] = None,
) -> JSONResponse:
    body = {
        "detail": detail,
        "code": code or _code_desde_status(status_code),
        "field": field,
    }
    return JSONResponse(status_code=status_code, content=body, headers=headers)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    ##mantenemos los headers (ej: el Retry-After del rate limit)
    return _problem(exc.status_code, exc.detail, headers=getattr(exc, "headers", None))


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errores = exc.errors()
    primer = errores[0] if errores else {}
    ##loc viene como ("body", "campo"): le sacamos el prefijo y nos quedamos con el campo
    loc = [str(parte) for parte in primer.get("loc", []) if parte not in ("body", "query", "path")]
    field = ".".join(loc) or None
    detail = primer.get("msg", "Datos de entrada inválidos.")
    return _problem(
        status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail,
        code="VALIDATION_ERROR",
        field=field,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Error no controlado en %s %s", request.method, request.url.path)
    return _problem(
        status.HTTP_500_INTERNAL_SERVER_ERROR,
        "Error interno del servidor.",
        code="INTERNAL_SERVER_ERROR",
    )


def register_exception_handlers(app: FastAPI) -> None:
    ##engancha los 3 handlers en la app. se llama desde main.py
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
