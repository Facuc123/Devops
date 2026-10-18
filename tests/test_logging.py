"""Pruebas del logging JSON estructurado."""

import json
import logging
from collections.abc import Iterator
from io import StringIO
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.observability.logging import http_logger


@pytest.fixture
def salida_logs() -> Iterator[StringIO]:
    """Redirige temporalmente el logger HTTP a memoria."""
    handler = http_logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)

    salida = StringIO()
    stream_original = handler.setStream(salida)
    try:
        yield salida
    finally:
        handler.setStream(stream_original)


def buscar_log_http(salida: str, path: str) -> dict[str, Any]:
    """Busca en stdout el registro JSON correspondiente a una ruta."""
    registros = [json.loads(linea) for linea in salida.splitlines() if linea.startswith("{")]
    return next(registro for registro in registros if registro.get("path") == path)


def test_request_genera_log_json_y_request_id(
    salida_logs: StringIO,
) -> None:
    with TestClient(app) as client:
        respuesta = client.get("/health")

    log = buscar_log_http(salida_logs.getvalue(), "/health")

    assert respuesta.status_code == 200
    assert respuesta.headers["X-Request-ID"] == log["request_id"]
    assert log["level"] == "INFO"
    assert log["method"] == "GET"
    assert log["status_code"] == 200
    assert log["duration_ms"] >= 0
    assert log["timestamp"].endswith("Z")


def test_request_conserva_request_id_recibido(
    salida_logs: StringIO,
) -> None:
    with TestClient(app) as client:
        respuesta = client.get(
            "/health",
            headers={"X-Request-ID": "request-de-prueba"},
        )

    log = buscar_log_http(salida_logs.getvalue(), "/health")

    assert respuesta.headers["X-Request-ID"] == "request-de-prueba"
    assert log["request_id"] == "request-de-prueba"
