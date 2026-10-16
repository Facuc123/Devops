"""Pruebas de la documentación OpenAPI."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_swagger_esta_disponible() -> None:
    respuesta = client.get("/docs")

    assert respuesta.status_code == 200
    assert "swagger-ui" in respuesta.text.lower()


def test_openapi_contiene_metadata_y_endpoints() -> None:
    respuesta = client.get("/openapi.json")

    assert respuesta.status_code == 200

    documento = respuesta.json()
    assert documento["info"]["title"] == "API Días sin Incidentes"
    assert documento["info"]["description"]
    assert documento["info"]["version"]

    tags = {tag["name"] for tag in documento["tags"]}
    assert tags == {"sistema", "incidentes", "estado"}

    assert "/health" in documento["paths"]
    assert "/incidentes" in documento["paths"]
    assert "/incidentes/{incidente_id}" in documento["paths"]
    assert "/status" in documento["paths"]
