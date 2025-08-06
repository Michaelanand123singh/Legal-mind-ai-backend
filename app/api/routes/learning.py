from fastapi import APIRouter, Depends, HTTPException
from app.core.database import get_database
from pydantic import BaseModel
from typing import List, Dict, Any
from datetime import datetime

router = APIRouter()

class ProgressUpdate(BaseModel):
    module_id: str
    lesson_id: str
    completed: bool = True

# Mock learning modules data
MOCK_LEARNING_MODULES = [
    {
        "id": "contract_basics",
        "title": "Contract Law Basics",
        "description": "Fundamental concepts of contract formation and enforcement",
        "lessons": [
            {"id": "offer_acceptance", "title": "Offer and Acceptance", "completed": False},
            {"id": "consideration", "title": "Consideration", "completed": False},
            {"id": "capacity", "title": "Capacity to Contract", "completed": False}
        ]
    },
    {
        "id": "tort_fundamentals", 
        "title": "Tort Law Fundamentals",
        "description": "Introduction to civil wrongs and liability",
        "lessons": [
            {"id": "negligence", "title": "Negligence", "completed": False},
            {"id": "intentional_torts", "title": "Intentional Torts", "completed": False},
            {"id": "strict_liability", "title": "Strict Liability", "completed": False}
        ]
    }
]

@router.get("/modules")
async def get_learning_modules():
    """Get all available learning modules"""
    try:
        return {"modules": MOCK_LEARNING_MODULES}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching modules: {str(e)}")

@router.get("/modules/{module_id}")
async def get_module_content(module_id: str):
    """Get detailed content for a specific module"""
    try:
        module = next((m for m in MOCK_LEARNING_MODULES if m["id"] == module_id), None)
        if not module:
            raise HTTPException(status_code=404, detail="Module not found")
        return module
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching module content: {str(e)}")

@router.post("/progress")
async def update_progress(progress: ProgressUpdate, db=Depends(get_database)):
    """Update user's learning progress"""
    try:
        # Simple progress tracking - in production you'd use proper user auth
        progress_doc = {
            "user_id": "anonymous",
            "module_id": progress.module_id,
            "lesson_id": progress.lesson_id,
            "completed": progress.completed,
            "updated_at": datetime.now()
        }
        
        # Upsert progress
        if db:
            await db.user_progress.update_one(
                {
                    "user_id": "anonymous",
                    "module_id": progress.module_id,
                    "lesson_id": progress.lesson_id
                },
                {"$set": progress_doc},
                upsert=True
            )
        
        return {"message": "Progress updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating progress: {str(e)}")

@router.get("/progress")
async def get_user_progress(db=Depends(get_database)):
    """Get user's learning progress"""
    try:
        if not db:
            # Return mock progress if no database
            return {"progress": {}}
        
        progress_cursor = db.user_progress.find({"user_id": "anonymous"})
        progress_list = await progress_cursor.to_list(length=None)
        
        # Group progress by module
        progress_dict = {}
        for item in progress_list:
            module_id = item["module_id"]
            if module_id not in progress_dict:
                progress_dict[module_id] = {}
            progress_dict[module_id][item["lesson_id"]] = {
                "completed": item["completed"],
                "updated_at": item["updated_at"]
            }
        
        return {"progress": progress_dict}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching progress: {str(e)}")

@router.get("/stats")
async def get_learning_stats(db=Depends(get_database)):
    """Get learning statistics"""
    try:
        # Calculate stats from mock data and progress
        total_lessons = sum(len(module.get("lessons", [])) for module in MOCK_LEARNING_MODULES)
        
        completed_lessons = 0
        if db:
            try:
                completed_count = await db.user_progress.count_documents({
                    "user_id": "anonymous",
                    "completed": True
                })
                completed_lessons = completed_count
            except Exception:
                completed_lessons = 0
        
        completion_rate = (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        
        return {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "completion_rate": round(completion_rate, 1)
        }
    except Exception as e:
        print(f"Stats error: {e}")  # Log the actual error
        # Return default stats if there's an error
        return {
            "total_lessons": 6,
            "completed_lessons": 0,
            "completion_rate": 0.0
        }