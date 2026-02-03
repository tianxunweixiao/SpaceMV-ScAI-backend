from typing import Any, Optional

from pydantic import Field, NonNegativeInt, computed_field
from pydantic_settings import BaseSettings


class ClickhouseConfig(BaseSettings):
    """
        Configuration settings for Clickhouse connection
    """

    # ClickHouse connection parameters
    CLICKHOUSE_HOST: str = Field(
        description="Clickhouse server host",
        default="localhost",
        alias="CLICKHOUSE_HOST",
    )

    CLICKHOUSE_PORT_HTTP: int = Field(
        description="Clickhouse server port",
        default=8123,
        alias="CLICKHOUSE_PORT_HTTP",
    )

    CLICKHOUSE_USER: str = Field(
        description="Clickhouse username",
        default="default",
        alias="CLICKHOUSE_USER",
    )

    CLICKHOUSE_PASSWORD: str = Field(
        description="Clickhouse password",
        default="",
        alias="CLICKHOUSE_PASSWORD",
    )

    CLICKHOUSE_DATABASE: str = Field(
        description="Clickhouse database name",
        default="default",
        alias="CLICKHOUSE_DATABASE",
    )

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        """Build ClickHouse connection URI from individual parameters"""
        return f"clickhouse://{self.CLICKHOUSE_USER}:{self.CLICKHOUSE_PASSWORD}@{self.CLICKHOUSE_HOST}:{self.CLICKHOUSE_PORT_HTTP}/{self.CLICKHOUSE_DATABASE}"

    SQLALCHEMY_TRACK_MODIFICATIONS: bool = Field(
        description="Enable track for modification",
        default=False,
    )

    SQLALCHEMY_POOL_SIZE: NonNegativeInt = Field(
        description="Maximum number of database connections in the pool.",
        default=30,
    )

    SQLALCHEMY_MAX_OVERFLOW: NonNegativeInt = Field(
        description="Maximum number of connections that can be created beyond the pool_size.",
        default=10,
    )

    @computed_field  # type: ignore[misc]
    @property
    def SQLALCHEMY_ENGINE_OPTIONS(self) -> dict[str, Any]:
        return {
            "pool_size": self.SQLALCHEMY_POOL_SIZE,
            "max_overflow": self.SQLALCHEMY_MAX_OVERFLOW
        }

