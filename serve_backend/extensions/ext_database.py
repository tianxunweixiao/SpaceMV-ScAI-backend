import asyncio
from typing import TYPE_CHECKING
from aioch import Client

from configs import app_config
from .base import Extension

if TYPE_CHECKING:
    from constellation_app import ConstellationApp


class ClickHousePool:
    """ClickHouse connection pool for async operations"""
    
    def __init__(self, size: int = 5):
        self.queue = asyncio.Queue()
        self.size = size
        self._clients = []
    
    async def init(self):
        """Initialize the connection pool"""
        for _ in range(self.size):
            client = Client(
                host=app_config.CLICKHOUSE_HOST,
                port=app_config.CLICKHOUSE_PORT_NATIVE,
                user=app_config.CLICKHOUSE_USER,
                password=app_config.CLICKHOUSE_PASSWORD,
                database=app_config.CLICKHOUSE_DATABASE
            )
            await self.queue.put(client)
            self._clients.append(client)
    
    async def acquire(self):
        """Acquire a client from the pool"""
        return await self.queue.get()
    
    async def release(self, client):
        """Release a client back to the pool"""
        await self.queue.put(client)
    
    async def close(self):
        """Close all connections in the pool"""
        while not self.queue.empty():
            client = await self.queue.get()
            close = getattr(client, "close", None)
            if callable(close):
                await close()


# Global pool instance
pool = ClickHousePool()


class DatabaseExtension(Extension):
    """Database extension for initializing ClickHouse connection pool"""
    
    def init_app(self, app: "ConstellationApp") -> None:
        """Initialize database connection pool"""
        # Store pool in app state for access in controllers
        app.state.clickhouse_pool = pool
        
        # Add lifespan handler to manage pool lifecycle
        @app.on_event("startup")
        async def startup():
            await pool.init()
            if app_config.DEBUG:
                import logging
                logging.info("ClickHouse connection pool initialized")
        
        @app.on_event("shutdown")
        async def shutdown():
            await pool.close()
            if app_config.DEBUG:
                import logging
                logging.info("ClickHouse connection pool closed")


ext_database = DatabaseExtension()
