import logging
import os
from typing import Awaitable, Callable, Iterable, List, Optional
from fastapi import FastAPI, Request, WebSocket
from fastapi.responses import FileResponse, HTMLResponse
from openai import AsyncOpenAI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from openai.types.chat import ChatCompletionMessageParam  

from config import load_config_from_json
from main import NAME

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
    chat: Iterable[ChatCompletionMessageParam] = []
    chat.append(
        {"role": "system", "content": SETTINGS.ROLE},
    )
    try:
        async def send(val: str) -> None:
            await websocket.send_text(val)
        while True:
            data: str = await websocket.receive_text()
            await websocket.send_text("[[END]]")
            await get_message_async(data, chat, send) 
    except Exception as e:
        logging.info("WebSocket closed:", e)

@app.get("/favicon.ico")
async def favicon():
    file_path = os.path.join("static", "assets", "theam.svg") 
    return FileResponse(file_path)


async def get_message_async(
    prompt: str,
    chat: list[ChatCompletionMessageParam],
    channel: Optional[Callable[[str], Awaitable[None]]] = None
    ) -> None:
    client = AsyncOpenAI(api_key=SETTINGS.API_KEY, base_url=SETTINGS.BASE_URL)
    async def send(msg: str):
        if channel:
            await channel(msg)
    chat.append(
         {"role": "user", "content": prompt}
    )
    try:
        resp = await client.chat.completions.create(
            model=SETTINGS.MODEL,
            messages=chat,
            temperature=SETTINGS.TEMPERATURE,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.0,
        )
        text = (resp.choices[0].message.content or "").strip()
        chat.append(
        {"role": "assistant", "content": text},
        )
        rewrite_prompt = f"{SETTINGS.REWRITE_PROMPT}\nText:\n{text}"
        stream = await client.chat.completions.create(
            model=SETTINGS.MODEL,
            messages=[
                {"role": "system", "content": SETTINGS.REWRITE_ROLE},
                {"role": "user", "content": rewrite_prompt},
            ],
            temperature=SETTINGS.TEMPERATURE_REWRITE,
            top_p=0.9,
            frequency_penalty=0.5,
            presence_penalty=0.0,
            stream=True,
        )
        full_message_parts = []
        async for chunk in stream:
            token = getattr(chunk.choices[0].delta, "content", None)
            if token:
                await send(token)
                full_message_parts.append(token)

        final_text = "".join(full_message_parts)
        logging.debug(final_text)

    except Exception as e:
        await send(f"[Error] {str(e)}")
        