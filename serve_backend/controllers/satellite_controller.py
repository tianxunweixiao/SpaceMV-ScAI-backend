from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(prefix="/satellites", tags=["satellites"])


@router.get("")
async def get_satellites() -> List[Dict[str, Any]]:
    """
    Get all satellites from database
    
    Returns:
        List of satellite data
    """
    from services.satellite_service import SatelliteService
    service = SatelliteService()
    return await service.get_all_satellites()
