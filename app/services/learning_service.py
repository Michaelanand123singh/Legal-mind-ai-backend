from app.core.database import get_database
from typing import List, Dict, Any
from datetime import datetime
from bson import ObjectId

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

class LearningService:
    def __init__(self):
        self.db = None
        self.learning_modules = {
            "contract_law": {
                "id": "contract_law",
                "title": "Contract Law Fundamentals",
                "description": "Learn the basics of contract formation, interpretation, and breach",
                "lessons": [
                    {"id": "offer_acceptance", "title": "Offer and Acceptance", "duration": 30},
                    {"id": "consideration", "title": "Consideration", "duration": 25},
                    {"id": "capacity", "title": "Capacity to Contract", "duration": 20},
                    {"id": "breach_remedies", "title": "Breach and Remedies", "duration": 35}
                ]
            },
            "tort_law": {
                "id": "tort_law",
                "title": "Tort Law Essentials",
                "description": "Understanding negligence, intentional torts, and strict liability",
                "lessons": [
                    {"id": "negligence", "title": "Elements of Negligence", "duration": 40},
                    {"id": "intentional_torts", "title": "Intentional Torts", "duration": 30},
                    {"id": "strict_liability", "title": "Strict Liability", "duration": 25},
                    {"id": "defenses", "title": "Defenses to Tort Claims", "duration": 20}
                ]
            },
            "criminal_law": {
                "id": "criminal_law",
                "title": "Criminal Law Basics",
                "description": "Elements of crimes, defenses, and criminal procedure",
                "lessons": [
                    {"id": "actus_reus", "title": "Actus Reus", "duration": 25},
                    {"id": "mens_rea", "title": "Mens Rea", "duration": 30},
                    {"id": "defenses", "title": "Criminal Defenses", "duration": 35},
                    {"id": "procedure", "title": "Criminal Procedure Overview", "duration": 40}
                ]
            }
        }
    
    async def _get_db(self):
        if not self.db:
            try:
                self.db = get_database()
            except Exception as e:
                print(f"Database connection error: {e}")
                self.db = None
        return self.db
    
    async def get_learning_modules(self) -> List[Dict[str, Any]]:
        """Get all available learning modules"""
        modules = []
        for module_id, module_data in self.learning_modules.items():
            module_copy = module_data.copy()
            module_copy["total_lessons"] = len(module_data["lessons"])
            module_copy["estimated_duration"] = sum(lesson["duration"] for lesson in module_data["lessons"])
            modules.append(module_copy)
        return modules
    
    async def get_module_content(self, module_id: str) -> Dict[str, Any]:
        """Get detailed content for a specific module"""
        if module_id not in self.learning_modules:
            raise ValueError(f"Module {module_id} not found")
        
        module = self.learning_modules[module_id].copy()
        
        # Add more detailed content for each lesson
        detailed_lessons = []
        for lesson in module["lessons"]:
            detailed_lesson = lesson.copy()
            detailed_lesson["content"] = await self._get_lesson_content(module_id, lesson["id"])
            detailed_lessons.append(detailed_lesson)
        
        module["lessons"] = detailed_lessons
        return module
    
    async def _get_lesson_content(self, module_id: str, lesson_id: str) -> Dict[str, Any]:
        """Get content for a specific lesson"""
        # In a real application, this would fetch from a database or content management system
        content_templates = {
            "offer_acceptance": {
                "overview": "An offer is a definite proposal to enter into a contract. Acceptance is the agreement to the terms of the offer.",
                "key_points": [
                    "Offers must be definite and communicated",
                    "Acceptance must be unqualified and communicated",
                    "The mirror image rule requires exact acceptance"
                ],
                "examples": ["Case: Carlill v. Carbolic Smoke Ball Co.", "Case: Pharmaceutical Society v. Boots"],
                "quiz": [
                    {"question": "What makes an offer legally binding?", "type": "multiple_choice"},
                    {"question": "Explain the mirror image rule", "type": "essay"}
                ]
            },
            "negligence": {
                "overview": "Negligence is the failure to exercise reasonable care that results in damage or injury to another.",
                "key_points": [
                    "Four elements: duty, breach, causation, damages",
                    "Reasonable person standard applies",
                    "Both factual and proximate causation required"
                ],
                "examples": ["Case: Donoghue v. Stevenson", "Case: Palsgraf v. Long Island Railroad"],
                "quiz": [
                    {"question": "What are the four elements of negligence?", "type": "multiple_choice"},
                    {"question": "Explain proximate cause", "type": "essay"}
                ]
            }
        }
        
        return content_templates.get(lesson_id, {
            "overview": f"Content for {lesson_id} in {module_id}",
            "key_points": ["Key concept 1", "Key concept 2"],
            "examples": ["Example case"],
            "quiz": []
        })
    
    async def track_progress(self, user_id: str, module_id: str, lesson_id: str, completed: bool = True):
        """Track user's learning progress"""
        try:
            db = await self._get_db()
            if not db:
                print("Database not available for tracking progress")
                return
            
            progress_update = {
                "user_id": user_id,
                "module_id": module_id,
                "lesson_id": lesson_id,
                "completed": completed,
                "completed_at": datetime.now() if completed else None,
                "updated_at": datetime.now()
            }
            
            await db.learning_progress.update_one(
                {"user_id": user_id, "module_id": module_id, "lesson_id": lesson_id},
                {"$set": progress_update},
                upsert=True
            )
        except Exception as e:
            print(f"Error tracking progress: {e}")
    
    async def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's learning progress"""
        try:
            db = await self._get_db()
            if not db:
                # Return mock progress if database not available
                return self._get_mock_progress()
            
            progress_cursor = db.learning_progress.find({"user_id": user_id})
            progress_records = await progress_cursor.to_list(length=None)
            
            # Convert ObjectIds to strings
            progress_records = serialize_objectid(progress_records)
            
            # Organize progress by module
            progress_by_module = {}
            for record in progress_records:
                module_id = record["module_id"]
                if module_id not in progress_by_module:
                    progress_by_module[module_id] = []
                progress_by_module[module_id].append({
                    "lesson_id": record["lesson_id"],
                    "completed": record["completed"],
                    "completed_at": record.get("completed_at")
                })
            
            return progress_by_module
            
        except Exception as e:
            print(f"Error getting user progress: {e}")
            return self._get_mock_progress()
    
    def _get_mock_progress(self) -> Dict[str, Any]:
        """Return mock progress data when database is unavailable"""
        return {
            "contract_law": [
                {"lesson_id": "offer_acceptance", "completed": True, "completed_at": "2024-01-15T10:30:00"},
                {"lesson_id": "consideration", "completed": True, "completed_at": "2024-01-15T11:00:00"},
                {"lesson_id": "capacity", "completed": False, "completed_at": None},
                {"lesson_id": "breach_remedies", "completed": False, "completed_at": None}
            ],
            "tort_law": [
                {"lesson_id": "negligence", "completed": True, "completed_at": "2024-01-14T09:30:00"},
                {"lesson_id": "intentional_torts", "completed": False, "completed_at": None},
                {"lesson_id": "strict_liability", "completed": False, "completed_at": None},
                {"lesson_id": "defenses", "completed": False, "completed_at": None}
            ],
            "criminal_law": [
                {"lesson_id": "actus_reus", "completed": False, "completed_at": None},
                {"lesson_id": "mens_rea", "completed": False, "completed_at": None},
                {"lesson_id": "defenses", "completed": False, "completed_at": None},
                {"lesson_id": "procedure", "completed": False, "completed_at": None}
            ]
        }

learning_service = LearningService()