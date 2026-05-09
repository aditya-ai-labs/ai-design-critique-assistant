from fastapi import FastAPI
from app.backend.routes import router

app = FastAPI(title="AI Design Critique Assistant")

app.include_router(router)

@app.get("/")
def root():
    return {"message": "Backend is running"}