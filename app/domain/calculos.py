"""Cálculos puros relacionados con incidentes."""

from collections.abc import Iterable
from datetime import date

from app.domain.models import Incidente


def dias_sin_incidentes(
    incidentes: Iterable[Incidente],
    fecha_inicio_operaciones: date,
    hoy: date | None = None,
) -> int:
    """Calcula los días completos desde el último incidente."""
    fecha_actual = hoy or date.today()
    lista = list(incidentes)

    if not lista:
        return max((fecha_actual - fecha_inicio_operaciones).days, 0)

    fecha_ultimo_incidente = max(incidente.ocurrido_en.date() for incidente in lista)

    return max((fecha_actual - fecha_ultimo_incidente).days, 0)


def record_historico(
    incidentes: Iterable[Incidente],
    fecha_inicio_operaciones: date,
    hoy: date | None = None,
) -> int:
    """Calcula el mayor período registrado sin incidentes."""
    fecha_actual = hoy or date.today()
    fechas = sorted(incidente.ocurrido_en.date() for incidente in incidentes)

    if not fechas:
        return max((fecha_actual - fecha_inicio_operaciones).days, 0)

    periodos = [(fechas[0] - fecha_inicio_operaciones).days]

    periodos.extend(
        (fecha_actual - fecha_anterior).days
        for fecha_anterior, fecha_actual in zip(fechas, fechas[1:], strict=False)
    )

    periodos.append((fecha_actual - fechas[-1]).days)

    return max(periodos)
