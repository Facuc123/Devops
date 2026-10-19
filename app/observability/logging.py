"""Logging JSON estructurado para las solicitudes HTTP."""

import json
import logging
import sys
from datetime import UTC, datetime
from time import perf_counter
from typing import Any
from uuid import uuid4

from fastapi import Request, Response
from starlette.middleware.base import RequestResponseEndpoint


class JsonFormatter(logging.Formatter):
    """Convierte cada registro HTTP en un objeto JSON de una sola línea."""

    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC)
            .isoformat(timespec="milliseconds")
            .replace("+00:00", "Z"),
            "level": record.levelname,
            "path": record.path,
            "method": record.method,
            "status_code": record.status_code,
            "duration_ms": record.duration_ms,
            "request_id": record.request_id,
        }
        return json.dumps(payload, ensure_ascii=False)


def crear_logger_http() -> logging.Logger:
    """Configura un logger que escribe JSON en stdout."""
    logger = logging.getLogger("dias_sin_incidentes.http")
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter())
        logger.addHandler(handler)

    return logger


http_logger = crear_logger_http()


async def registrar_request(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """Registra método, ruta, estado y duración de cada solicitud."""
    inicio = perf_counter()
    request_id = request.headers.get("X-Request-ID", str(uuid4()))
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        duracion_ms = round((perf_counter() - inicio) * 1000, 2)
        http_logger.info(
            "request_completed",
            extra={
                "path": request.url.path,
                "method": request.method,
                "status_code": status_code,
                "duration_ms": duracion_ms,
                "request_id": request_id,
            },
        )
