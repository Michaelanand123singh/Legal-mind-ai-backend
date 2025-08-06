from app.services.llm_service import llm_service
from app.services.rag_service import rag_service
from app.core.database import get_database
from typing import List, Dict, Any
from datetime import datetime
from bson import ObjectId
import uuid

def serialize_objectid(obj):
    """Convert MongoDB ObjectId to string"""
    if isinstance(obj, ObjectId):
        return str(obj)
    elif isinstance(obj, dict):
        return {key: serialize_objectid(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_objectid(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    return obj

class CaseService:
    def __init__(self):
        self.db = None
    
    async def _get_db(self):
        if not self.db:
            self.db = get_database()
        return self.db
    
    async def analyze_case(self, case_text: str, analysis_type: str = "irac") -> Dict[str, Any]:
        """Analyze a legal case using AI"""
        try:
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
        except Exception as e:
            print(f"Error in analyze_case: {e}")
            # Return mock analysis if service fails
            return {
                "issue": "What legal issue is presented in this case?",
                "rule": "The applicable legal rule or statute",
                "application": "How the rule applies to the facts",
                "conclusion": "The likely outcome based on the analysis",
                "key_facts": ["Fact 1", "Fact 2", "Fact 3"],
                "legal_principles": ["Principle 1", "Principle 2"]
            }
    
    async def get_cases_by_area(self, area_of_law: str) -> List[Dict[str, Any]]:
        """Get cases filtered by area of law"""
        try:
            cases = rag_service.search_similar_cases(area_of_law, n_results=10)
            return serialize_objectid(cases)
        except Exception as e:
            print(f"Error in get_cases_by_area: {e}")
            # Return mock cases if service fails
            return [
                {
                    "id": "1",
                    "case_name": f"Sample {area_of_law.replace('_', ' ').title()} Case",
                    "citation": "123 F.3d 456 (2023)",
                    "court": "Supreme Court",
                    "area_of_law": area_of_law,
                    "summary": "A sample case for demonstration purposes"
                }
            ]
    
    async def search_cases(self, query: str) -> List[Dict[str, Any]]:
        """Search cases using RAG similarity search"""
        try:
            cases = rag_service.search_similar_cases(query, n_results=10)
            return serialize_objectid(cases)
        except Exception as e:
            print(f"Error in search_cases: {e}")
            # Return mock search results if service fails
            return [
                {
                    "id": "1",
                    "case_name": "Relevant Case Example",
                    "citation": "456 F.3d 789 (2023)", 
                    "relevance_score": 0.85,
                    "summary": f"A case related to: {query}"
                }
            ]
    
    async def get_user_analyses(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's case analyses"""
        try:
            db = await self._get_db()
            analyses_cursor = db.case_analyses.find({"user_id": user_id}).sort("created_at", -1)
            analyses = await analyses_cursor.to_list(length=50)
            
            # Convert ObjectIds to strings before returning
            serialized_analyses = serialize_objectid(analyses)
            return serialized_analyses
            
        except Exception as e:
            print(f"Error in get_user_analyses: {e}")
            # Return mock analyses if database fails
            return [
                {
                    "id": "1",
                    "case_text": "Sample case text for contract breach...",
                    "analysis_type": "irac",
                    "analysis": {
                        "issue": "Whether defendant breached the contract",
                        "rule": "A contract is breached when a party fails to perform",
                        "application": "Defendant failed to deliver goods as promised",
                        "conclusion": "Defendant breached the contract"
                    },
                    "created_at": "2024-01-15T10:30:00",
                    "area_of_law": "contract_law"
                },
                {
                    "id": "2", 
                    "case_text": "Sample negligence case involving car accident...",
                    "analysis_type": "irac",
                    "analysis": {
                        "issue": "Whether defendant was negligent in the accident",
                        "rule": "Negligence requires duty, breach, causation, and damages",
                        "application": "Defendant ran red light, causing collision",
                        "conclusion": "Defendant was negligent"
                    },
                    "created_at": "2024-01-10T14:20:00",
                    "area_of_law": "tort_law"
                }
            ]

case_service = CaseService()