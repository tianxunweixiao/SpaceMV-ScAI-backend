from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Dict, Any
import json

router = APIRouter(tags=["constellations"])


@router.get("/constellations")
async def get_constellations() -> List[Dict[str, Any]]:
    """
    Get all constellations from database
    
    Returns:
        List of constellation data
    """
    from services.constellation_service import ConstellationService
    service = ConstellationService()
    return await service.get_all_constellations()


@router.get("/constellations_find/{constellation_id}")
async def find_constellation(constellation_id: str) -> Dict[str, Any]:
    """
    Find constellation by ID(Norad ID)
    
    Args:
        constellation_id: Constellation identifier
        
    Returns:
        Dict containing constellation data
    """
    from services.constellation_service import ConstellationService
    service = ConstellationService()
    result = await service.find_constellation(constellation_id)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.post("/upload_constellation")
async def upload_constellation(file: UploadFile = File(...), constellation_type: str = Form(...)) -> Dict[str, Any]:
    """
    Upload constellation data to database
    
    Args:
        file: JSON file containing constellation data
        constellation_type: Constellation type
        
    Returns:
        Dict containing upload result
    """
    from services.constellation_service import ConstellationService
    service = ConstellationService()
    
    content = await file.read()
    text = content.decode('utf-8')
    data = json.loads(text)
    
    result = await service.upload_constellation(data, constellation_type)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.delete("/constellations/{con_id}")
async def delete_constellation(con_id: str) -> Dict[str, Any]:
    """
    Delete constellation by ID
    
    Args:
        con_id: Constellation identifier
        
    Returns:
        Dict containing deletion result
    """
    from services.constellation_service import ConstellationService
    service = ConstellationService()
    
    result = await service.delete_constellation(con_id)
    
    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])
    
    return result
