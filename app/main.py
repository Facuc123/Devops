"""Punto de entrada de la API dias-sin-incidentes."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.config import Settings, get_settings

app = FastAPI(
    title="dias-sin-incidentes",
    description=(
        "El cartel de fábrica *'X días sin accidentes'*, pero para producción.\n\n"
        "Registra incidentes y expone cuántos días lleva el sistema sin caerse."
    ),
    version=get_settings().app_version,
    contact={"name": "Facundo Canto y Luciano Sicolo"},
)


class HealthResponse(BaseModel):
    """Respuesta del chequeo de salud."""

    status: str = Field(examples=["ok"])
    servicio: str = Field(examples=["dias-sin-incidentes"])
    version: str = Field(examples=["0.1.0"])
    entorno: str = Field(examples=["local"])


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["sistema"],
    summary="Chequeo de salud",
    description=(
        "Indica si el proceso está vivo y responde. Lo usan el HEALTHCHECK del "
        "contenedor y la plataforma de deploy para decidir si el servicio está listo."
    ),
)
def health() -> HealthResponse:
    settings: Settings = get_settings()
    return HealthResponse(
        status="ok",
        servicio=settings.app_nombre,
        version=settings.app_version,
        entorno=settings.entorno,
    )
