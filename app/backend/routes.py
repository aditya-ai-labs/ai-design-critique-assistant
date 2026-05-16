from fastapi import APIRouter, UploadFile, File
from app.backend.services.ai_service import analyze_ui, chat_with_context

router = APIRouter()


@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    return await analyze_ui(file)


@router.post("/chat")
async def chat(data: dict):
    question = data.get("question")
    analysis = data.get("analysis")

    reply = await chat_with_context(question, analysis)

    return {"reply": reply}