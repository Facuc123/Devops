"""Repositorio de incidentes almacenado en memoria."""

from uuid import UUID

from app.domain.models import Incidente


class MemoryIncidenteRepository:
    def __init__(self) -> None:
        self._incidentes: dict[UUID, Incidente] = {}

    def crear(self, incidente: Incidente) -> Incidente:
        self._incidentes[incidente.id] = incidente
        return incidente

    def listar(self, offset: int = 0, limite: int = 20) -> list[Incidente]:
        incidentes = sorted(
            self._incidentes.values(),
            key=lambda incidente: incidente.ocurrido_en,
            reverse=True,
        )
        return incidentes[offset : offset + limite]

    def obtener(self, incidente_id: UUID) -> Incidente | None:
        return self._incidentes.get(incidente_id)

    def eliminar(self, incidente_id: UUID) -> bool:
        return self._incidentes.pop(incidente_id, None) is not None
