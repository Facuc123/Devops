"""Pruebas del endpoint de caos."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.config import get_settings
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def limpiar_configuracion() -> Iterator[None]:
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_chaos_boom_esta_oculto_si_esta_deshabilitado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHAOS_ENABLED", "false")

    respuesta = client.post("/chaos/boom")

    assert respuesta.status_code == 404
    assert respuesta.json() == {"detail": "Endpoint no disponible"}


def test_chaos_boom_genera_error_si_esta_habilitado(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("CHAOS_ENABLED", "true")

    respuesta = client.post("/chaos/boom")

    assert respuesta.status_code == 500
    assert respuesta.json() == {"detail": "Falla controlada para validar la observabilidad"}
