"""Endpoint para generar una falla controlada."""

from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/chaos", tags=["caos"])


@router.post(
    "/boom",
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    summary="Generar una falla controlada",
    description=(
        "Genera intencionalmente una respuesta HTTP 500 "
        "para probar los logs, las métricas y las alertas."
    ),
)
def provocar_error() -> None:
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Falla controlada para validar la observabilidad",
    )
