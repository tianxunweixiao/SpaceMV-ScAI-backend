from typing import TYPE_CHECKING
from configs import constellation_config
from models.engine import init_db

from .base import Extension

if TYPE_CHECKING:
    from constellation_app import ConstellationApp


class DatabaseExtension(Extension):
    """Database extension for initializing database connection"""
    
    def init_app(self, app: "ConstellationApp") -> None:
        """Initialize database engine and session"""
        init_db(
            database_uri=constellation_config.SQLALCHEMY_DATABASE_URI,
            pool_size=constellation_config.SQLALCHEMY_POOL_SIZE,
            max_overflow=constellation_config.SQLALCHEMY_MAX_OVERFLOW
        )


ext_database = DatabaseExtension()


