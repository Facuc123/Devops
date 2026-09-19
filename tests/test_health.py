"""Tests del endpoint de salud."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_responde_200():
    respuesta = client.get("/health")
    assert respuesta.status_code == 200


def test_health_devuelve_el_contrato_completo():
    """El HEALTHCHECK del contenedor depende de estos campos: si cambian, se rompe."""
    cuerpo = client.get("/health").json()
    assert cuerpo["status"] == "ok"
    assert cuerpo["servicio"] == "dias-sin-incidentes"
    assert set(cuerpo) == {"status", "servicio", "version", "entorno"}


def test_openapi_esta_expuesto():
    """Swagger es requisito excluyente del TP: que un cambio no lo rompa en silencio."""
    esquema = client.get("/openapi.json")
    assert esquema.status_code == 200
    assert "/health" in esquema.json()["paths"]
