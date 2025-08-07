from pydantic import BaseModel, Field
from typing import Optional, List
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