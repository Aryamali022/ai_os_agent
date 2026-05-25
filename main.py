import os
import sys
from fastapi import FastAPI, HTTPException
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

agent = AIOsAgent()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    thought: str
    action: str
    parameters: str
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Send a message to the AI OS Agent and get a response.
    Example body: {"message": "hello, what can you do?"}
    """
    try:
        result = agent.chat(request.message)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
