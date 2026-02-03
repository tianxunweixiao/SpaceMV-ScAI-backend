from typing import Dict, Any
import logging
import json
import httpx
import asyncio
from configs.app_config import app_config

class LLMService:
    """Service for LLM-related operations"""
    
 
    def chat_ollama(self, request_data: Dict[str, Any]):
        """
        Process LLM chat request (ollama API)
        
        Args:
            request_data: LLM request data containing model, inputs, parameters
            
        Returns:
            Async generator function for streaming LLM output
        """
        body = request_data
        
        model_name = body['model']
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        input_question = body['inputs']
        transfer_body = {
               "model": f"{model_name}",
               "messages": [
                    {
                      "role": "user",
                      "content": input_question
                    }
                          ]
               }
        body_trans = json.dumps(transfer_body)
        ollama_url = app_config.OLLAMA_URL
        
        async def iter_stream():
            buffer = b""
            skip_next = False
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream("POST", ollama_url, headers=headers, content=body_trans.encode("utf-8")) as resp:
                    try:
                        async for chunk in resp.aiter_bytes():
                            if not chunk:
                                continue
                            buffer += chunk
                            lines = buffer.split(b"\n")
                            buffer = lines[-1]
                            
                            for line in lines[:-1]:
                                try:
                                    line_str = line.decode("utf-8")
                                    if line_str.startswith("{"):
                                        data_json = json.loads(line_str)
                                        done_sigh = data_json.get("done", {})
                                        if not done_sigh :
                                            text = data_json.get("message", {}).get("content", "")
                                            if skip_next:
                                                skip_next = False
                                                continue
                                            if text in ("</think>", "</think>"):
                                                skip_next = True
                                            if '\n\n' in text:
                                                text = text.replace('\n\n', '\n')
                                        else:
                                            text = '<｜end▁of▁sentence｜>'
                                        
                                        transfer_json = {"token": {"text": text}}
                                        new_line_str = "data: " + json.dumps(transfer_json, ensure_ascii=False)
                                        line = new_line_str.encode("utf-8")
                                except Exception:
                                    pass
                                yield line + b"\n"
                    except asyncio.CancelledError:
                        await resp.aclose()
                        await client.aclose()
                        raise
        
        return iter_stream
