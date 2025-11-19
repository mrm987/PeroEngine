from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import time

app = FastAPI()

# Allow CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str

@app.get("/")
def read_root():
    return {"status": "online", "message": "PeroEngine Brain is Running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.post("/chat")
def chat_endpoint(request: ChatRequest):
    # Mock response for now
    time.sleep(0.5) # Simulate processing
    return {
        "response": f"I heard you say: '{request.message}'. I am still learning to speak!",
        "emotion": "happy"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
