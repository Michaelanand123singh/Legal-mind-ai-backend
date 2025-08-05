from fastapi import APIRouter, Depends, HTTPException
from app.models.case import CaseAnalysisRequest, CaseAnalysisResponse
from app.services.case_service import case_service
from app.core.database import get_database
from typing import List

router = APIRouter()

@router.post("/analyze", response_model=CaseAnalysisResponse)
async def analyze_case(request: CaseAnalysisRequest):
    """Analyze a legal case using IRAC method"""
    try:
        analysis = await case_service.analyze_case(request.case_text, request.analysis_type)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing case: {str(e)}")

@router.get("/area/{area_of_law}")
async def get_cases_by_area(area_of_law: str):
    """Get cases by area of law"""
    try:
        cases = await case_service.get_cases_by_area(area_of_law)
        return {"cases": cases}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching cases: {str(e)}")

@router.get("/search")
async def search_cases(q: str):
    """Search cases using RAG similarity search"""
    try:
        if not q:
            raise HTTPException(status_code=400, detail="Query parameter 'q' is required")
        
        results = await case_service.search_cases(q)
        return {"results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching cases: {str(e)}")

@router.get("/areas")
async def get_legal_areas():
    """Get available areas of law"""
    return {
        "areas": [
            {"id": "contract_law", "name": "Contract Law"},
            {"id": "tort_law", "name": "Tort Law"},
            {"id": "criminal_law", "name": "Criminal Law"},
            {"id": "constitutional_law", "name": "Constitutional Law"},
            {"id": "civil_procedure", "name": "Civil Procedure"},
            {"id": "evidence", "name": "Evidence Law"},
            {"id": "property_law", "name": "Property Law"}
        ]
    }

@router.get("/analyses")
async def get_user_analyses(db=Depends(get_database)):
    """Get user's case analyses"""
    try:
        analyses = await case_service.get_user_analyses("anonymous")
        return {"analyses": analyses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analyses: {str(e)}")