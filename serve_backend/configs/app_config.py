import logging
import os
from pathlib import Path
from typing import Any, ClassVar

from pydantic import Field
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict


class AppConfig(BaseSettings):
    """Application configuration class"""
    
    # Project root directory
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent
    ENV_FILE: ClassVar[Path] = BASE_DIR.parent / ".env"
    
    model_config = SettingsConfigDict(
        # Relative path of the .env file
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Read environment variables from the .env file
    DEBUG: bool = Field(..., description="Debug mode")
    FLASK_DEBUG: bool = Field(..., description="Flask debug mode")

    # ClickHouse database configuration
    CLICKHOUSE_HOST: str = Field(..., description="ClickHouse host")
    CLICKHOUSE_PORT_NATIVE: int = Field(..., description="ClickHouse native port")
    CLICKHOUSE_USER: str = Field(..., description="ClickHouse username")
    CLICKHOUSE_PASSWORD: str = Field(..., description="ClickHouse password")
    CLICKHOUSE_DATABASE: str = Field(..., description="ClickHouse database name")

    # Simulation configuration
    STK_LOCAL: bool = Field(..., description="Whether to use local STK")
    STK_PYTHON_LOCAL_EXE: str = Field(..., description="Local Python executable path for STK")
    STK_SCRIPT_LOCAL_PATH: str = Field(..., description="Local STK script path")
    STK_PYTHON_REMOTE_EXE: str = Field(..., description="Remote Python executable path for STK")
    STK_SCRIPT_REMOTE_PATH: str = Field(..., description="Remote STK script path")
    REPLACE_BASE: str = Field(..., description="Base path for simulation files")
    SSH_PASSWORD: str = Field(..., description="SSH password")
    SSH_USER: str = Field(..., description="SSH username")
    SSH_HOST: str = Field(..., description="SSH host")

    # Output directory
    OUTPUT_DIR: str = Field(..., description="Output directory path")

    # LLM configuration
    OLLAMA_URL: str = Field(..., description="OLLAMA URL")

    @property
    def CLICKHOUSE_URI(self) -> str:
        """Get ClickHouse connection URI"""
        return f"clickhouse://{self.CLICKHOUSE_USER}:{self.CLICKHOUSE_PASSWORD}@{self.CLICKHOUSE_HOST}:{self.CLICKHOUSE_PORT_NATIVE}/{self.CLICKHOUSE_DATABASE}"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


# Create global config instance
app_config = AppConfig()






