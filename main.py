from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import OpenAI
from typing import Optional, List, Dict, Any
import json

app = FastAPI()

# Initialize OpenAI client
client = OpenAI(
    api_key="QsN6UGMS.pj7sNnMC4IW0dpF63Lae8BqMNhHI7D4s",
    base_url="https://inference.baseten.co/v1"
)

class ChatRequest(BaseModel):
    messages: List[Dict[str, str]]
    stop: Optional[List[str]] = []
    top_p: Optional[float] = 1
    max_tokens: Optional[int] = 3000
    temperature: Optional[float] = 1
    presence_penalty: Optional[float] = 0
    frequency_penalty: Optional[float] = 0

async def generate_stream(chat_request: ChatRequest):
    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1-0528",
            messages=chat_request.messages,
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

@app.post("/api/chat")
async def chat_endpoint(chat_request: ChatRequest):
    return StreamingResponse(
        generate_stream(chat_request),
        media_type="text/event-stream"
    )

@app.get("/")
async def root():
    return {"message": "DeepSeek Chat API is running"} 
