from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
import asyncio
from typing import AsyncGenerator
from config import load_config_from_json
from main import get_message
from fastapi.staticfiles import StaticFiles


app = FastAPI()

app = FastAPI()
SETTINGS = load_config_from_json("config.json")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def start_web():
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return html_content

@app.post("/chat")
async def chat_stream(request: Request):
    data = await request.json()
    prompt = data.get("message", "")
    queue = asyncio.Queue()
    loop = asyncio.get_event_loop()
    def channel(token: str):
        asyncio.run_coroutine_threadsafe(queue.put(token), loop)
    task = loop.run_in_executor(None, get_message, prompt, channel)
    async def event_generator() -> AsyncGenerator[str, None]:
        while True:
            if task.done() and queue.empty():
                break
            try:
                token = await asyncio.wait_for(queue.get(), timeout=0.1)
                yield f"data: {token}\n\n"
            except asyncio.TimeoutError:
                continue
        await asyncio.wrap_future(task)
    return StreamingResponse(event_generator(), media_type="text/event-stream")