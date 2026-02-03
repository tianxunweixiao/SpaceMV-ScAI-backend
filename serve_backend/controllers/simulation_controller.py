from fastapi import APIRouter
from typing import Dict, Any
from pydantic import BaseModel

router = APIRouter(tags=["simulation"])


class SimulationRequest(BaseModel):
    """Model for simulation request"""
    level: int  # Simulation Level 0 - Single Satellite 1 - Constellation
    ID: str  # Single Star/Constellation ID
    start_time: str   # Simulation Start Time(UTC)  eg:20130912032513
    end_time: str  # Simulation End Time(UTC)  eg:20130915032619
    interval: str  # Simulation Step Size(s)
    area_data: str  # Polygon data(Longitude first, Latitude second) eg:123 34|134 41|127 37
    line_data: str   # Line data(Longitude first, Latitude second) eg:123 31|124 31
    point_data: str  # Point Data (Longitude first, Latitude second) eg:123 41
    algorithm_type: int  # Algorithm Type - STK


@router.post("/simulation_stream")
async def simulation_stream(data: SimulationRequest):
    """
    Execute simulation and stream results
    
    Args:
        data: Simulation request data
        
    Returns:
        Streaming response with simulation results
    """
    from services.simulation_service import SimulationService
    service = SimulationService()
    return await service.simulation_stream(data.dict())

