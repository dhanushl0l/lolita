from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from main import load_config_from_json

app = FastAPI()
SETTINGS = load_config_from_json("config.json")

@app.get("/", response_class=HTMLResponse)
def start_web():
    with open("static/indux.html", "r") as f:
        html_content = f.read()
    return html_content
