from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from openai import OpenAI
from typing import Optional, List, Dict, Any, Literal
import json

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
    stream: Optional[bool] = True
    stop: Optional[List[str]] = Field(default_factory=list)
    top_p: Optional[float] = 1
    max_tokens: Optional[int] = 3000
    temperature: Optional[float] = 1
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0

async def generate_stream(chat_request: ChatCompletionRequest):
    try:
        messages_dict = [msg.dict() for msg in chat_request.messages]
        response = client.chat.completions.create(
            model=chat_request.model,
            messages=messages_dict,
            stop=chat_request.stop,
            stream=True,
            stream_options={
                "include_usage": True,
                "continuous_usage_stats": True
            },
            top_p=chat_request.top_p,
            max_tokens=chat_request.max_tokens,
            temperature=chat_request.temperature,
            presence_penalty=chat_request.presence_penalty,
            frequency_penalty=chat_request.frequency_penalty
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta.content is not None:
                yield f"data: {json.dumps({'content': chunk.choices[0].delta.content})}\n\n"

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/v1/models")
async def list_models():
    return JSONResponse({
        "object": "list",
        "data": AVAILABLE_MODELS
    })

@app.post("/v1/chat/completions")
async def chat_completions(chat_request: ChatCompletionRequest):
    if chat_request.stream:
        return StreamingResponse(
            generate_stream(chat_request),
            media_type="text/event-stream"
        )
    else:
        try:
            messages_dict = [msg.dict() for msg in chat_request.messages]
            response = client.chat.completions.create(
                model=chat_request.model,
                messages=messages_dict,
                stop=chat_request.stop,
                stream=False,
                top_p=chat_request.top_p,
                max_tokens=chat_request.max_tokens,
                temperature=chat_request.temperature,
                presence_penalty=chat_request.presence_penalty,
                frequency_penalty=chat_request.frequency_penalty
            )
            return JSONResponse(response.dict())
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "DeepSeek Chat API is running. Use /v1/chat/completions for chat and /v1/models for available models."} 
