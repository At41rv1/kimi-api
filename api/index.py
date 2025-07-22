from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import httpx
import json

app = FastAPI()

API_KEY = "4a6pMDyn.2Gm8ZhMYbojhpxAtgjMWFFxQ8Tbphxhf"
BASE_URL = "https://inference.baseten.co/v1"
REAL_MODEL = "moonshotai/Kimi-K2-Instruct"
MODEL_NAME = "Kimi-AI"

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>Kimi API</title>
            <style>
                body { font-family: sans-serif; padding: 30px; background: #f9f9f9; }
                h1 { color: #1d4ed8; }
                code { background: #eee; padding: 4px 6px; border-radius: 4px; }
                pre { background: #eee; padding: 10px; border-radius: 6px; }
            </style>
        </head>
        <body>
            <h1>✅ API IS ON - USE UNLIMITED</h1>
            <p>This is a custom proxy to Kimi-AI running on Vercel.</p>

            <h2>🔗 Endpoints</h2>
            <ul>
                <li><code>GET /v1/models</code> — Returns available model</li>
                <li><code>POST /v1/chat/completions</code> — Sends a chat message</li>
            </ul>

            <h2>📥 Example Request (POST /v1/chat/completions) -- By At41rv--</h2>
            <pre>{
  "model": "Kimi-AI",
  "messages": [
    {"role": "user", "content": "Who are you?"}
  ],
  "stream": false
}</pre>

            <h2>📤 Example Response</h2>
            <pre>{
  "id": "...",
  "object": "chat.completion",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I am Kimi, your intelligent assistant!"
      },
      ...
    }
  ]
}</pre>

            <p>Need help? Contact the creator or test it with <code>curl</code> or Python.</p>
        </body>
    </html>
    """

@app.get("/v1/models")
async def models():
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
async def chat(request: Request):
    body = await request.json()
    body["model"] = REAL_MODEL

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        if body.get("stream"):
            async with client.stream(
                "POST", f"{BASE_URL}/chat/completions", headers=headers, json=body
            ) as r:
                async def streamer():
                    async for line in r.aiter_lines():
                        if line.strip():
                            yield f"data: {line}\n\n"
                return StreamingResponse(streamer(), media_type="text/event-stream")
        else:
            r = await client.post(f"{BASE_URL}/chat/completions", headers=headers, json=body)
            return JSONResponse(status_code=r.status_code, content=r.json())
