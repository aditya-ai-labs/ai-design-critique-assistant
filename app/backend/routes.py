from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from typing import Dict, Any
from app.models.schemas import ChatResponse,ChatRequest

from app.backend.services.ai_service import (
    analyze_ui,
    chat_with_context,
    improve_ui,
    export_pdf
)

router = APIRouter()


# ---------------- ANALYZE ----------------
@router.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    try:
        if not file:
            raise HTTPException(status_code=400, detail="No file uploaded")

        result = await analyze_ui(file)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- CHAT ----------------
@router.post("/chat", response_model=ChatResponse)
async def chat(data: ChatRequest):
    try:
        question = data.get("question")
        analysis = data.get("analysis")

        if not question:
            raise HTTPException(status_code=400, detail="Question is required")

        reply = await chat_with_context(question, analysis)

        return {"reply": reply}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- IMPROVE UI ----------------
@router.post("/improve")
async def improve(data: Dict[str, Any]):
    try:
        analysis = data.get("analysis")

        if not analysis:
            raise HTTPException(status_code=400, detail="Analysis required")

        return await improve_ui(analysis)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- EXPORT PDF ----------------
@router.post("/export")
async def export(data: Dict[str, Any]):
    try:
        analysis = data.get("analysis")
        image = data.get("image")

        if not analysis:
            raise HTTPException(status_code=400, detail="Analysis required")

        pdf_file = export_pdf(analysis, image)

        return StreamingResponse(
            pdf_file,
            media_type="application/pdf",
            headers={
                "Content-Disposition": "attachment; filename=design_report.pdf"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))