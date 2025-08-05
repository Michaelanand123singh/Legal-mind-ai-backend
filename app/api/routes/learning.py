from fastapi import APIRouter, Depends, HTTPException
from app.services.learning_service import learning_service
from app.core.database import get_database
from pydantic import BaseModel

router = APIRouter()

class ProgressUpdate(BaseModel):
    module_id: str
    lesson_id: str
    completed: bool = True

@router.get("/modules")
async def get_learning_modules():
    """Get all available learning modules"""
    try:
        modules = await learning_service.get_learning_modules()
        return {"modules": modules}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching modules: {str(e)}")

@router.get("/modules/{module_id}")
async def get_module_content(module_id: str):
    """Get detailed content for a specific module"""
    try:
        content = await learning_service.get_module_content(module_id)
        return content
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching module content: {str(e)}")

@router.post("/progress")
async def update_progress(progress: ProgressUpdate):
    """Update user's learning progress"""
    try:
        await learning_service.track_progress(
            "anonymous",  # Replace with actual user ID
            progress.module_id,
            progress.lesson_id,
            progress.completed
        )
        return {"message": "Progress updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating progress: {str(e)}")

@router.get("/progress")
async def get_user_progress():
    """Get user's learning progress"""
    try:
        progress = await learning_service.get_user_progress("anonymous")
        return {"progress": progress}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching progress: {str(e)}")

@router.get("/stats")
async def get_learning_stats():
    """Get learning statistics"""
    try:
        progress = await learning_service.get_user_progress("anonymous")
        total_lessons = sum(len(module.get("lessons", [])) for module in progress.values())
        completed_lessons = sum(
            1 for module in progress.values() 
            for lesson in module 
            if lesson.get("completed", False)
        )
        
        return {
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "completion_rate": (completed_lessons / total_lessons * 100) if total_lessons > 0 else 0
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching stats: {str(e)}")