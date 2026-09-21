"""Endpoints para administrar incidentes."""

from datetime import UTC, datetime
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from pydantic import BaseModel, Field

from app.domain.models import Incidente, Severidad
from app.repositories.base import IncidenteRepository
from app.repositories.memory import MemoryIncidenteRepository

router = APIRouter(prefix="/incidentes", tags=["incidentes"])


class IncidenteCrear(BaseModel):
    """Datos requeridos para registrar un incidente."""

    titulo: str = Field(
        min_length=1,
        max_length=200,
        examples=["Caída de la API"],
    )
    severidad: Severidad = Field(examples=[Severidad.SEV1])
    descripcion: str = Field(
        max_length=2000,
        examples=["El servicio devolvió errores 500."],
    )
    ocurrido_en: datetime | None = Field(
        default=None,
        examples=["2026-09-20T15:30:00Z"],
    )


class IncidenteResponse(BaseModel):
    """Representación pública de un incidente."""

    id: UUID
    titulo: str
    severidad: Severidad
    descripcion: str
    ocurrido_en: datetime

    @classmethod
    def desde_dominio(cls, incidente: Incidente) -> "IncidenteResponse":
        return cls(
            id=incidente.id,
            titulo=incidente.titulo,
            severidad=incidente.severidad,
            descripcion=incidente.descripcion,
            ocurrido_en=incidente.ocurrido_en,
        )


_repositorio = MemoryIncidenteRepository()


def get_incidente_repository() -> IncidenteRepository:
    """Devuelve el repositorio utilizado por la aplicación."""
    return _repositorio


Repositorio = Annotated[
    IncidenteRepository,
    Depends(get_incidente_repository),
]


@router.post(
    "",
    response_model=IncidenteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un incidente",
)
def crear_incidente(
    datos: IncidenteCrear,
    repositorio: Repositorio,
) -> IncidenteResponse:
    ocurrido_en = datos.ocurrido_en or datetime.now(UTC)

    try:
        incidente = Incidente(
            titulo=datos.titulo,
            severidad=datos.severidad,
            descripcion=datos.descripcion,
            ocurrido_en=ocurrido_en,
        )
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error

    incidente_creado = repositorio.crear(incidente)
    return IncidenteResponse.desde_dominio(incidente_creado)


@router.get(
    "",
    response_model=list[IncidenteResponse],
    summary="Listar incidentes",
)
def listar_incidentes(
    repositorio: Repositorio,
    offset: Annotated[int, Query(ge=0)] = 0,
    limite: Annotated[int, Query(ge=1, le=100)] = 20,
) -> list[IncidenteResponse]:
    return [
        IncidenteResponse.desde_dominio(incidente)
        for incidente in repositorio.listar(offset, limite)
    ]


@router.get(
    "/{incidente_id}",
    response_model=IncidenteResponse,
    summary="Obtener un incidente",
)
def obtener_incidente(
    incidente_id: UUID,
    repositorio: Repositorio,
) -> IncidenteResponse:
    incidente = repositorio.obtener(incidente_id)

    if incidente is None:
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    return IncidenteResponse.desde_dominio(incidente)


@router.delete(
    "/{incidente_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un incidente",
)
def eliminar_incidente(
    incidente_id: UUID,
    repositorio: Repositorio,
) -> Response:
    if not repositorio.eliminar(incidente_id):
        raise HTTPException(status_code=404, detail="Incidente no encontrado")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
