"""Pruebas del endpoint de métricas Prometheus."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_metrics_responde_en_formato_prometheus():
    respuesta = client.get("/metrics")

    assert respuesta.status_code == 200
    assert respuesta.headers["content-type"].startswith("text/plain")


def test_metrics_cuenta_requests_por_status():
    client.get("/health")

    cuerpo = client.get("/metrics").text

    assert 'http_requests_total{method="GET",path="/health",status="200"}' in cuerpo
    assert "http_request_duration_seconds_bucket" in cuerpo


def test_metrics_usa_el_template_de_la_ruta():
    client.get(f"/incidentes/{uuid4()}")

    cuerpo = client.get("/metrics").text

    assert 'path="/incidentes/{incidente_id}"' in cuerpo


def test_metrics_no_se_cuenta_a_si_mismo():
    client.get("/metrics")

    cuerpo = client.get("/metrics").text

    assert 'path="/metrics"' not in cuerpo
