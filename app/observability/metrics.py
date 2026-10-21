"""Métricas Prometheus de las solicitudes HTTP (Golden Signals)."""

from time import perf_counter

from fastapi import Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from starlette.middleware.base import RequestResponseEndpoint
from starlette.routing import Match

from app.config import get_settings

# Buckets pensados para una API chica: la mayoría de las respuestas tarda pocos ms.
BUCKETS_LATENCIA = (0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0)

# Rutas que no se miden para no ensuciar el tráfico con el scraping y el healthcheck.
RUTAS_EXCLUIDAS = {"/metrics"}

http_requests_total = Counter(
    "http_requests_total",
    "Cantidad de solicitudes HTTP atendidas.",
    ["method", "route", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "Duración de las solicitudes HTTP en segundos.",
    ["method", "route"],
    buckets=BUCKETS_LATENCIA,
)

http_requests_in_progress = Gauge(
    "http_requests_in_progress",
    "Solicitudes HTTP que se están procesando en este momento.",
    ["method"],
)

app_info = Gauge(
    "app_info",
    "Información de la versión desplegada (siempre vale 1).",
    ["servicio", "version", "entorno"],
)


def registrar_info_app() -> None:
    """Publica la versión y el entorno para poder filtrar por deploy en Grafana."""
    settings = get_settings()
    app_info.labels(
        servicio=settings.app_nombre,
        version=settings.app_version,
        entorno=settings.entorno,
    ).set(1)


def resolver_ruta(request: Request) -> str:
    """Devuelve la plantilla de la ruta (`/incidentes/{incidente_id}`).

    Usar la plantilla y no la URL real evita crear una serie por cada UUID.
    Las rutas que no existen se agrupan en `sin_ruta`.
    """
    for ruta in request.app.router.routes:
        coincidencia, _ = ruta.matches(request.scope)
        if coincidencia == Match.FULL:
            return getattr(ruta, "path", request.url.path)
    return "sin_ruta"


async def registrar_metricas(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """Mide tráfico, errores y latencia de cada solicitud."""
    if request.url.path in RUTAS_EXCLUIDAS:
        return await call_next(request)

    metodo = request.method
    ruta = resolver_ruta(request)
    status_code = 500
    inicio = perf_counter()
    http_requests_in_progress.labels(method=metodo).inc()

    try:
        response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        http_request_duration_seconds.labels(method=metodo, route=ruta).observe(
            perf_counter() - inicio
        )
        http_requests_total.labels(
            method=metodo,
            route=ruta,
            status_code=str(status_code),
        ).inc()
        http_requests_in_progress.labels(method=metodo).dec()


def exponer_metricas() -> Response:
    """Serializa todas las métricas en el formato de texto de Prometheus."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
