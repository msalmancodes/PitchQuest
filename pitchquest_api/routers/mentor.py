# pitchquest_api/routers/mentor.py

"""
Mentor API Endpoints

ARCHITECTURAL PURPOSE:
- Exposes mentor agent functionality via HTTP endpoints
- Handles request validation and response formatting
- Integrates with mentor service layer

ENDPOINTS:
- POST /api/mentor/message - Process mentor conversation message
- GET /api/mentor/status/{session_id} - Get mentor session status  
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any
import uuid

from ..database import get_db
from ..services.mentor_service import mentor_service
from .. import schemas

router = APIRouter()

@router.post("/message", response_model=schemas.MentorMessageResponse)
async def process_mentor_message(
    message_request: schemas.MentorMessageRequest,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Process a mentor conversation message
    
    FLOW:
    1. Validate request (Pydantic does this automatically)
    2. Call mentor service to process message
    3. Return structured response
    
    Args:
        message_request: Validated request containing session_id and content
        db: Database session (injected by FastAPI)
        
    Returns:
        Dict with AI response and session status
    """
    
    try:
        # Extract session_id, create if not provided
        session_id = message_request.session_id or str(uuid.uuid4())
        
        # Process message through service layer
        result = mentor_service.process_mentor_message(
            session_id=session_id,
            user_message=message_request.content,
            db=db
        )
        
        # Return service result directly (it's already web-formatted)
        return result
        
    except Exception as e:
        # FastAPI error handling
        raise HTTPException(
            status_code=500,
            detail=f"Mentor processing error: {str(e)}"
        )


@router.get("/status/{session_id}", response_model=schemas.MentorStatusResponse)
async def get_mentor_status(
    session_id: str,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Get mentor session status without processing a message
    
    USEFUL FOR:
    - Frontend checking session state
    - Resuming conversations after page refresh
    - Progress tracking
    
    Args:
        session_id: Session identifier
        db: Database session (injected by FastAPI)
        
    Returns:
        Dict with session status and progress
    """
    
    try:
        # Get status through service layer
        status = mentor_service.get_session_status(session_id, db)
        return {
            "success": True,
            "session_id": session_id,
            **status
        }
        
    except Exception as e:
        # FastAPI error handling
        raise HTTPException(
            status_code=500,
            detail=f"Status retrieval error: {str(e)}"
        )


@router.post("/session/new", response_model=schemas.MentorStatusResponse)
async def create_mentor_session(
    session_data: schemas.MentorSessionCreate,
    db: Session = Depends(get_db)
) -> Dict[str, Any]:
    """
    Create a new mentor session
    
    OPTIONAL ENDPOINT:
    - Can be used to pre-create sessions with student info
    - Alternative: sessions auto-create on first message
    
    Args:
        session_data: Initial session information
        db: Database session
        
    Returns:
        Dict with new session info
    """
    
    try:
        # Generate session ID if not provided
        session_id = str(uuid.uuid4())
        
        # Get initial status (this will create session if needed)
        status = mentor_service.get_session_status(session_id, db)
        
        return {
            "success": True,
            "session_id": session_id,
            "message": "Mentor session created successfully",
            **status
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Session creation error: {str(e)}"
        )