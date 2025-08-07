from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import uuid

from ..database import get_db
from ..models import Session as SessionModel
from ..schemas import SessionCreate, SessionResponse, SessionUpdate

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

@router.post("/", response_model=SessionResponse)
async def create_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db)
):
    """Create a new learning session"""
    
    # Generate unique session ID
    session_id = str(uuid.uuid4())
    
    # Create new session in database
    db_session = SessionModel(
        id=session_id,
        student_name=session_data.student_name,
        student_hobby=session_data.student_hobby,
        student_age=session_data.student_age,
        student_location=session_data.student_location,
        current_phase="mentor"
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    
    return db_session

@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """Get session details"""
    
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    update_data: SessionUpdate,
    db: Session = Depends(get_db)
):
    """Update session information"""
    
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update fields that were provided
    for field, value in update_data.dict(exclude_unset=True).items():
        setattr(session, field, value)
    
    db.commit()
    db.refresh(session)
    
    return session