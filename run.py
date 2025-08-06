#!/usr/bin/env python3
"""
Run script for Legal Education AI Backend
"""
import os
import uvicorn
from app.main import app

if __name__ == "__main__":
    # Get port from environment variable (Cloud Run sets PORT=8080)
    port = int(os.environ.get("PORT", 8080))
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )