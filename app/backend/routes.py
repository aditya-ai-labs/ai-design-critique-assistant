from fastapi import APIRouter, UploadFile, File
from app.backend.services.ai_service import analyze_ui

router = APIRouter()

@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    result = await analyze_ui(file)
    return result