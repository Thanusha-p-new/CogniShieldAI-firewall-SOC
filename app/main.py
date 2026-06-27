from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List
import json
import os

from app.scanner import scan_prompt
from app.analytics import update_stats, get_stats

app = FastAPI()

connections: List[WebSocket] = []


class PromptRequest(BaseModel):
    prompt: str


@app.get("/api")
def home():
    return {"message": "AI Firewall Running"}


@app.get("/")
def dashboard():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


async def broadcast(data: dict):
    dead = []

    for conn in connections:
        try:
            await conn.send_text(json.dumps(data))
        except:
            dead.append(conn)

    for d in dead:
        if d in connections:
            connections.remove(d)


@app.post("/scan")
async def scan(request: PromptRequest):

    result = scan_prompt(request.prompt)

    update_stats(result)

    await broadcast({
        "type": "scan_update",
        "stats": get_stats(),
        "last_scan": result
    })

    return result


@app.get("/stats")
def stats():
    return get_stats()


@app.get("/logs")
def get_logs():
    file = "logs/attacks.log"

    if not os.path.exists(file):
        return {"logs": []}

    try:
        with open(file, "r", encoding="utf-8") as f:
            return {"logs": f.readlines()[-50:]}
    except:
        return {"logs": []}


@app.websocket("/ws")
async def ws(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)

    try:
        while True:
            await websocket.receive_text()
    except:
        if websocket in connections:
            connections.remove(websocket)
