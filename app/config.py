"""Configuración de la aplicación, leída desde variables de entorno."""

from datetime import date
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Settings de la app.

    Cada atributo se puede sobreescribir con una variable de entorno del mismo
    nombre en mayúsculas. Nunca hardcodear valores acá: el contenedor tiene que
    poder correr en local, en CI y en producción cambiando solo el entorno.
    """

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_nombre: str = "dias-sin-incidentes"
    app_version: str = "0.1.0"
    entorno: str = "local"

    # Desde cuándo contamos si todavía no hubo ningún incidente registrado.
    fecha_inicio_operaciones: date = date(2026, 9, 1)

    # Interruptor del endpoint de falla controlada. Apagado por defecto.
    chaos_enabled: bool = False


@lru_cache
def get_settings() -> Settings:
    """Devuelve las settings cacheadas (se leen del entorno una sola vez)."""
    return Settings()
