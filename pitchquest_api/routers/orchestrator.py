"""
Orchestrator Router - Single endpoint for seamless conversation flow

THE MAIN ENDPOINT: /api/orchestrator/message
- Handles entire conversation flow automatically
- Routes to mentor → investor → evaluator → complete
- Creates new sessions when needed
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas import OrchestratorMessageRequest, OrchestratorMessageResponse
from ..services.orchestrator_service import orchestrator_service

router = APIRouter()

@router.post("/message", response_model=OrchestratorMessageResponse)
async def process_message(
    request: OrchestratorMessageRequest, 
    db: Session = Depends(get_db)
):
    """
    🎯 THE UNIFIED ENDPOINT - Complete conversation flow
    
    This endpoint provides seamless experience:
    - Auto-generates session_id for new conversations
    - Routes to mentor → investor → evaluator automatically
    - Handles phase transitions based on completion status
    - Creates new sessions when current one ends
    - Mirrors your LangGraph routing logic exactly
    
    Request:
        session_id (optional): Existing session or auto-generated
        message: User's input message
        
    Response:
        Unified format with routing metadata and next steps
    """
    try:
        result = orchestrator_service.process_message(
            session_id=request.session_id,
            message=request.message,
            db=db
        )
        
        return OrchestratorMessageResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Orchestrator error: {str(e)}"
        )

@router.get("/health")
async def health_check():
    """Health check for orchestrator service"""
    return {
        "status": "healthy", 
        "service": "orchestrator",
        "message": "Ready to route messages seamlessly!",
        "features": [
            "Auto-routing based on session state",
            "Seamless phase transitions", 
            "Auto-triggered evaluation",
            "New session creation on completion"
        ]
    }
    