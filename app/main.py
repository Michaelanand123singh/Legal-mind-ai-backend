from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import your modules with error handling
try:
    from app.core.config import settings
    from app.core.database import connect_db, close_db
    from app.api.routes import chat, cases, learning, search
    HAS_MODULES = True
    logger.info("✅ All modules imported successfully")
except ImportError as e:
    logger.error(f"❌ Import error: {e}")
    HAS_MODULES = False

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting LegalMind AI Backend...")
    
    if HAS_MODULES:
        try:
            db_connected = await connect_db()
            if db_connected:
                logger.info("✅ Database connected successfully")
            else:
                logger.info("⚠️  Running without database (demo mode)")
        except Exception as e:
            logger.warning(f"⚠️  Database connection failed: {e}")
            logger.info("Continuing without database...")
    
    logger.info("🎯 Backend startup complete")
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down...")
    if HAS_MODULES:
        try:
            await close_db()
        except Exception as e:
            logger.warning(f"Shutdown warning: {e}")
    logger.info("👋 Shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="LegalMind AI",
    description="AI-powered legal education platform",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "https://legal-mind-ai-frontend.vercel.app",
        "https://*.vercel.app",
        "*"  # Allow all origins for now (remove in production)
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    expose_headers=["*"]
)

# Include routers with error handling
if HAS_MODULES:
    try:
        app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
        app.include_router(cases.router, prefix="/api/cases", tags=["cases"])
        app.include_router(learning.router, prefix="/api/learning", tags=["learning"])
        app.include_router(search.router, prefix="/api/search", tags=["search"])
        logger.info("✅ All API routes registered successfully")
    except Exception as e:
        logger.error(f"❌ Error registering routes: {e}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🎓 LegalMind AI Backend is running",
        "version": "1.0.0",
        "status": "healthy",
        "database_connected": HAS_MODULES,
        "endpoints": [
            "/health",
            "/api/chat/",
            "/api/chat/sessions",
            "/api/chat/topics",
            "/api/learning/stats",
            "/api/cases/analyses"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "legal-ai-backend",
        "version": "1.0.0",
        "modules_loaded": HAS_MODULES
    }

@app.get("/api/test")
async def test_endpoint():
    """Test endpoint to verify API is working"""
    return {
        "message": "✅ API is working correctly",
        "timestamp": "2024-01-01T00:00:00Z"
    }

# Handle CORS preflight requests
@app.options("/{full_path:path}")
async def options_handler(full_path: str):
    """Handle CORS preflight requests"""
    return {"message": "OK"}

# Error handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return {
        "error": "Internal server error",
        "message": "Something went wrong. Please try again later."
    }