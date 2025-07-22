from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse, PlainTextResponse
import httpx
import asyncio

app = FastAPI()

# Hidden actual backend
API_KEY = "4a6pMDyn.2Gm8ZhMYbojhpxAtgjMWFFxQ8Tbphxhf"
BASE_URL = "https://inference.baseten.co/v1"
MODEL_NAME = "Kimi-AI"  # Public-facing name (can be anything you want)

@app.get("/", response_class=PlainTextResponse)
async def root():
    return "API IS ON - USE UNLIMITED"

@app.get("/v1/models")
async def get_models():
    return {
        "object": "list",
        "data": [
            {
                "id": MODEL_NAME,
                "object": "model",
                "owned_by": "you"
            }
        ]
    }

@app.post("/v1/chat/completions")
async def chat_proxy(request: Request):
    body = await request.json()
    
    # Override model to hidden real model name
    body["model"] = "moonshotai/Kimi-K2-Instruct"
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        if body.get("stream"):
            # Handle streaming
            async with client.stream(
                "POST",
                f"{BASE_URL}/chat/completions",
                json=body,
                headers=headers
            ) as resp:
                async def streamer():
                    async for line in resp.aiter_lines():
                        if line.strip():
                            yield f"data: {line}\n\n"
                return StreamingResponse(streamer(), media_type="text/event-stream")
        else:
            # Handle non-streaming
            resp = await client.post(
                f"{BASE_URL}/chat/completions",
                json=body,
                headers=headers
            )
            return JSONResponse(status_code=resp.status_code, content=resp.json())
