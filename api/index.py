from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
import httpx
import os
import asyncio

app = FastAPI()

API_KEY = "4a6pMDyn.2Gm8ZhMYbojhpxAtgjMWFFxQ8Tbphxhf"
BASE_URL = "https://inference.baseten.co/v1"
MODEL_NAME = "moonshotai/Kimi-K2-Instruct"

@app.post("/chat")
async def proxy_chat(request: Request):
    body = await request.json()
    
    # Force model name override (hides it from users)
    body["model"] = MODEL_NAME
    
    # Forward request to original API with real base_url
    async with httpx.AsyncClient(timeout=60.0) as client:
        async with client.stream(
            "POST",
            f"{BASE_URL}/chat/completions",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json=body,
        ) as response:
            
            async def stream_generator():
                async for line in response.aiter_lines():
                    if line.strip():
                        yield line + "\n"
            
            return StreamingResponse(stream_generator(), media_type="text/event-stream")
