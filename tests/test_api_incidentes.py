from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.api.routes_incidentes import get_incidente_repository
from app.main import app
from app.repositories.memory import MemoryIncidenteRepository


@pytest.fixture
def client() -> Iterator[TestClient]:
    repositorio = MemoryIncidenteRepository()
    app.dependency_overrides[get_incidente_repository] = lambda: repositorio

    with TestClient(app) as cliente:
        yield cliente

    app.dependency_overrides.clear()


def datos_incidente() -> dict[str, str]:
    return {
        "titulo": "Caída de la API",
        "severidad": "SEV1",
        "descripcion": "El servicio devolvió errores 500.",
        "ocurrido_en": "2026-09-20T15:30:00Z",
    }


def test_crear_y_listar_incidente(client: TestClient):
    creacion = client.post("/incidentes", json=datos_incidente())

    assert creacion.status_code == 201
    assert creacion.json()["severidad"] == "SEV1"

    listado = client.get("/incidentes")

    assert listado.status_code == 200
    assert len(listado.json()) == 1
    assert listado.json()[0]["id"] == creacion.json()["id"]


def test_obtener_incidente_por_id(client: TestClient):
    creado = client.post("/incidentes", json=datos_incidente()).json()

    respuesta = client.get(f"/incidentes/{creado['id']}")

    assert respuesta.status_code == 200
    assert respuesta.json()["titulo"] == "Caída de la API"


def test_eliminar_incidente(client: TestClient):
    creado = client.post("/incidentes", json=datos_incidente()).json()

    respuesta = client.delete(f"/incidentes/{creado['id']}")

    assert respuesta.status_code == 204
    assert client.get(f"/incidentes/{creado['id']}").status_code == 404


def test_incidente_inexistente_devuelve_404(client: TestClient):
    assert client.get(f"/incidentes/{uuid4()}").status_code == 404
    assert client.delete(f"/incidentes/{uuid4()}").status_code == 404


def test_rechaza_severidad_invalida(client: TestClient):
    datos = datos_incidente()
    datos["severidad"] = "SEV4"

    respuesta = client.post("/incidentes", json=datos)

    assert respuesta.status_code == 422


def test_rechaza_fecha_futura(client: TestClient):
    datos = datos_incidente()
    datos["ocurrido_en"] = (datetime.now(UTC) + timedelta(days=1)).isoformat()

    respuesta = client.post("/incidentes", json=datos)

    assert respuesta.status_code == 422
    assert respuesta.json()["detail"] == "La fecha del incidente no puede ser futura"
