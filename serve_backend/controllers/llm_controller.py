from fastapi import APIRouter
from typing import Dict, Any
from pydantic import BaseModel
from fastapi.responses import StreamingResponse

router = APIRouter(tags=["llm"])

class LLMRequest(BaseModel):
    """Model for LLM request"""
    model: str
    inputs: str
    context: Dict[str, Any] = {}

'''
@router.post("/generate_stream")
async def llm_chat(data: LLMRequest) -> Dict[str, Any]:
    """
    Process LLM chat request(Ascend mindIE)
    
    Args:
        data: LLM request data
        
    Returns:
        Dict containing LLM response
    """
    from services.llm_service import LLMService
    service = LLMService()
    return await service.chat(data.dict())
'''

@router.post("/generate_stream_ollama")
async def llm_chat_ollama(data: LLMRequest) -> StreamingResponse:
    """
    Process LLM chat request with ollama
    
    Args:
        data: LLM request data
        
    Returns:
        StreamingResponse with LLM output
    """
    from services.llm_service import LLMService
    service = LLMService()
    return StreamingResponse(service.chat_ollama(data.dict())(), media_type="text/plain")
