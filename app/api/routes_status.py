"""Endpoint del estado operativo del servicio."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.api.routes_incidentes import IncidenteResponse, Repositorio
from app.config import get_settings
from app.domain.calculos import (
    dias_sin_incidentes,
    record_historico,
)

router = APIRouter(tags=["estado"])


class StatusResponse(BaseModel):
    """Resumen del tiempo transcurrido sin incidentes."""

    dias_sin_incidentes: int = Field(ge=0, examples=[12])
    record_historico: int = Field(ge=0, examples=[47])
    ultimo_incidente: IncidenteResponse | None = None


@router.get(
    "/status",
    response_model=StatusResponse,
    summary="Consultar el estado operativo",
    description=(
        "Calcula los días sin incidentes y el récord histórico "
        "utilizando todos los incidentes registrados."
    ),
)
def obtener_status(repositorio: Repositorio) -> StatusResponse:
    incidentes = repositorio.listar(limite=None)
    settings = get_settings()

    ultimo_incidente = (
        max(
            incidentes,
            key=lambda incidente: incidente.ocurrido_en,
        )
        if incidentes
        else None
    )

    return StatusResponse(
        dias_sin_incidentes=dias_sin_incidentes(
            incidentes,
            settings.fecha_inicio_operaciones,
        ),
        record_historico=record_historico(
            incidentes,
            settings.fecha_inicio_operaciones,
        ),
        ultimo_incidente=(
            IncidenteResponse.desde_dominio(ultimo_incidente) if ultimo_incidente else None
        ),
    )
