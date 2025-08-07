from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base

class Session(Base):
    __tablename__ = "sessions"

    id = Column(String, primary_key=True, index=True) # uuid string 
    student_name = Column(String, nullable=True)
    student_hobby = Column(String, nullable=True)
    student_age = Column(Integer, nullable=True)
    student_location = Column(String, nullable=True)


    # workflow state
    current_phase = Column(String, default="mentor")
    mentor_complete = Column(Boolean, default=False)
    investor_complete = Column(Boolean, default=False)
    evaluator_complete = Column(Boolean, default=False)

    # Business idea info
    business_idea = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    
    # Investor selection
    selected_investor = Column(String, nullable=True)  # aria_iyer, anna_ito, adam_ingram
    

    #Timestamps 

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relations 
    messages = relationship("Message", back_populates="session")
    evaluations = relationship("Evaluation", back_populates="session", uselist=False)



class Message(Base):

    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))

    #Message Details

    agent_type = Column(String)
    role = Column(String)
    content = Column(Text)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    # Relations
    session = relationship("Session", back_populates="messages")


class Evaluation(Base):
    __tablename__ = "evaluations"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))

    #Evaluation scores 
    overall_score = Column(Integer, nullable=True)
    hook_score = Column(Integer, nullable=True)
    problem_score = Column(Integer, nullable=True)
    solution_score = Column(Integer, nullable=True)
    
    # Detailed Feedback
    strengths = Column(Text, nullable=True)
    improvements = Column(Text, nullable=True)
    detailed_feedback = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())

    # Relations
    session = relationship("Session", back_populates="evaluations")


