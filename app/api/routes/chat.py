from fastapi import APIRouter, Depends, HTTPException
from app.models.chat import ChatRequest, ChatResponse, ChatSession
from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.core.database import get_database
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest, db=Depends(get_database)):
    """Handle chat requests with AI tutor"""
    try:
        # Get relevant context from RAG
        context = rag_service.get_context_for_query(request.message, request.topic)
        context_str = "\n\n".join(context)
        
        # Generate response using LLM
        response_text = await llm_service.generate_legal_explanation(
            topic=request.topic or "general legal question",
            question=request.message,
            context=context
        )
        
        # Save chat session (simplified - in production you'd want user authentication)
        chat_session = {
            "id": str(uuid.uuid4()),
            "user_id": "anonymous",  # Replace with actual user ID
            "topic": request.topic or "general",
            "messages": [
                {"role": "user", "content": request.message, "timestamp": datetime.now()},
                {"role": "assistant", "content": response_text, "timestamp": datetime.now()}
            ],
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        await db.chat_sessions.insert_one(chat_session)
        
        return ChatResponse(
            response=response_text,
            topic=request.topic,
            sources=context[:3] if context else []
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat request: {str(e)}")

@router.get("/sessions")
async def get_chat_sessions(db=Depends(get_database)):
    """Get user's chat sessions"""
    sessions_cursor = db.chat_sessions.find({"user_id": "anonymous"}).sort("updated_at", -1)
    sessions = await sessions_cursor.to_list(length=50)
    return sessions

@router.get("/topics")
async def get_chat_topics():
    """Get available chat topics"""
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