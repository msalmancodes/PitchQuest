# pitchquest_api/services/investor_service.py
"""
Investor Service - Web API integration for investor agent
Ensures complete state preservation and proper field mapping
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session as DatabaseSession
from datetime import datetime
import json
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Add the project root to Python path so we can import our agents
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import investor agent functions
from agents.investor_agent import (
    process_single_investor_message,
    InvestorState
)

# Import database models and CRUD operations - MATCH MENTOR PATTERN
from pitchquest_api import models, crud

class InvestorService:
    """Service layer for investor agent with complete state management"""
    
    def __init__(self):
        """Initialize investor service"""
        self.field_mappings = {
            # Orchestrator → Database field mappings
            "investor_persona": "selected_investor",
            "pitch_complete": "investor_complete",
            # These stay the same
            "mentor_complete": "mentor_complete",
            "student_ready_for_investor": "student_ready_for_investor"
        }
    
    def process_investor_message(
        self,
        session_id: str,
        user_message: str,
        db: DatabaseSession
    ) -> Dict[str, Any]:
        """
        Process investor message with COMPLETE state preservation
        
        Args:
            session_id: Unique session identifier
            user_message: User's message
            db: Database session
            
        Returns:
            Response with AI message and complete session status
        """
        
        # Step 1: Load COMPLETE session state from database
        current_state = self._load_complete_session_state(session_id, db)
        
        # Log state before processing
        logger.info(f"Investor state BEFORE: mentor_complete={current_state.get('mentor_complete')}, "
                   f"ready={current_state.get('student_ready_for_investor')}, "
                   f"persona={current_state.get('investor_persona')}")
        
        # Step 2: Process message through investor agent
        # The agent uses **state pattern to preserve ALL fields
        result = process_single_investor_message(current_state, user_message)
        
        # Step 3: Save COMPLETE updated state to database
        self._save_complete_session_state(
            session_id=session_id,
            updated_state=result['updated_state'],
            user_message=user_message,
            ai_response=result['ai_response'],
            db=db
        )
        
        # Log state after processing
        logger.info(f"Investor state AFTER: pitch_complete={result.get('pitch_complete')}, "
                   f"persona={result.get('investor_persona')}")
        
        # Step 4: Return response for API with all relevant fields
        return {
            "session_id": session_id,
            "response": result['ai_response'],
            # Investor-specific fields
            "pitch_complete": result.get('pitch_complete', False),
            "investor_persona": result.get('investor_persona'),
            "persona_selection_needed": result.get('persona_selection_needed', False),
            "ready_for_pitch": result.get('ready_for_pitch', False),
            "exchange_count": result.get('exchange_count', 0),
            # Preserve mentor fields for complete state visibility
            "mentor_complete": result['updated_state'].get('mentor_complete', True),
            "student_ready_for_investor": result['updated_state'].get('student_ready_for_investor', True),
            "current_phase": "evaluator" if result.get('pitch_complete') else "investor"
        }
    
    def _load_complete_session_state(self, session_id: str, db: DatabaseSession) -> InvestorState:
        """
        Load COMPLETE session state from database, preserving ALL fields
        
        Args:
            session_id: Session identifier
            db: Database session
            
        Returns:
            Complete InvestorState with all fields preserved
        """
        
        # Get session from database using crud
        db_session = crud.get_session(db, session_id)
        
        if not db_session:
            # Create default state for new sessions (shouldn't happen for investor)
            logger.warning(f"No session found for {session_id}, creating default investor state")
            return {
                "student_info": {},
                "messages": [],
                "exchange_count": 0,
                "pitch_complete": False,
                "mentor_complete": True,  # Assume mentor done if we're here
                "student_ready_for_investor": True
            }
        
        # Reconstruct COMPLETE student_info from database fields
        student_info = {}
        if db_session.student_name:
            student_info["name"] = db_session.student_name
        if db_session.student_hobby:
            student_info["hobby"] = db_session.student_hobby
        if db_session.student_location:
            student_info["location"] = db_session.student_location
        if db_session.business_idea:
            student_info["business_idea"] = db_session.business_idea
        if db_session.problem_audience:
            student_info["problem_audience"] = db_session.problem_audience
        
        # Load ALL conversation messages using crud
        messages = crud.get_messages_by_session(db, session_id)
        
        # Convert to agent format and filter for investor phase
        agent_messages = []
        investor_messages = []
        
        for msg in messages:
            msg_dict = {
                "role": msg.role,
                "content": msg.content
            }
            agent_messages.append(msg_dict)
            
            # Filter for investor-phase messages
            # Simple approach: if agent_type is investor
            if msg.agent_type == "investor":
                investor_messages.append(msg_dict)
        
        # Count exchanges (user messages in investor phase)
        exchange_count = len([m for m in investor_messages if m.get("role") == "user"])
        
        # Build COMPLETE state with ALL fields preserved
        state = {
            # Core student data
            "student_info": student_info,
            "messages": investor_messages,  # Only investor messages for agent processing
            
            # Investor-specific fields (map from database names)
            "exchange_count": exchange_count,
            "pitch_complete": db_session.investor_complete or False,
            
            # PRESERVE mentor fields (critical for state continuity)
            "mentor_complete": db_session.mentor_complete or False,
            "student_ready_for_investor": db_session.student_ready_for_investor or False,
            "question_count": db_session.question_count or 0,
            
            # Current phase tracking
            "current_phase": db_session.current_phase or "investor"
        }
        
        # Add investor persona if already selected
        if db_session.selected_investor:
            state["investor_persona"] = db_session.selected_investor
        
        logger.info(f"Loaded complete state for {session_id}: {list(state.keys())}")
        
        return state
    
    def _save_complete_session_state(
        self,
        session_id: str,
        updated_state: InvestorState,
        user_message: str,
        ai_response: str,
        db: DatabaseSession
    ):
        """
        Save COMPLETE session state to database, preserving ALL fields
        
        Args:
            session_id: Session identifier
            updated_state: Complete updated state from investor agent
            user_message: User's message
            ai_response: AI's response
            db: Database session
        """
        
        # Get existing session using crud
        db_session = crud.get_session(db, session_id)
        
        if not db_session:
            # Create new session (edge case - shouldn't normally happen)
            logger.warning(f"Creating new session in investor phase for {session_id}")
            session_data = {
                "id": session_id,
                "current_phase": "investor",
                "mentor_complete": True,
                "student_ready_for_investor": True
            }
            db_session = crud.create_session(db, session_data)
        
        # Prepare update data
        session_updates = {
            "current_phase": "investor"
        }
        
        # Map investor-specific fields (orchestrator names → database names)
        if "investor_persona" in updated_state:
            session_updates["selected_investor"] = updated_state["investor_persona"]
        
        if "pitch_complete" in updated_state:
            session_updates["investor_complete"] = updated_state["pitch_complete"]
        
        # PRESERVE mentor fields (don't overwrite with None)
        if "mentor_complete" in updated_state:
            session_updates["mentor_complete"] = updated_state["mentor_complete"]
        
        if "student_ready_for_investor" in updated_state:
            session_updates["student_ready_for_investor"] = updated_state["student_ready_for_investor"]
        
        if "question_count" in updated_state:
            session_updates["question_count"] = updated_state["question_count"]
        
        # Update student info (might be enriched during investor phase)
        student_info = updated_state.get("student_info", {})
        if student_info:
            # Only update if values exist (don't overwrite with None)
            if student_info.get("name"):
                session_updates["student_name"] = student_info["name"]
            if student_info.get("hobby"):
                session_updates["student_hobby"] = student_info["hobby"]
            if student_info.get("location"):
                session_updates["student_location"] = student_info["location"]
            if student_info.get("business_idea"):
                session_updates["business_idea"] = student_info["business_idea"]
            if student_info.get("problem_audience"):
                session_updates["problem_audience"] = student_info["problem_audience"]
        
        # Update session using crud
        crud.update_session(db, session_id, session_updates)
        
        # Save conversation messages using crud
        if user_message:
            user_msg_data = {
                "session_id": session_id,
                "role": "user",
                "content": user_message,
                "agent_type": "investor"
            }
            crud.create_message(db, user_msg_data)
        
        if ai_response:
            ai_msg_data = {
                "session_id": session_id,
                "role": "assistant",
                "content": ai_response,
                "agent_type": "investor"
            }
            crud.create_message(db, ai_msg_data)
        
        logger.info(f"Saved complete state for {session_id}: "
                   f"investor_persona={session_updates.get('selected_investor')}, "
                   f"pitch_complete={session_updates.get('investor_complete')}")
    
    def get_session_status(self, session_id: str, db: DatabaseSession) -> Dict[str, Any]:
        """
        Get complete session status for monitoring
        
        Args:
            session_id: Session identifier
            db: Database session
            
        Returns:
            Complete session status
        """
        db_session = crud.get_session(db, session_id)
        
        if not db_session:
            return {"error": "Session not found"}
        
        messages = crud.get_messages_by_session(db, session_id)
        investor_messages = [m for m in messages if m.agent_type == "investor"]
        
        return {
            "session_id": session_id,
            "current_phase": db_session.current_phase,
            # Mentor status
            "mentor_complete": db_session.mentor_complete,
            "student_ready_for_investor": db_session.student_ready_for_investor,
            # Investor status
            "selected_investor": db_session.selected_investor,
            "investor_complete": db_session.investor_complete,
            # Student info
            "student_name": db_session.student_name,
            "business_idea": db_session.business_idea,
            # Message count
            "total_messages": len(messages),
            "investor_messages": len(investor_messages)
        }

# Create singleton instance
investor_service = InvestorService()

# Test function for direct testing
def test_investor_service():
    """Test the investor service with complete state management"""
    from pitchquest_api.database import SessionLocal
    
    print("🧪 Testing Investor Service with State Preservation")
    print("=" * 60)
    
    db = SessionLocal()
    service = InvestorService()
    
    # Create a test session with mentor data
    test_session_id = f"test_investor_{datetime.now().timestamp()}"
    
    # Simulate mentor completion using crud
    session_data = {
        "id": test_session_id,
        "current_phase": "mentor",
        "mentor_complete": True,
        "student_ready_for_investor": True,
        "student_name": "Test Student",
        "student_hobby": "coding",
        "business_idea": "AI tutoring platform"
    }
    test_session = crud.create_session(db, session_data)
    
    print(f"✅ Created test session: {test_session_id}")
    print(f"   Mentor complete: {test_session.mentor_complete}")
    print(f"   Ready for investor: {test_session.student_ready_for_investor}")
    
    # Test 1: Request persona selection
    print("\n📍 Test 1: Persona Selection")
    result1 = service.process_investor_message(
        session_id=test_session_id,
        user_message="start",
        db=db
    )
    print(f"   Persona selection needed: {result1['persona_selection_needed']}")
    print(f"   Mentor fields preserved: mentor_complete={result1['mentor_complete']}")
    
    # Test 2: Select persona
    print("\n📍 Test 2: Select Investor")
    result2 = service.process_investor_message(
        session_id=test_session_id,
        user_message="aria",
        db=db
    )
    print(f"   Selected: {result2['investor_persona']}")
    print(f"   Ready for pitch: {result2['ready_for_pitch']}")
    
    # Test 3: Start pitching
    print("\n📍 Test 3: Pitch Message")
    result3 = service.process_investor_message(
        session_id=test_session_id,
        user_message="I have an AI platform that helps students learn",
        db=db
    )
    print(f"   Exchange count: {result3['exchange_count']}")
    print(f"   Pitch complete: {result3['pitch_complete']}")
    
    # Verify state preservation
    print("\n📊 Final State Check:")
    status = service.get_session_status(test_session_id, db)
    print(f"   Current phase: {status['current_phase']}")
    print(f"   Mentor complete: {status['mentor_complete']} (preserved ✅)")
    print(f"   Ready for investor: {status['student_ready_for_investor']} (preserved ✅)")
    print(f"   Investor: {status['selected_investor']}")
    print(f"   Total messages: {status['total_messages']}")
    
    db.close()
    print("\n✅ Investor service test complete with state preservation!")

if __name__ == "__main__":
    test_investor_service()