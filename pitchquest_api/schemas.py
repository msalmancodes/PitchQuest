from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# Session Schemas
class SessionCreate(BaseModel):
    student_name: Optional[str] = None
    student_hobby: Optional[str] = None
    student_age: Optional[int] = None
    student_location: Optional[str] = None

class SessionResponse(BaseModel):
    id: str
    student_name: Optional[str]
    student_hobby: Optional[str] 
    student_age: Optional[int]
    student_location: Optional[str]
    current_phase: str
    mentor_complete: bool
    investor_complete: bool
    evaluator_complete: bool
    business_idea: Optional[str]
    target_audience: Optional[str]
    selected_investor: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy models

class SessionUpdate(BaseModel):
    business_idea: Optional[str] = None
    target_audience: Optional[str] = None
    selected_investor: Optional[str] = None
    current_phase: Optional[str] = None
    mentor_complete: Optional[bool] = None
    investor_complete: Optional[bool] = None

# Message Schemas
class MessageCreate(BaseModel):
    content: str
    role: str = Field(..., pattern="^(user|assistant)$")  # ✅ Updated to use 'pattern'

class MessageResponse(BaseModel):
    id: int
    session_id: str
    agent_type: str
    role: str
    content: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Agent Response Schemas
class AgentResponse(BaseModel):
    response: str
    session_updated: bool = False
    next_phase: Optional[str] = None
    conversation_complete: bool = False

# =============================================================================
# MENTOR-SPECIFIC SCHEMAS
# =============================================================================

class MentorMessageRequest(BaseModel):
    """
    Schema for mentor conversation requests
    
    PURPOSE: Handles mentor-specific conversation input with session tracking
    """
    session_id: Optional[str] = None  # Auto-generated if not provided
    content: str = Field(..., min_length=1, max_length=1000)
    agent_type: str = Field(default="mentor", pattern="^mentor$")  # Always "mentor" for this endpoint

class MentorMessageResponse(BaseModel):
    """
    Schema for mentor conversation responses
    
    PURPOSE: Structured response from mentor agent with session status
    """
    success: bool
    ai_response: str
    session_id: str
    mentor_complete: bool
    student_ready_for_investor: bool
    question_count: int
    student_info: Dict[str, Any]
    next_phase: str
    error: Optional[str] = None

class MentorStatusResponse(BaseModel):
    """
    Schema for mentor session status responses
    
    PURPOSE: Get current mentor session state without processing a message
    """
    success: bool
    session_exists: bool
    session_id: str
    message_count: int
    question_count: int
    mentor_complete: bool
    student_ready_for_investor: bool
    student_info: Dict[str, Any]
    current_phase: str

class MentorSessionCreate(BaseModel):
    """
    Schema for creating new mentor sessions
    
    PURPOSE: Optional pre-creation of sessions with initial student data
    """
    student_name: Optional[str] = None
    student_hobby: Optional[str] = None
    student_age: Optional[int] = None
    student_location: Optional[str] = None