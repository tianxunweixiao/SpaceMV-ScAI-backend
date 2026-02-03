import logging
from pathlib import Path
from typing import Any, ClassVar
from pydantic.fields import FieldInfo
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict
from .middleware import MiddlewareConfig


class ConstellationConfig(
    # Middleware configs
    MiddlewareConfig,
):  
    # Project root directory
    BASE_DIR: ClassVar[Path] = Path(__file__).resolve().parent.parent
    ENV_FILE: ClassVar[Path] = BASE_DIR.parent / ".env"

    model_config = SettingsConfigDict(
        # read from dotenv format config file
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        # ignore extra attributes
        extra="ignore",
    )

    # Before adding any config,
    # please consider to arrange it in the proper config group of existed or added
    # for better readability and maintainability.

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
