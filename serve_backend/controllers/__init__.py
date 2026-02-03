from .satellite_controller import router as satellite_router
from .constellation_controller import router as constellation_router
from .sensor_controller import router as sensor_router
from .simulation_controller import router as simulation_router
from .llm_controller import router as llm_router

__all__ = [
    "satellite_router",
    "constellation_router",
    "sensor_router",
    "simulation_router",
    "llm_router"
]
