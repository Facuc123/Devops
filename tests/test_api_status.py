"""Pruebas de integración del endpoint de estado."""

from collections.abc import Iterator
from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.api.routes_incidentes import get_incidente_repository
from app.config import get_settings
from app.main import app
from app.repositories.memory import MemoryIncidenteRepository


@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
) -> Iterator[TestClient]:
    inicio = datetime.now(UTC).date() - timedelta(days=10)
    monkeypatch.setenv(
        "FECHA_INICIO_OPERACIONES",
        inicio.isoformat(),
    )
    get_settings.cache_clear()

    repositorio = MemoryIncidenteRepository()
    app.dependency_overrides[get_incidente_repository] = lambda: repositorio

    with TestClient(app) as cliente:
        yield cliente

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def crear_incidente(
    client: TestClient,
    titulo: str,
    dias_atras: int,
) -> None:
    respuesta = client.post(
        "/incidentes",
        json={
            "titulo": titulo,
            "severidad": "SEV2",
            "descripcion": "Incidente utilizado por la prueba.",
            "ocurrido_en": (datetime.now(UTC) - timedelta(days=dias_atras)).isoformat(),
        },
    )

    assert respuesta.status_code == 201


def test_status_sin_incidentes(client: TestClient) -> None:
    respuesta = client.get("/status")

    assert respuesta.status_code == 200

    cuerpo = respuesta.json()
    assert cuerpo["dias_sin_incidentes"] == 10
    assert cuerpo["record_historico"] == 10
    assert cuerpo["ultimo_incidente"] is None


def test_status_calcula_estado_con_incidentes(
    client: TestClient,
) -> None:
    crear_incidente(client, "Primer incidente", 7)
    crear_incidente(client, "Último incidente", 2)

    respuesta = client.get("/status")

    assert respuesta.status_code == 200

    cuerpo = respuesta.json()
    assert cuerpo["dias_sin_incidentes"] == 2
    assert cuerpo["record_historico"] == 5
    assert cuerpo["ultimo_incidente"]["titulo"] == "Último incidente"
