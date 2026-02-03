import os
from typing import Any, Literal, Optional
from urllib.parse import parse_qsl, quote_plus

from pydantic import Field, NonNegativeFloat, NonNegativeInt, PositiveFloat, PositiveInt, computed_field
from pydantic_settings import BaseSettings

from .cache.redis_config import RedisConfig
from .storage.clickhouse_config import ClickhouseConfig


class DeploymentConfig(BaseSettings):
    """
    Configuration settings for application deployment
    """

    DEBUG: bool = Field(
        description="Enable debug mode for additional logging and development features",
        default=False,
    )


class MiddlewareConfig(
    # place the configs in alphabet order
    DeploymentConfig,
    ClickhouseConfig,
    RedisConfig
):
    pass
