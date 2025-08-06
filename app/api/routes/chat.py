from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_database
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    topic: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    topic: Optional[str] = None
    sources: List[str] = []

class ChatSession(BaseModel):
    id: str
    user_id: str
    topic: str
    messages: List[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

# REMOVED THE MOCK FUNCTION - Using real AI services now

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db=Depends(get_database)):
    """Handle chat requests with AI tutor"""
    try:
        logger.info(f"Received chat request: {request.message[:100]}..., topic: {request.topic}")
        
        # Validate request
        if not request.message or request.message.strip() == "":
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Get relevant context from RAG service
        try:
            context = rag_service.get_context_for_query(
                query=request.message, 
                topic=request.topic
            )
            logger.info(f"Retrieved {len(context)} context items from RAG")
        except Exception as e:
            logger.warning(f"RAG service error: {e}. Proceeding without context.")
            context = []
        
        # Generate response using LLM service with context
        try:
            response_text = await llm_service.generate_legal_explanation(
                topic=request.topic or "general",
                question=request.message,
                context=context
            )
            logger.info("Generated response using LLM service")
        except Exception as e:
            logger.error(f"LLM service error: {e}")
            # Fallback to basic response if LLM fails
            try:
                # Try basic LLM call without context as fallback
                response_text = await llm_service.generate_response(
                    f"As a legal tutor, please explain: {request.message} in the context of {request.topic or 'general law'}"
                )
                logger.info("Generated fallback response using basic LLM")
            except Exception as fallback_error:
                logger.error(f"Fallback LLM also failed: {fallback_error}")
                response_text = f"I apologize, but I'm experiencing technical difficulties. However, I can tell you that your question about '{request.message}' in {request.topic or 'general legal matters'} is important. Please try again in a moment."
        
        # Extract source information from context
        sources = []
        if context:
            # Extract case names or other identifiers from context for citation
            for ctx in context:
                if "Case:" in ctx:
                    case_line = ctx.split('\n')[0]  # First line usually has case name
                    case_name = case_line.replace("Case: ", "").strip()
                    if case_name and case_name != "Unknown":
                        sources.append(case_name)
        
        # Save chat session if database is available
        if db is not None:
            try:
                chat_session = {
                    "id": str(uuid.uuid4()),
                    "user_id": "anonymous",
                    "topic": request.topic or "general",
                    "messages": [
                        {"role": "user", "content": request.message, "timestamp": datetime.now()},
                        {"role": "assistant", "content": response_text, "timestamp": datetime.now()}
                    ],
                    "sources": sources,
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                await db.chat_sessions.insert_one(chat_session)
                logger.info("Chat session saved to database")
            except Exception as db_error:
                logger.warning(f"Database save failed (non-fatal): {db_error}")
        else:
            logger.info("Database not available, running in demo mode")
        
        return ChatResponse(
            response=response_text,
            topic=request.topic,
            sources=sources
        )
    
    except HTTPException as he:
        logger.error(f"HTTP error in chat: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}")
        # Don't expose internal error details to client
        raise HTTPException(status_code=500, detail="An error occurred while processing your request. Please try again.")

@router.get("/sessions")
async def get_chat_sessions(db=Depends(get_database)):
    """Get user's chat sessions"""
    try:
        if db is None:
            logger.info("Database not available, returning empty sessions")
            return {"sessions": []}
        
        sessions_cursor = db.chat_sessions.find({"user_id": "anonymous"}).sort("updated_at", -1)
        sessions = await sessions_cursor.to_list(length=50)
        
        # Convert ObjectId to string for JSON serialization
        for session in sessions:
            if "_id" in session:
                session["_id"] = str(session["_id"])
        
        return {"sessions": sessions}
    except Exception as e:
        logger.error(f"Sessions error: {e}")
        # Return empty sessions instead of failing
        return {"sessions": []}

@router.get("/topics")
async def get_chat_topics():
    """Get available chat topics"""
    try:
        return {
            "topics": [
                {"id": "contract_law", "name": "Contract Law"},
                {"id": "tort_law", "name": "Tort Law"},
                {"id": "criminal_law", "name": "Criminal Law"},
                {"id": "constitutional_law", "name": "Constitutional Law"},
                {"id": "civil_procedure", "name": "Civil Procedure"},
                {"id": "evidence", "name": "Evidence Law"}
            ]
        }
    except Exception as e:
        logger.error(f"Topics error: {e}")
        raise HTTPException(status_code=500, detail="Error getting topics")

# Optional: Add endpoint to test RAG functionality
@router.post("/test-rag")
async def test_rag(query: str, topic: Optional[str] = None):
    """Test endpoint to verify RAG is working"""
    try:
        context = rag_service.get_context_for_query(query, topic)
        return {
            "query": query,
            "topic": topic,
            "context_found": len(context),
            "context": context
        }
    except Exception as e:
        logger.error(f"RAG test error: {e}")
        raise HTTPException(status_code=500, detail=f"RAG test failed: {str(e)}")

# Optional: Add endpoint to test LLM functionality
@router.post("/test-llm")
async def test_llm(message: str, topic: Optional[str] = None):
    """Test endpoint to verify LLM is working"""
    try:
        response = await llm_service.generate_legal_explanation(
            topic=topic or "general",
            question=message,
            context=[]
        )
        return {
            "query": message,
            "topic": topic,
            "response": response
        }
    except Exception as e:
        logger.error(f"LLM test error: {e}")
        raise HTTPException(status_code=500, detail=f"LLM test failed: {str(e)}")