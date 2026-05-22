from pydantic import BaseModel
from typing import List, Optional


# ---------------- ANALYSIS ITEM ----------------
class AnalysisItem(BaseModel):
    category: str
    issue: str
    suggestion: str
    severity: str


# ---------------- ANALYZE RESPONSE ----------------
class AnalyzeResponse(BaseModel):
    analysis: List[AnalysisItem]


# ---------------- CHAT REQUEST ----------------
class ChatRequest(BaseModel):
    question: str
    analysis: Optional[List[AnalysisItem]] = None


# ---------------- CHAT RESPONSE ----------------
class ChatResponse(BaseModel):
    reply: str


# ---------------- IMPROVE RESPONSE ----------------
class ImproveResponse(BaseModel):
    image: Optional[str]


# ---------------- EXPORT REQUEST ----------------
class ExportRequest(BaseModel):
    analysis: List[AnalysisItem]
    image: Optional[str] = None