# pitchquest_api/routers/evaluator.py
"""
Evaluator API Router
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from ..database import get_db
from ..services.evaluator_service import evaluator_service

router = APIRouter()

class EvaluationResponse(BaseModel):
    success: bool
    session_id: str
    overall_score: int = 0
    performance_level: str = ""
    score_breakdown: Dict[str, str] = {}
    strengths: list = []
    improvements: list = []
    evaluator_complete: bool = False

@router.post("/evaluate/{session_id}")
async def evaluate_pitch(
    session_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Evaluate a completed pitch session
    
    Args:
        session_id: Session to evaluate
        db: Database session
        
    Returns:
        Evaluation results
    """
    try:
        result = evaluator_service.evaluate_pitch(session_id, db)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{session_id}")
async def get_evaluation_status(
    session_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get evaluation status for a session
    
    Args:
        session_id: Session identifier
        db: Database session
        
    Returns:
        Evaluation status and results if available
    """
    try:
        status = evaluator_service.get_evaluation_status(session_id, db)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/result/{session_id}")
async def get_evaluation_result(
    session_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get existing evaluation results (backward compatibility)
    
    Args:
        session_id: Session identifier
        db: Database session
        
    Returns:
        Evaluation results if available
    """
    status = evaluator_service.get_evaluation_status(session_id, db)
    
    if not status.get("exists"):
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not status.get("evaluated"):
        return {
            "evaluated": False,
            "message": "Session not yet evaluated",
            "ready_for_evaluation": status.get("ready_for_evaluation", False)
        }
    
    return {
        "evaluated": True,
        "overall_score": status.get("overall_score", 0),
        "strengths": status.get("strengths", ""),
        "improvements": status.get("improvements", ""),
        "detailed_feedback": status.get("detailed_feedback", "")
    }