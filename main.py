from fastapi import FastAPI, WebSocket, Request, HTTPException, Depends
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict
import uuid
import json

from app.scanner import scan_prompt
from app.analytics import update_stats, get_stats

app = FastAPI()

# ---------------- USERS ----------------
USERS = {
    "admin": "admin123",
    "soc": "secure123",
    "user1": "pass123"
}

SESSIONS: Dict[str, str] = {}

connections: List[WebSocket] = []


# ---------------- MODELS ----------------
class LoginRequest(BaseModel):
    username: str
    password: str

class PromptRequest(BaseModel):
    prompt: str


# ---------------- HOME ----------------
@app.get("/api")
def api():
    return {"message": "CogniShieldAI Running"}


@app.get("/")
def home():
    with open("templates/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


# ---------------- LOGIN ----------------
@app.post("/login")
def login(data: LoginRequest):

    if data.username not in USERS or USERS[data.username] != data.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = str(uuid.uuid4())
    SESSIONS[token] = data.username

    return {
        "token": token,
        "user": data.username
    }


# ---------------- AUTH ----------------
def auth(request: Request):
    token = request.headers.get("token")

    if not token or token not in SESSIONS:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return SESSIONS[token]


# ---------------- SCAN ----------------
@app.post("/scan")
def scan(req: PromptRequest, user=Depends(auth)):

    result = scan_prompt(req.prompt)
    result["user"] = user

    update_stats(result)

    return result


# ---------------- STATS ----------------
@app.get("/stats")
def stats(user=Depends(auth)):
    return get_stats()


# ---------------- WS ----------------
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