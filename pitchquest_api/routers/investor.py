# routers/investor.py
"""
Investor API Router - Handles investor pitch sessions
Supports persona selection and pitch conversation flow
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
from pydantic import BaseModel

from ..database import get_db
from ..services.investor_service import investor_service  # ← CORRECT IMPORT

# Create router with prefix and tags
router = APIRouter()

# Define request/response models directly here for now
class InvestorMessageRequest(BaseModel):
    session_id: str
    message: str

class InvestorMessageResponse(BaseModel):
    session_id: str
    response: str
    phase_complete: bool
    next_phase: str
    metadata: Dict[str, Any]

@router.post("/message", response_model=InvestorMessageResponse)
async def process_investor_message(
    request: InvestorMessageRequest,
    db: Session = Depends(get_db)
) -> InvestorMessageResponse:
    """
    Process investor conversation message
    
    Handles both:
    1. Persona selection (first interaction)
    2. Pitch conversation (after persona selected)
    """
    try:
        # Process message through investor service
        result = investor_service.process_investor_message(
            session_id=request.session_id,
            user_message=request.message,
            db=db
        )
        
        # Return structured response
        return InvestorMessageResponse(
            session_id=result["session_id"],
            response=result["response"],
            phase_complete=result.get("pitch_complete", False),
            next_phase="evaluator" if result.get("pitch_complete") else "investor",
            metadata={
                "investor_persona": result.get("investor_persona"),
                "persona_selection_needed": result.get("persona_selection_needed", False),
                "ready_for_pitch": result.get("ready_for_pitch", False),
                "exchange_count": result.get("exchange_count", 0),
                "pitch_complete": result.get("pitch_complete", False)
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{session_id}")
async def get_investor_status(
    session_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get investor session status
    """
    try:
        status = investor_service.get_session_status(session_id, db)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/start/{session_id}")
async def start_investor_session(
    session_id: str,
    db: Session = Depends(get_db)
) -> InvestorMessageResponse:
    """
    Start investor session - triggers persona selection
    """
    try:
        # Send "start" message to trigger persona selection
        result = investor_service.process_investor_message(
            session_id=session_id,
            user_message="start",
            db=db
        )
        
        return InvestorMessageResponse(
            session_id=result["session_id"],
            response=result["response"],
            phase_complete=False,
            next_phase="investor",
            metadata={
                "persona_selection_needed": True,
                "ready_for_pitch": False
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))