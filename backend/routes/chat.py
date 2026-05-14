from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services import ai_service, memory_service

router = APIRouter(prefix="/chat", tags=["chat"])

class ChatRequest(BaseModel):
    message: str

@router.post("/")
async def chat(request: ChatRequest):
    medical_memory = memory_service.get_medical_memory()
    chat_history = memory_service.get_chat_history()

    memory_service.add_chat_message("user", request.message)

    return StreamingResponse(
        ai_service.answer_chat_question_stream(
            user_message=request.message,
            medical_memory=medical_memory,
            chat_history=chat_history
        ),
        media_type="text/event-stream"
    )

@router.get("/")
async def get_chat():
    history = memory_service.get_chat_history()
    # Filter out system messages (like raw OCR text) so the UI only renders human/assistant chat
    filtered_history = [msg for msg in history if msg.get("role") != "system"]
    return {"status": "success", "chat_history": filtered_history}
