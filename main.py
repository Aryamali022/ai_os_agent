import os
import sys
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import AIOsAgent

# Load environment variables
load_dotenv()

if not os.environ.get("GROQ_API_KEY"):
    print("[ERROR] GROQ_API_KEY not found in environment variables.")
    print("Please create a .env file and add your GROQ_API_KEY.")
    sys.exit(1)

app = FastAPI(
    title="AI OS Agent API",
    description="An API to interface with the AI OS Agent using Groq Llama 3.3 70B Versatile model.",
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
async def chat_endpoint(request: ChatRequest):
    """
    Send a message to the AI OS Agent and get a response.
    Supports multiple tasks in a single message.
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
    return FileResponse("static/index.html")

# Mount static files at /static for CSS, JS, images etc.
app.mount("/static", StaticFiles(directory="static"), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
