"""Pruebas de las métricas Prometheus."""

from collections.abc import Iterator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from prometheus_client import REGISTRY

from app.config import get_settings
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_configuracion() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def contar_requests(method: str, route: str, status_code: str) -> float:
    valor = REGISTRY.get_sample_value(
        "http_requests_total",
        {"method": method, "route": route, "status_code": status_code},
    )
    return valor or 0.0


def contar_latencias(method: str, route: str) -> float:
    valor = REGISTRY.get_sample_value(
        "http_request_duration_seconds_count",
        {"method": method, "route": route},
    )
    return valor or 0.0


def test_metrics_expone_formato_prometheus() -> None:
    respuesta = client.get("/metrics")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/plain")
    assert "# TYPE http_requests_total counter" in respuesta.text
    assert "# TYPE http_request_duration_seconds histogram" in respuesta.text


def test_request_incrementa_trafico_y_latencia() -> None:
    antes = contar_requests("GET", "/health", "200")
    latencias_antes = contar_latencias("GET", "/health")

    client.get("/health")

    assert contar_requests("GET", "/health", "200") == antes + 1
    assert contar_latencias("GET", "/health") == latencias_antes + 1


def test_rutas_con_parametros_usan_la_plantilla() -> None:
    """Un UUID distinto por request no tiene que crear una serie nueva."""
    ruta = "/incidentes/{incidente_id}"
    antes = contar_requests("GET", ruta, "404")

    client.get(f"/incidentes/{uuid4()}")
    client.get(f"/incidentes/{uuid4()}")

    assert contar_requests("GET", ruta, "404") == antes + 2


def test_rutas_inexistentes_se_agrupan() -> None:
    antes = contar_requests("GET", "sin_ruta", "404")

    client.get("/no-existe")

    assert contar_requests("GET", "sin_ruta", "404") == antes + 1


def test_chaos_boom_se_cuenta_como_error_5xx(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHAOS_ENABLED", "true")
    antes = contar_requests("POST", "/chaos/boom", "500")

    client.post("/chaos/boom")

    assert contar_requests("POST", "/chaos/boom", "500") == antes + 1


def test_metrics_no_se_mide_a_si_mismo() -> None:
    client.get("/metrics")

    assert contar_requests("GET", "/metrics", "200") == 0


def test_app_info_publica_version_y_entorno() -> None:
    settings = get_settings()
    valor = REGISTRY.get_sample_value(
        "app_info",
        {
            "servicio": settings.app_nombre,
            "version": settings.app_version,
            "entorno": settings.entorno,
        },
    )

    assert valor == 1
