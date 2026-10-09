from typing import Protocol
from uuid import UUID

from app.domain.models import Incidente


class IncidenteRepository(Protocol):
    """Operaciones requeridas para administrar incidentes."""

    def crear(self, incidente: Incidente) -> Incidente: ...

    def listar(self, offset: int = 0, limite: int = 20) -> list[Incidente]: ...

    def obtener(self, incidente_id: UUID) -> Incidente | None: ...

    def eliminar(self, incidente_id: UUID) -> bool: ...
