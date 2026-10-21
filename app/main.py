"""Punto de entrada de la API dias-sin-incidentes."""

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.api.routes_chaos import router as chaos_router
from app.api.routes_incidentes import router as incidentes_router
from app.api.routes_status import router as status_router
from app.config import Settings, get_settings
from app.observability.logging import registrar_request
from app.observability.metrics import registrar_metricas
from app.observability.metrics import router as metrics_router

OPENAPI_TAGS = [
    {
        "name": "sistema",
        "description": "Operaciones técnicas para comprobar la salud del servicio.",
    },
    {
        "name": "incidentes",
        "description": "Creación, consulta, listado y eliminación de incidentes.",
    },
    {
        "name": "estado",
        "description": ("Estado operativo calculado a partir del historial de incidentes."),
    },
]

app = FastAPI(
    title="API Días sin Incidentes",
    description=(
        "API REST para registrar incidentes y consultar el tiempo "
        "transcurrido sin fallas.\n\n"
        "Permite administrar incidentes clasificados como `SEV1`, "
        "`SEV2` o `SEV3`, consultar el récord histórico y verificar "
        "la salud del servicio."
    ),
    version=get_settings().app_version,
    contact={
        "name": "Facundo Canto y Luciano Sicolo",
    },
    openapi_tags=OPENAPI_TAGS,
)

app.include_router(incidentes_router)
app.include_router(status_router)
app.include_router(chaos_router)
app.include_router(metrics_router)


app.middleware("http")(registrar_request)
app.middleware("http")(registrar_metricas)


class HealthResponse(BaseModel):
    """Respuesta del chequeo de salud."""

    status: str = Field(
        description="Estado actual del servicio.",
        examples=["ok"],
    )
    servicio: str = Field(
        description="Nombre del servicio.",
        examples=["dias-sin-incidentes"],
    )
    version: str = Field(
        description="Versión actual de la API.",
        examples=["1.0.0"],
    )
    entorno: str = Field(
        description="Entorno donde se ejecuta la aplicación.",
        examples=["local"],
    )


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
