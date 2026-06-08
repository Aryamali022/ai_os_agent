import os
import sys
from pathlib import Path
from typing import List
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import AIOsAgent

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"

# Load environment variables
load_dotenv()

if not os.environ.get("NVIDIA_API_KEY"):
    print("[ERROR] NVIDIA_API_KEY not found in environment variables.")
    print("Please create a .env file and add your NVIDIA_API_KEY.")
    sys.exit(1)

app = FastAPI(
    title="AI OS Agent API",
    description="An API to interface with the AI OS Agent using Nvidia Llama 3.1 Nemotron Nano 8B model.",
    version="1.0.0"
)

# Allow frontend on any port (e.g. Live Server) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize agent once at startup
agent = AIOsAgent()

# --- Pydantic Models ---

class ChatRequest(BaseModel):
    message: str

class TaskResult(BaseModel):
    action: str
    parameters: str
    action_result: str

class ChatResponse(BaseModel):
    thought: str
    tasks: List[TaskResult]
    response: str

# --- API Routes (defined BEFORE static mount) ---

@app.post("/chat", response_model=ChatResponse)
def chat_endpoint(request: ChatRequest):
    """
    Send a message to the AI OS Agent and get a response.
    Supports multiple tasks in a single message.
    Defined synchronously (def instead of async def) so FastAPI runs it in a background thread automatically.
    """
    try:
        result = agent.chat(request.message)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "agent": "online"}


@app.get("/")
async def serve_frontend():
    """Serve the frontend chat interface."""
    return FileResponse(str(STATIC_DIR / "index.html"))

# Mount static files at /static for CSS, JS, images etc.
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
