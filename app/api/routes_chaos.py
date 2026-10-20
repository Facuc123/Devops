"""Endpoint para generar una falla controlada."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.config import Settings, get_settings

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
def provocar_error(
    settings: Annotated[Settings, Depends(get_settings)],
) -> None:
    if not settings.chaos_enabled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint no disponible",
        )

    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Falla controlada para validar la observabilidad",
    )
