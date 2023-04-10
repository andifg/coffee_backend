"""Settings of the webservice."""
from __future__ import annotations

from pydantic import BaseSettings


class Settings(BaseSettings):
    """The settings used within the service

    Args:
        BaseSettings: The pydantic base settings that are automatically picking
            up environment variables and are matching those against the settings
            down below case insensitively.
    """

    build_version: str = "0.0.0"

    host: str = "0.0.0.0"
    port: int = 80

    log_level: str = "info"

    mongodb_database: str = "coffee_backend"
    mongodb_coffee_collection: str = "coffee"


settings = Settings()
