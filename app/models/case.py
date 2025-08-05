from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

class CaseAnalysisRequest(BaseModel):
    case_text: str
    analysis_type: str = "irac"  # "irac", "brief", "summary"

class CaseAnalysisResponse(BaseModel):
    issue: str
    rule: str
    application: str
    conclusion: str
    key_facts: List[str]
    legal_principles: List[str]

class LegalCase(BaseModel):
    id: Optional[str] = None
    case_name: str
    citation: Optional[str] = None
    court: Optional[str] = None
    year: Optional[int] = None
    facts: str
    holding: str
    reasoning: str
    area_of_law: str
    keywords: List[str] = []

class CaseBrief(BaseModel):
    case_name: str
    citation: str
    facts: str
    procedural_history: str
    issue: str
    holding: str
    reasoning: str
    rule: str