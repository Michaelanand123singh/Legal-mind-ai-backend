from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import connect_db, close_db
from app.api.routes import chat, cases, learning, search

app = FastAPI(
    title="LegalMind AI",
    description="AI-powered legal education platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    await connect_db()

@app.on_event("shutdown")
async def shutdown_event():
    await close_db()

app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
app.include_router(learning.router, prefix="/api/learning", tags=["learning"])
app.include_router(search.router, prefix="/api/search", tags=["search"])

@app.get("/")
async def root():
    return {"message": "LegalMind AI Backend is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}