from fastapi import APIRouter
from pydantic import BaseModel
from rag.pipeline import generate_answer

router = APIRouter()

class ChatRequest(BaseModel):
    query: str
    chat_history: list[dict] = []   # optional, for future multi-turn use

class ChatResponse(BaseModel):
    query: str
    answer: str
    sources: list[dict]

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    result = generate_answer(request.query)
    return ChatResponse(
        query=result["query"],
        answer=result["answer"],
        sources=result["sources"]
    )