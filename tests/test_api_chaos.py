"""Pruebas del endpoint de caos."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_chaos_boom_devuelve_error_500() -> None:
    respuesta = client.post("/chaos/boom")

    assert respuesta.status_code == 500
    assert respuesta.json() == {"detail": "Falla controlada para validar la observabilidad"}
