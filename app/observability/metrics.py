"""Métricas Prometheus de las solicitudes HTTP."""

from time import perf_counter

from fastapi import APIRouter, Request, Response
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest
from starlette.middleware.base import RequestResponseEndpoint

REQUESTS = Counter(
    "http_requests_total",
    "Cantidad de solicitudes HTTP.",
    ["method", "path", "status"],
)

LATENCIA = Histogram(
    "http_request_duration_seconds",
    "Duración de las solicitudes HTTP en segundos.",
    ["method", "path"],
)

router = APIRouter(tags=["sistema"])


@router.get("/metrics", include_in_schema=False)
def metricas() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


async def registrar_metricas(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """Cuenta cada solicitud y mide su duración."""
    inicio = perf_counter()
    status = 500

    try:
        response = await call_next(request)
        status = response.status_code
        return response
    finally:
        ruta = request.scope.get("route")
        path = ruta.path if ruta else "sin_ruta"

        if path != "/metrics":
            LATENCIA.labels(request.method, path).observe(perf_counter() - inicio)
            REQUESTS.labels(request.method, path, str(status)).inc()
