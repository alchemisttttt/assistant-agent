from fastapi import FastAPI
from requests import session

from agent import run_agent, SYSTEM_PROMPT
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

app= FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions={}

class ChatRequest(BaseModel):
    message: str
    session_id: str

@app.post("/chat")
def chat(request: ChatRequest):
    if request.session_id not in sessions:
        sessions[request.session_id]=[{"role":"system","content":SYSTEM_PROMPT}]

    history=sessions[request.session_id]
    reply= run_agent(request.message, history)
    return {"reply":reply}


@app.get("/")
def root():
    return FileResponse("index.html")
