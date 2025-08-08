# pitchquest_api/crud.py

"""
CRUD Operations for PitchQuest Database

ARCHITECTURAL PURPOSE:
- Separates database operations from business logic
- Provides clean interface between service layer and SQLAlchemy
- Handles all database queries and data persistence

PATTERN: Service Layer → CRUD → Database
"""

from sqlalchemy.orm import Session as DatabaseSession
from typing import Dict, Any, List, Optional

from . import models, schemas


# =============================================================================
# SESSION OPERATIONS
# =============================================================================

def get_session(db: DatabaseSession, session_id: str) -> Optional[models.Session]:
    """
    Get session by ID
    
    Args:
        db: Database session
        session_id: Unique session identifier
        
    Returns:
        Session model or None if not found
    """
    return db.query(models.Session).filter(models.Session.id == session_id).first()


def create_session(db: DatabaseSession, session_data: Dict[str, Any]) -> models.Session:
    """
    Create new session record
    
    Args:
        db: Database session
        session_data: Dictionary with session information
        
    Returns:
        Created session model
    """
    # Extract student_info if provided as dict, otherwise use individual fields
    student_info = session_data.get("student_info", {})
    
    db_session = models.Session(
        id=session_data["id"],
        current_phase=session_data.get("current_phase", "mentor"),
        mentor_complete=session_data.get("mentor_complete", False),
        investor_complete=session_data.get("investor_complete", False),
        evaluator_complete=session_data.get("evaluator_complete", False),
        
        # Map student_info dict to individual columns
        student_name=student_info.get("name") or session_data.get("student_name"),
        student_hobby=student_info.get("hobby") or session_data.get("student_hobby"),
        student_age=student_info.get("age") or session_data.get("student_age"),
        student_location=student_info.get("location") or session_data.get("student_location"),
        business_idea=student_info.get("business_idea") or session_data.get("business_idea"),
        target_audience=student_info.get("target_audience") or session_data.get("target_audience"),
        
        selected_investor=session_data.get("selected_investor")
    )
    
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def update_session(db: DatabaseSession, session_id: str, updates: Dict[str, Any]) -> Optional[models.Session]:
    """
    Update existing session
    
    Args:
        db: Database session
        session_id: Session to update
        updates: Dictionary of fields to update
        
    Returns:
        Updated session model or None if not found
    """
    db_session = get_session(db, session_id)
    if not db_session:
        return None
    
    # Handle student_info dict if provided
    if "student_info" in updates:
        student_info = updates.pop("student_info")  # Remove from updates dict
        
        # Map student_info dict to individual columns
        if "name" in student_info:
            db_session.student_name = student_info["name"]
        if "hobby" in student_info:
            db_session.student_hobby = student_info["hobby"]
        if "age" in student_info:
            db_session.student_age = student_info["age"]
        if "location" in student_info:
            db_session.student_location = student_info["location"]
        if "business_idea" in student_info:
            db_session.business_idea = student_info["business_idea"]
        if "target_audience" in student_info:
            db_session.target_audience = student_info["target_audience"]
    
    # Update other allowed fields (only if they exist on the model)
    allowed_fields = {
        "current_phase", "mentor_complete", "investor_complete", "evaluator_complete",
        "student_name", "student_hobby", "student_age", "student_location", 
        "business_idea", "target_audience", "selected_investor"
    }
    
    for key, value in updates.items():
        if key in allowed_fields and hasattr(db_session, key):
            setattr(db_session, key, value)
    
    db.commit()
    db.refresh(db_session)
    return db_session


def delete_session(db: DatabaseSession, session_id: str) -> bool:
    """
    Delete session and all related data
    
    Args:
        db: Database session
        session_id: Session to delete
        
    Returns:
        True if deleted, False if not found
    """
    db_session = get_session(db, session_id)
    if not db_session:
        return False
    
    # Delete related messages and evaluations first (foreign key constraint)
    db.query(models.Message).filter(models.Message.session_id == session_id).delete()
    db.query(models.Evaluation).filter(models.Evaluation.session_id == session_id).delete()
    
    # Delete session
    db.delete(db_session)
    db.commit()
    return True


# =============================================================================
# MESSAGE OPERATIONS  
# =============================================================================

def get_messages_by_session(db: DatabaseSession, session_id: str) -> List[models.Message]:
    """
    Get all messages for a session, ordered by creation time
    
    Args:
        db: Database session
        session_id: Session to get messages for
        
    Returns:
        List of message models ordered by created_at
    """
    return (db.query(models.Message)
              .filter(models.Message.session_id == session_id)
              .order_by(models.Message.created_at)
              .all())


