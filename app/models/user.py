from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: Optional[str] = None
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    full_name: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserProgress(BaseModel):
    user_id: str
    module_id: str
    lesson_id: str
    completed: bool = False
    completed_at: Optional[datetime] = None
    score: Optional[float] = None

class UserStats(BaseModel):
    total_lessons: int
    completed_lessons: int
    completion_rate: float
    study_streak: int
    total_study_time: int  # in minutes