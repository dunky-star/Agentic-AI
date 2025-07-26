#  `main.py` will wrap it in a FastAPI app# This is a sample Python script.
import uvicorn
from fastapi import FastAPI, HTTPException
from typing import List
from rag_service import answer_research_question
from openai import BaseModel

from services import get_ai_response
app = FastAPI(
    title="AI Chatbot API",
    description="A simple AI chatbot API powered by LangChain and OpenAI's GPT model.",
    version="1.0.0",
)

class ChatRequest(BaseModel):
    message : str

class ChatResponse(BaseModel):
    response: str

class ResearchRequest(BaseModel):
    question: str

class Source(BaseModel):
    title: str
    content: str
    score: float

class ResearchResponse(BaseModel):
    answer: str
    sources: List[Source]


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """Chat with an AI assistant"""
    try:
        ai_response = get_ai_response(request.message)
        return ChatResponse(response=ai_response)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/research", response_model=ResearchResponse)
async def ask_research_question(request: ResearchRequest):
    try:
        answer, sources = answer_research_question(request.question)
        formatted = [
            Source(
                title=s["title"],
                content=s["content"][:200] + "..." if len(s["content"]) > 200 else s["content"],
                score=s["score"]
            ) for s in sources
        ]
        return ResearchResponse(answer=answer, sources=formatted)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "AI Chatbot API is running! Visit /docs for API documentation."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

