from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.backend.routes import router

# ---------------- APP INIT ----------------
app = FastAPI(
    title="AI Design Critique Assistant",
    description="AI-powered UI/UX analysis and critique system",
    version="1.0.0"
)

# ---------------- CORS (IMPORTANT FOR FRONTEND) ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # 🔥 production me restrict karna
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- ROUTES ----------------
app.include_router(router, prefix="")

# ---------------- HEALTH CHECK ----------------
@app.get("/")
def root():
    return {
        "status": "running",
        "message": "AI Design Critique Backend is live 🚀"
    }

@app.get("/health")
def health():
    return {"status": "ok"}