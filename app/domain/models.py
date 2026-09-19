"""Modelos del dominio de incidentes."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4


class Severidad(StrEnum):
    """Niveles válidos de severidad de un incidente."""

    SEV1 = "SEV1"
    SEV2 = "SEV2"
    SEV3 = "SEV3"


@dataclass(frozen=True)
class Incidente:
    """Incidente ocurrido en el entorno de producción."""

    titulo: str
    severidad: Severidad
    descripcion: str
    ocurrido_en: datetime
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        """Valida las reglas fundamentales del incidente."""
        if not self.titulo.strip():
            raise ValueError("El título no puede estar vacío")

        ahora = datetime.now(self.ocurrido_en.tzinfo or UTC)

        if self.ocurrido_en > ahora:
            raise ValueError("La fecha del incidente no puede ser futura")
