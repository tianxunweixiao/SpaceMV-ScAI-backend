from fastapi import FastAPI
from .base import Extension
from controllers import (
    satellite_router,
    constellation_router,
    sensor_router,
    simulation_router,
    llm_router
)


class RoutersExtension(Extension):
    """Extension for registering API routers"""
    
    def is_enabled(self) -> bool:
        """Check if router extension is enabled"""
        return True
    
    def init_app(self, app: FastAPI) -> None:
        """
        Initialize routers extension
        
        Args:
            app: FastAPI application instance
        """
        # Register all routers
        app.include_router(satellite_router)
        app.include_router(constellation_router)
        app.include_router(sensor_router)
        app.include_router(simulation_router)
        app.include_router(llm_router)


# Create router extension instance
ext_routers = RoutersExtension()
