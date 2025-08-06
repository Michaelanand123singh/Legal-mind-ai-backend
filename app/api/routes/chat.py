from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_database
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

# Mock LLM response function
async def generate_mock_response(topic: str, question: str) -> str:
    """Generate a mock legal explanation"""
    responses = {
        "contract_law": f"Regarding your contract law question: '{question}' - In contract law, the fundamental elements include offer, acceptance, consideration, and capacity. Your specific question relates to key principles that govern contractual relationships.",
        "tort_law": f"For your tort law inquiry: '{question}' - Tort law deals with civil wrongs and the remedies available. The main categories are intentional torts, negligence, and strict liability.",
        "criminal_law": f"Concerning your criminal law question: '{question}' - Criminal law involves offenses against the state. Key elements include actus reus (guilty act) and mens rea (guilty mind).",
        "constitutional_law": f"Regarding constitutional law: '{question}' - Constitutional law governs the interpretation and implementation of the Constitution, including separation of powers and individual rights.",
        "civil_procedure": f"About civil procedure: '{question}' - Civil procedure governs the process by which civil cases are adjudicated in court, including pleadings, discovery, and trial procedures.",
        "evidence": f"Concerning evidence law: '{question}' - Evidence law determines what information may be presented to a judge or jury and how it should be presented during trial."
    }
    
    return responses.get(topic, f"Thank you for your legal question: '{question}'. This is a general legal inquiry that requires careful analysis of applicable laws and precedents.")

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db=Depends(get_database)):
    """Handle chat requests with AI tutor"""
    try:
        logger.info(f"Received chat request: {request.message[:100]}..., topic: {request.topic}")
        
        # Validate request
        if not request.message or request.message.strip() == "":
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        # Generate response
        response_text = await generate_mock_response(
            topic=request.topic or "general",
            question=request.message
        )
        
        # Save chat session if database is available
        if db:
            try:
                chat_session = {
                    "id": str(uuid.uuid4()),
                    "user_id": "anonymous",
                    "topic": request.topic or "general",
                    "messages": [
                        {"role": "user", "content": request.message, "timestamp": datetime.now()},
                        {"role": "assistant", "content": response_text, "timestamp": datetime.now()}
                    ],
                    "created_at": datetime.now(),
                    "updated_at": datetime.now()
                }
                
                await db.chat_sessions.insert_one(chat_session)
                logger.info("Chat session saved to database")
            except Exception as db_error:
                logger.warning(f"Database save failed (non-fatal): {db_error}")
        else:
            logger.info("Database not available, skipping session save")
        
        return ChatResponse(
            response=response_text,
            topic=request.topic,
            sources=[]
        )
    
    except HTTPException as he:
        logger.error(f"HTTP error in chat: {he.detail}")
        raise he
    except Exception as e:
        logger.error(f"Unexpected error in chat: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@router.get("/sessions")
async def get_chat_sessions(db=Depends(get_database)):
    """Get user's chat sessions"""
    try:
        if not db:
            logger.info("Database not available for sessions")
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
        raise HTTPException(status_code=500, detail=f"Error getting topics: {str(e)}")