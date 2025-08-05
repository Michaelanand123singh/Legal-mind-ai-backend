from fastapi import APIRouter, Depends, HTTPException, Query
from app.services.rag_service import rag_service
from app.core.database import get_database
from typing import Optional

router = APIRouter()

@router.get("/cases")
async def search_cases(
    q: str = Query(..., description="Search query"),
    area: Optional[str] = Query(None, description="Filter by area of law"),
    limit: int = Query(10, ge=1, le=50, description="Number of results to return")
):
    """Search legal cases using semantic similarity"""
    try:
        if not q.strip():
            raise HTTPException(status_code=400, detail="Search query cannot be empty")
        
        # Add area filter to query if provided
        search_query = f"{area} {q}" if area else q
        
        results = rag_service.search_similar_cases(search_query, n_results=limit)
        
        return {
            "query": q,
            "area": area,
            "results": results,
            "total": len(results)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching cases: {str(e)}")

@router.get("/statutes")
async def search_statutes(
    q: str = Query(..., description="Search query"),
    jurisdiction: Optional[str] = Query(None, description="Filter by jurisdiction"),
    db = Depends(get_database)
):
    """Search legal statutes"""
    try:
        # Simple text search in statutes collection
        search_filter = {"$text": {"$search": q}}
        if jurisdiction:
            search_filter["jurisdiction"] = jurisdiction
        
        statutes_cursor = db.statutes.find(search_filter).limit(20)
        statutes = await statutes_cursor.to_list(length=20)
        
        return {
            "query": q,
            "jurisdiction": jurisdiction,
            "results": statutes,
            "total": len(statutes)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching statutes: {str(e)}")

@router.get("/suggest")
async def get_search_suggestions(q: str = Query(..., min_length=2)):
    """Get search suggestions based on partial query"""
    try:
        # Simple suggestion system - in production, you'd want more sophisticated suggestions
        suggestions = []
        
        common_terms = [
            "contract formation", "negligence tort", "criminal intent", "due process",
            "breach of contract", "intentional tort", "constitutional rights", "evidence rules",
            "civil procedure", "property rights", "employment law", "family law"
        ]
        
        for term in common_terms:
            if q.lower() in term.lower():
                suggestions.append(term)
        
        return {"suggestions": suggestions[:10]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating suggestions: {str(e)}")

@router.get("/trending")
async def get_trending_searches(db = Depends(get_database)):
    """Get trending search terms"""
    try:
        # In a real implementation, you'd track search queries and return trending ones
        trending = [
            {"term": "contract law", "count": 150},
            {"term": "negligence", "count": 120},
            {"term": "constitutional rights", "count": 100},
            {"term": "criminal procedure", "count": 85},
            {"term": "property law", "count": 70}
        ]
        
        return {"trending": trending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching trending searches: {str(e)}")