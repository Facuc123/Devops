"""Pruebas unitarias de las reglas del dominio."""

from datetime import UTC, date, datetime

import pytest

from app.domain.calculos import dias_sin_incidentes, record_historico
from app.domain.models import Incidente, Severidad


def crear_incidente(fecha: datetime) -> Incidente:
    """Construye un incidente válido para las pruebas."""
    return Incidente(
        titulo="Falla en producción",
        severidad=Severidad.SEV1,
        descripcion="La API dejó de responder",
        ocurrido_en=fecha,
    )


def test_incidente_ocurrido_hoy_devuelve_cero_dias():
    hoy = date(2026, 9, 18)
    incidente = crear_incidente(datetime(2026, 9, 18, 10, tzinfo=UTC))

    resultado = dias_sin_incidentes(
        [incidente],
        fecha_inicio_operaciones=date(2026, 9, 1),
        hoy=hoy,
    )

    assert resultado == 0


def test_calcula_dias_desde_el_ultimo_incidente():
    hoy = date(2026, 9, 18)
    incidente = crear_incidente(datetime(2026, 9, 13, 10, tzinfo=UTC))

    resultado = dias_sin_incidentes(
        [incidente],
        fecha_inicio_operaciones=date(2026, 9, 1),
        hoy=hoy,
    )

    assert resultado == 5


def test_sin_incidentes_cuenta_desde_inicio_de_operaciones():
    resultado = dias_sin_incidentes(
        [],
        fecha_inicio_operaciones=date(2026, 9, 1),
        hoy=date(2026, 9, 18),
    )

    assert resultado == 17


def test_record_historico_considera_periodos_entre_incidentes():
    incidentes = [
        crear_incidente(datetime(2026, 9, 3, tzinfo=UTC)),
        crear_incidente(datetime(2026, 9, 13, tzinfo=UTC)),
        crear_incidente(datetime(2026, 9, 15, tzinfo=UTC)),
    ]

    resultado = record_historico(
        incidentes,
        fecha_inicio_operaciones=date(2026, 9, 1),
        hoy=date(2026, 9, 18),
    )

    assert resultado == 10


def test_record_historico_incluye_el_periodo_actual():
    incidente = crear_incidente(datetime(2026, 9, 5, tzinfo=UTC))

    resultado = record_historico(
        [incidente],
        fecha_inicio_operaciones=date(2026, 9, 1),
        hoy=date(2026, 9, 18),
    )

    assert resultado == 13


def test_rechaza_incidente_con_fecha_futura():
    with pytest.raises(
        ValueError,
        match="La fecha del incidente no puede ser futura",
    ):
        crear_incidente(datetime(2099, 1, 1, tzinfo=UTC))


def test_rechaza_severidad_invalida():
    with pytest.raises(ValueError):
        Severidad("SEV4")
