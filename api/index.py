from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import httpx
import json

app = FastAPI()

API_KEY = "4a6pMDyn.2Gm8ZhMYbojhpxAtgjMWFFxQ8Tbphxhf"
BASE_URL = "https://inference.baseten.co/v1"

# Mapping of display names (used by users) to real model names (sent to base URL)
MODEL_MAPPING = {
    "Kimi-K2": "moonshotai/Kimi-K2-Instruct",
    "DeepSeek-R1": "deepseek-ai/DeepSeek-R1",
    "DeepSeek-R1-0528": "deepseek-ai/DeepSeek-R1-0528",
    "DeepSeek-V3": "deepseek-ai/DeepSeek-V3-0324",
    "Llama4-Maverick-17B-lnstruct": "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
    "Llama4-Scout-17B-16E-lnstruct": "meta-llama/Llama-4-Scout-17B-16E-Instruct",
}

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
        <head>
            <title>A7 API</title>
            <style>
                body { font-family: 'Segoe UI', sans-serif; padding: 30px; background: #fdfdfd; color: #222; }
                h1 { color: #1e40af; }
                code { background: #f1f1f1; padding: 4px 6px; border-radius: 4px; }
                pre { background: #f1f1f1; padding: 10px; border-radius: 6px; overflow: auto; }
                .box { background: #e0ecff; border-left: 4px solid #1e40af; padding: 1em; margin-bottom: 1em; }
            </style>
        </head>
        <body>
            <h1>🚀 A7 AI API Docs</h1>
               <ul>
                <li><code>BY At41rv</code></li>               
            </ul>
            <div class="box">
                <strong>Status:</strong> <span style="color: green;">✅ API IS ON - USE UNLIMITED</span>
            </div>

            <h2>📌 Available Models</h2>
            <ul>
                <li><code>Kimi-K2</code></li>
                <li><code>DeepSeek-R1</code></li>
                <li><code>DeepSeek-R1-0528</code></li>
                <li><code>DeepSeek-V3</code></li>
                <li><code>Llama4-Maverick-17B-lnstruct</code></li>
                <li><code>Llama4-Scout-17B-16E-lnstruct</code></li>
            </ul>

            <h2>🔗 Endpoints</h2>
            <ul>
                <li><code>GET /v1/models</code> — List available models</li>
                <li><code>POST /v1/chat/completions</code> — Send chat request</li>
            </ul>

            <h2>📤 Example Request</h2>
            <pre>{
  "model": "Kimi-K2",
  "messages": [
    {"role": "user", "content": "Hello, who are you?"}
  ],
  "stream": false
}</pre>

            <h2>📥 Example Response</h2>
            <pre>{
  "id": "chatcmpl-xyz",
  "object": "chat.completion",
  "choices": [
    {
      "message": {
        "role": "assistant",
        "content": "I am Kimi, your assistant!"
      }
    }
  ]
}</pre>
        </body>
    </html>
    """

@app.get("/v1/models")
async def models():
    return {
        "object": "list",
        "data": [
            {"id": display, "object": "model", "owned_by": "you"}
            for display in MODEL_MAPPING.keys()
        ]
    }

@app.post("/v1/chat/completions")
async def chat(request: Request):
    body = await request.json()
    display_model = body.get("model")
    real_model = MODEL_MAPPING.get(display_model)

    if not real_model:
        return JSONResponse(status_code=400, content={"error": "Unknown model name"})

    body["model"] = real_model

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        if body.get("stream"):
            async with client.stream("POST", f"{BASE_URL}/chat/completions", headers=headers, json=body) as r:
                async def streamer():
                    async for line in r.aiter_lines():
                        if line.strip():
                            yield f"data: {line}\n\n"
                return StreamingResponse(streamer(), media_type="text/event-stream")
        else:
            r = await client.post(f"{BASE_URL}/chat/completions", headers=headers, json=body)
            return JSONResponse(status_code=r.status_code, content=r.json())
