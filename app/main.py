from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

# Import your modules (make sure these exist)
try:
    from app.core.config import settings
    from app.core.database import connect_db, close_db
    from app.api.routes import chat, cases, learning, search
    HAS_MODULES = True
except ImportError as e:
    print(f"Warning: Some modules not found: {e}")
    HAS_MODULES = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if HAS_MODULES:
        try:
            await connect_db()
            print("✅ Database connected successfully")
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            # Don't fail startup if DB is not available
    
    yield
    
    # Shutdown
    if HAS_MODULES:
        try:
            await close_db()
        except Exception as e:
            print(f"Warning: Error during shutdown: {e}")

app = FastAPI(
    title="LegalMind AI",
    description="AI-powered legal education platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration - Updated to fix CORS issues
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://legal-mind-ai-frontend.vercel.app",  # Your exact frontend URL
        "https://legal-mind-ai-frontend-*.vercel.app",  # For preview deployments
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
)

# Include routers only if modules are available
if HAS_MODULES:
    try:
        app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
        app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
        app.include_router(learning.router, prefix="/api/learning", tags=["learning"])
        app.include_router(search.router, prefix="/api/search", tags=["search"])
    except Exception as e:
        print(f"Warning: Error including routers: {e}")

@app.get("/")
async def root():
    return {
        "message": "LegalMind AI Backend is running",
        "version": "1.0.0",
        "status": "healthy"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "legal-ai-backend",
        "version": "1.0.0"
    }

# Additional endpoint for testing CORS
@app.get("/cors-test")
async def cors_test():
    return {
        "message": "CORS is working!",
        "frontend": "https://legal-mind-ai-frontend.vercel.app",
        "backend": "Cloud Run"
    }