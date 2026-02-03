from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any

router = APIRouter(tags=["sensors"])


class sensor_setting(BaseModel):
    """Model for sensor setting"""
    satellite_id: str
    sensor_type: int
    hha: float
    vha: float
    max_pa: float
    min_pa: float
    max_aa: float
    min_aa: float
    roll: float
    pitch: float
    yaw: float
    Mobility: float
    Band: int
    # 传感器参数： 水平半张角、垂直半张角、最大俯仰角、最小俯仰角、最大方位角、最小方位角、滚动角、俯仰角、偏航角、机动能力、谱段/波段
    # Sensor Parameters: Horizontal Half-Angle, Vertical Half-Angle, Maximum Pitch Angle, Minimum Pitch Angle, Maximum Azimuth Angle, Minimum Azimuth Angle, Roll Angle, Pitch Angle, Yaw Angle, Maneuverability, Spectrum Band/Frequency Band

@router.post("/sensors")
async def modify_sensor(sensor: sensor_setting) -> Dict[str, Any]:
    """
    Modify sensor parameters
    
    Args:
        sensor: Sensor setting data
        
    Returns:
        Dict containing update result
    """
    from services.satellite_service import SatelliteService
    service = SatelliteService()
    result = await service.update_sensor(
        satellite_id=sensor.satellite_id,
        sensor_type=sensor.sensor_type,
        hha=sensor.hha,
        vha=sensor.vha,
        max_pa=sensor.max_pa,
        min_pa=sensor.min_pa,
        max_aa=sensor.max_aa,
        min_aa=sensor.min_aa,
        roll=sensor.roll,
        pitch=sensor.pitch,
        yaw=sensor.yaw,
        Mobility=sensor.Mobility,
        Band=sensor.Band
    )
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.get("/sensors_find/{satellite_id}")
async def find_sensor(satellite_id: str) -> Dict[str, Any]:
    """
    Find sensor parameters by satellite ID
    
    Args:
        satellite_id: Satellite identifier
        
    Returns:
        Dict containing sensor data
    """
    from services.satellite_service import SatelliteService
    service = SatelliteService()
    result = await service.find_sensors(satellite_id)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result
