import os
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import FileResponse, HTMLResponse, StreamingResponse
import asyncio
from typing import AsyncGenerator
from config import load_config_from_json
from main import get_message, NAME
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


app = FastAPI()

SETTINGS = load_config_from_json("config.json")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="static")

@app.get("/", response_class=HTMLResponse)
def start_web(request: Request):
    return templates.TemplateResponse("index.html", {
        "request": request,
        "NAME": NAME
    })

@app.websocket("/ws/chat")
async def websocket_chat(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data: str = await websocket.receive_text()
            def send(val: str) -> None:
                loop = asyncio.get_event_loop()
                loop.call_soon_threadsafe(
                    asyncio.create_task,
                    websocket.send_text(val)
                )
            get_message(data, send)
            await websocket.send_text("[[END]]")
    except Exception as e:
        print("WebSocket closed:", e)


@app.get("/favicon.ico")
async def favicon():
    file_path = os.path.join("static", "assets", "theam.svg") 
    return FileResponse(file_path)