def create_message(db: DatabaseSession, message_data: Dict[str, Any]) -> models.Message:
    """
    Create new message record
    
    Args:
        db: Database session
        message_data: Dictionary with message information
        
    Returns:
        Created message model
    """
    db_message = models.Message(
        session_id=message_data["session_id"],
        role=message_data["role"],  # "user" or "assistant"
        content=message_data["content"],
        agent_type=message_data.get("agent_type", "mentor")  # "mentor", "investor", "evaluator"
    )
    
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message


def get_messages_by_agent(db: DatabaseSession, session_id: str, agent_type: str) -> List[models.Message]:
    """
    Get messages for specific agent in a session
    
    Args:
        db: Database session
        session_id: Session ID
        agent_type: "mentor", "investor", or "evaluator"
        
    Returns:
        List of messages for that agent
    """
    return (db.query(models.Message)
              .filter(models.Message.session_id == session_id)
              .filter(models.Message.agent_type == agent_type)
              .order_by(models.Message.created_at)
              .all())


# =============================================================================
# EVALUATION OPERATIONS
# =============================================================================

def create_evaluation(db: DatabaseSession, evaluation_data: Dict[str, Any]) -> models.Evaluation:
    """
    Create evaluation record (from evaluator agent)
    
    Args:
        db: Database session
        evaluation_data: Dictionary with evaluation information
        
    Returns:
        Created evaluation model
    """
    db_evaluation = models.Evaluation(
        session_id=evaluation_data["session_id"],
        overall_score=evaluation_data.get("overall_score"),
        hook_score=evaluation_data.get("hook_score"),
        problem_score=evaluation_data.get("problem_score"),
        solution_score=evaluation_data.get("solution_score"),
        strengths=evaluation_data.get("strengths", ""),
        improvements=evaluation_data.get("improvements", ""),
        detailed_feedback=evaluation_data.get("detailed_feedback", "")
    )
    
    db.add(db_evaluation)
    db.commit()
    db.refresh(db_evaluation)
    return db_evaluation


def get_evaluation_by_session(db: DatabaseSession, session_id: str) -> Optional[models.Evaluation]:
    """
    Get evaluation for a session
    
    Args:
        db: Database session
        session_id: Session ID
        
    Returns:
        Evaluation model or None if not found
    """
    return db.query(models.Evaluation).filter(models.Evaluation.session_id == session_id).first()


# =============================================================================
# ANALYTICS & INSTRUCTOR OPERATIONS
# =============================================================================

def get_all_sessions(db: DatabaseSession, limit: int = 100) -> List[models.Session]:
    """
    Get all sessions for instructor insights
    
    Args:
        db: Database session
        limit: Maximum sessions to return
        
    Returns:
        List of session models
    """
    return (db.query(models.Session)
              .order_by(models.Session.created_at.desc())
              .limit(limit)
              .all())


def get_completed_sessions(db: DatabaseSession) -> List[models.Session]:
    """
    Get sessions that completed all phases (for instructor analytics)
    
    Returns:
        List of completed sessions
    """
    return (db.query(models.Session)
              .filter(models.Session.mentor_complete == True)
              .filter(models.Session.investor_complete == True)
              .filter(models.Session.evaluator_complete == True)
              .order_by(models.Session.created_at.desc())
              .all())


def get_session_transcript(db: DatabaseSession, session_id: str) -> Dict[str, List[models.Message]]:
    """
    Get complete transcript organized by agent type
    
    Args:
        db: Database session
        session_id: Session ID
        
    Returns:
        Dictionary with agent_type as keys, message lists as values
    """
    all_messages = get_messages_by_session(db, session_id)
    
    transcript = {
        "mentor": [],
        "investor": [], 
        "evaluator": []
    }
    
    for message in all_messages:
        agent_type = message.agent_type or "mentor"
        if agent_type in transcript:
            transcript[agent_type].append(message)
    
    return transcript


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def session_exists(db: DatabaseSession, session_id: str) -> bool:
    """Check if session exists"""
    return get_session(db, session_id) is not None


def get_session_stats(db: DatabaseSession, session_id: str) -> Dict[str, Any]:
    """
    Get session statistics
    
    Returns:
        Dictionary with session metrics
    """
    session = get_session(db, session_id)
    if not session:
        return {"exists": False}
    
    messages = get_messages_by_session(db, session_id)
    evaluation = get_evaluation_by_session(db, session_id)
    
    return {
        "exists": True,
        "created_at": session.created_at,
        "current_phase": session.current_phase,
        "mentor_complete": session.mentor_complete,
        "investor_complete": session.investor_complete,
        "evaluator_complete": session.evaluator_complete,
        "message_count": len(messages),
        "has_evaluation": evaluation is not None,
        "student_name": session.student_name,
        "student_hobby": session.student_hobby,
        "business_idea": session.business_idea
    }