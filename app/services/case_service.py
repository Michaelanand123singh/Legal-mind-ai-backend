from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.core.database import get_database
from typing import List, Dict, Any
from datetime import datetime
import uuid

class CaseService:
    def __init__(self):
        self.db = None
    
    async def _get_db(self):
        if not self.db:
            self.db = get_database()
        return self.db
    
    async def analyze_case(self, case_text: str, analysis_type: str = "irac") -> Dict[str, Any]:
        """Analyze a legal case using AI"""
        analysis = await llm_service.analyze_legal_case(case_text)
        
        # Save analysis to database
        db = await self._get_db()
        case_analysis = {
            "id": str(uuid.uuid4()),
            "case_text": case_text,
            "analysis_type": analysis_type,
            "analysis": analysis,
            "user_id": "anonymous",  # Replace with actual user ID
            "created_at": datetime.now()
        }
        
        await db.case_analyses.insert_one(case_analysis)
        
        return analysis
    
    async def get_cases_by_area(self, area_of_law: str) -> List[Dict[str, Any]]:
        """Get cases filtered by area of law"""
        return rag_service.search_similar_cases(area_of_law, n_results=10)
    
    async def search_cases(self, query: str) -> List[Dict[str, Any]]:
        """Search cases using RAG similarity search"""
        return rag_service.search_similar_cases(query, n_results=10)
    
    async def get_user_analyses(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's case analyses"""
        db = await self._get_db()
        analyses_cursor = db.case_analyses.find({"user_id": user_id}).sort("created_at", -1)
        analyses = await analyses_cursor.to_list(length=50)
        return analyses

case_service = CaseService()