from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
import httpx
import json

app = FastAPI()

API_KEY = "4a6pMDyn.2Gm8ZhMYbojhpxAtgjMWFFxQ8Tbphxhf"
BASE_URL = "https://inference.baseten.co/v1"

# User-friendly model names mapped to real API identifiers
MODEL_MAPPING = {
    "Kimi-K2": "moonshotai/Kimi-K2-Instruct",
    "DeepSeek-R1-Think": "deepseek-ai/DeepSeek-R1",
    "DeepSeek-R1-0528-Think": "deepseek-ai/DeepSeek-R1-0528",
    "DeepSeek-V3": "deepseek-ai/DeepSeek-V3-0324",
    "Llama4-Maverick-17B-lnstruct": "meta-llama/Llama-4-Maverick-17B-128E-Instruct",
    "Llama4-Scout-17B-16E-lnstruct": "meta-llama/Llama-4-Scout-17B-16E-Instruct"
}

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <html>
    <head>
        <title>At41rv A7 API</title>
        <style>
            body { font-family: Arial; padding: 30px; background: #fff; color: #111; }
            h1 { color: #1e40af; }
            code, pre { background: #f3f3f3; padding: 8px; border-radius: 5px; }
        </style>
    </head>
    <body>
        <h1>🚀 At41rv A7 AI API Docs</h1>
        <p>📌 Base URL: <code>https://a7-at41rv.vercel.app</code></p>
        <h2>📍 Available Models:</h2>
        <ul>
            <li><code>Kimi-K2</code></li>
            <li><code>.</code></li>
            <li><code>DeepSeek-R1-Think</code></li>
            <li><code>.</code></li>
            <li><code>DeepSeek-R1-0528-Think</code></li>
            <li><code>.</code></li>
            <li><code>DeepSeek-V3</code></li>
            <li><code>.</code></li>
            <li><code>Llama4-Maverick-17B-lnstruct</code></li>
            <li><code>.</code></li>
            <li><code>Llama4-Scout-17B-16E-lnstruct</code></li>
            <li><code>.</code></li>
        </ul>
        <h2>🧠 Endpoints:</h2>
        <ul>
            <li><code>GET /v1/models</code> — List available models</li>
            <li><code>.</code></li>
            <li><code>POST /v1/chat/completions</code> — Chat with model (set <code>"stream": true</code> to enable streaming)</li>
        </ul>
        <h2>💬 Example Request:</h2>
            <li><code>.</code></li>
        <pre>{
  "model": "Kimi-K2",
  "messages": [{"role": "user", "content": "Hello!"}],
  "stream": false
}</pre>
    </body>
    </html>
    """

@app.get("/v1/models")
async def list_models():
    return {
        "object": "list",
        "data": [{"id": k, "object": "model", "owned_by": "you"} for k in MODEL_MAPPING.keys()]
    }

@app.post("/v1/chat/completions")
async def chat_handler(request: Request):
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
        if body.get("stream", False):
            async with client.stream("POST", f"{BASE_URL}/chat/completions", headers=headers, json=body) as resp:
                async def event_stream():
                    async for line in resp.aiter_lines():
                        if line.strip():
                            yield f"data: {line}\n\n"
                return StreamingResponse(event_stream(), media_type="text/event-stream")
        else:
            resp = await client.post(f"{BASE_URL}/chat/completions", headers=headers, json=body)
            return JSONResponse(status_code=resp.status_code, content=resp.json())
