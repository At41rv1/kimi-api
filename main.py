from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional, List, Dict, Any, Literal
import json
import asyncio

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize OpenAI client
client = OpenAI(
    api_key="QsN6UGMS.pj7sNnMC4IW0dpF63Lae8BqMNhHI7D4s",
    base_url="https://inference.baseten.co/v1"
)

AVAILABLE_MODELS = [
    {
        "id": "deepseek-ai/DeepSeek-R1-0528",
        "object": "model",
        "created": 1706745600,
        "owned_by": "deepseek-ai",
        "permission": [],
        "root": "deepseek-ai/DeepSeek-R1-0528",
        "parent": None,
    }
]

class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str

class ChatCompletionRequest(BaseModel):
    model: str
    messages: List[ChatMessage]
    stream: Optional[bool] = False
    stop: Optional[List[str]] = Field(default_factory=list)
    top_p: Optional[float] = 1
    max_tokens: Optional[int] = 3000
    temperature: Optional[float] = 1
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0

class ErrorResponse(BaseModel):
    error: str

@app.get("/v1/models")
async def list_models():
    try:
        return {
            "object": "list",
            "data": AVAILABLE_MODELS
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Failed to list models: {str(e)}"}
        )

@app.post("/v1/chat/completions")
async def chat_completions(chat_request: ChatCompletionRequest):
    try:
        messages_dict = [{"role": msg.role, "content": msg.content} for msg in chat_request.messages]
        
        response = client.chat.completions.create(
            model=chat_request.model,
            messages=messages_dict,
            stop=chat_request.stop,
            stream=False,  # Force non-streaming for Vercel compatibility
            top_p=chat_request.top_p,
            max_tokens=chat_request.max_tokens,
            temperature=chat_request.temperature,
            presence_penalty=chat_request.presence_penalty,
            frequency_penalty=chat_request.frequency_penalty
        )
        
        # Convert the response to a dictionary and return
        response_dict = {
            "id": response.id,
            "object": "chat.completion",
            "created": response.created,
            "model": response.model,
            "choices": [{
                "index": choice.index,
                "message": {
                    "role": choice.message.role,
                    "content": choice.message.content
                },
                "finish_reason": choice.finish_reason
            } for choice in response.choices],
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        
        return JSONResponse(content=response_dict)

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Chat completion failed: {str(e)}"}
        )

@app.get("/")
async def root():
    return {
        "status": "healthy",
        "version": "1.0",
        "endpoints": {
            "models": "/v1/models",
            "chat": "/v1/chat/completions"
        }
    } 
