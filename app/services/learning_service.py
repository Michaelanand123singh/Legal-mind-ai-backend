from app.core.database import get_database
from typing import List, Dict, Any
from datetime import datetime

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
            self.db = get_database()
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
        db = await self._get_db()
        
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
    
    async def get_user_progress(self, user_id: str) -> Dict[str, Any]:
        """Get user's learning progress"""
        db = await self._get_db()
        
        progress_cursor = db.learning_progress.find({"user_id": user_id})
        progress_records = await progress_cursor.to_list(length=None)
        
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

learning_service = LearningService()