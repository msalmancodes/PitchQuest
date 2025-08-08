# pitchquest_api/services/mentor_service.py

"""
Mentor Web Service - Bridge between FastAPI and LangGraph Agent

ARCHITECTURAL PURPOSE:
- Converts stateless web requests into stateful agent conversations
- Handles database persistence for session state
- Wraps existing mentor_node logic for web interface

PATTERN:
Request → Load State → Process Message → Save State → Response
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session as DatabaseSession

# Add the project root to Python path so we can import our agents
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import your existing mentor agent logic
from agents.mentor_agent import process_single_mentor_message, MentorState

# Import database models and CRUD operations
from pitchquest_api import models, crud


class MentorService:
    """
    Service class that bridges web requests to your LangGraph mentor agent
    
    ARCHITECTURE EXPLANATION:
    - Each web request loads session state from database
    - Uses your existing process_single_mentor_message() function
    - Saves updated state back to database
    - Returns formatted response for web client
    """
    
    def __init__(self):
        """Initialize the mentor service"""
        pass
    
    def _load_session_state(self, session_id: str, db: DatabaseSession) -> MentorState:
        """
        Load current session state from database
        
        WHY THIS MATTERS:
        Web APIs are stateless - each request starts fresh
        But agents need conversation history to work properly
        So we reconstruct the state from database on each request
        
        Args:
            session_id: Unique session identifier
            db: Database session for queries
            
        Returns:
            MentorState: Current conversation state reconstructed from DB
        """
        print(f"🔍 Debug: Getting session from database...")
        
        # Get session from database with detailed error catching
        try:
            print(f"🔍 Debug: Calling crud.get_session...")
            db_session = crud.get_session(db, session_id)
            print(f"🔍 Debug: crud.get_session returned: {type(db_session)}")
        except Exception as e:
            print(f"❌ Error in crud.get_session: {e}")
            raise e
            
        print(f"🔍 Debug: db_session result: {db_session}")
        
        if not db_session:
            print(f"🔍 Debug: No session found, returning fresh state")
            # Return fresh state for new sessions
            return {
                "student_info": {},
                "messages": [],
                "question_count": 0,
                "exchange_count": 0,
                "mentor_complete": False,
                "student_ready_for_investor": False
            }
        
        print(f"🔍 Debug: Session found, getting messages...")
        # Get all messages for this session, ordered by creation time
        try:
            print(f"🔍 Debug: Calling crud.get_messages_by_session...")
            messages = crud.get_messages_by_session(db, session_id)
            print(f"🔍 Debug: Found {len(messages)} messages")
        except Exception as e:
            print(f"❌ Error getting messages: {e}")
            raise e
        
        # Convert database messages to agent format
        agent_messages = []
        for msg in messages:
            agent_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # CRITICAL FIX: Reconstruct student_info from individual database columns
        student_info = {}
        
        try:
            print(f"🔍 Debug: Accessing student_name...")
            if db_session.student_name:
                student_info["name"] = db_session.student_name
                
            print(f"🔍 Debug: Accessing student_hobby...")  
            if db_session.student_hobby:
                student_info["hobby"] = db_session.student_hobby
                
            print(f"🔍 Debug: Accessing student_age...")
            if db_session.student_age:
                student_info["age"] = db_session.student_age
                
            print(f"🔍 Debug: Accessing student_location...")
            if db_session.student_location:
                student_info["location"] = db_session.student_location
                
            print(f"🔍 Debug: Accessing business_idea...")
            if db_session.business_idea:
                student_info["business_idea"] = db_session.business_idea
                
            print(f"🔍 Debug: Accessing target_audience...")
            if db_session.target_audience:
                student_info["target_audience"] = db_session.target_audience
        except Exception as e:
            print(f"❌ Error accessing session fields: {e}")
            raise e
        
        print(f"🔍 Debug: Reconstructed student_info: {student_info}")
        
        # Determine student readiness from mentor completion status
        # WHY: If mentor is complete, we assume student is ready (can be refined later)
        student_ready = db_session.mentor_complete
        
        print(f"🔍 Debug: About to return state...")
        # Reconstruct state from database data
        # WHY: Agent needs this exact state structure to work properly
        return {
            "student_info": student_info,
            "messages": agent_messages,
            "question_count": len([m for m in agent_messages if m["role"] == "assistant"]),
            "exchange_count": len(agent_messages),
            "mentor_complete": db_session.mentor_complete,
            "student_ready_for_investor": student_ready
        }
    
    def _save_session_state(self, session_id: str, updated_state: MentorState, 
                           new_message: Optional[str], ai_response: str, db: DatabaseSession):
        """
        Save updated session state back to database
        
        WHY THIS MATTERS:
        After agent processes the message, we need to persist:
        1. Updated session metadata (completion status, student info)
        2. New conversation messages (user input + AI response)
        3. Progress tracking for instructor insights
        
        Args:
            session_id: Session to update
            updated_state: New state from agent processing
            new_message: User's input message (if any)
            ai_response: Agent's response message
            db: Database session
        """
        
        # Update or create session record
        db_session = crud.get_session(db, session_id)
        if not db_session:
            # Create new session with individual fields
            session_data = {
                "id": session_id,
                "current_phase": "mentor",
                "mentor_complete": updated_state["mentor_complete"],
                
                # Map student_info dict to individual columns
                "student_name": updated_state["student_info"].get("name"),
                "student_hobby": updated_state["student_info"].get("hobby"),
                "student_age": updated_state["student_info"].get("age"),
                "student_location": updated_state["student_info"].get("location"),
                "business_idea": updated_state["student_info"].get("business_idea"),
                "target_audience": updated_state["student_info"].get("target_audience")
            }
            db_session = crud.create_session(db, session_data)
        else:
            # Update existing session with individual fields
            session_updates = {
                "mentor_complete": updated_state["mentor_complete"],
                
                # Map student_info dict to individual columns
                "student_name": updated_state["student_info"].get("name"),
                "student_hobby": updated_state["student_info"].get("hobby"), 
                "student_age": updated_state["student_info"].get("age"),
                "student_location": updated_state["student_info"].get("location"),
                "business_idea": updated_state["student_info"].get("business_idea"),
                "target_audience": updated_state["student_info"].get("target_audience")
            }
            crud.update_session(db, session_id, session_updates)
        
        # Save new user message (if provided)
        if new_message and new_message.strip():
            user_msg_data = {
                "session_id": session_id,
                "role": "user",
                "content": new_message.strip(),
                "agent_type": "mentor"
            }
            crud.create_message(db, user_msg_data)
        
        # Save AI response message
        ai_msg_data = {
            "session_id": session_id,
            "role": "assistant", 
            "content": ai_response,
            "agent_type": "mentor"
        }
        crud.create_message(db, ai_msg_data)
    
    def process_mentor_message(self, session_id: str, user_message: str, db: DatabaseSession) -> Dict[str, Any]:
        """
        Main service method - processes one mentor conversation turn
        
        THIS IS THE CORE INTEGRATION FUNCTION
        
        FLOW EXPLANATION:
        1. Load current session state from database (conversation history)
        2. Use your existing agent logic to process the user message
        3. Save updated state and new messages to database
        4. Return structured response for web client
        
        Args:
            session_id: Unique session identifier for this conversation
            user_message: Student's input message
            db: Database session for persistence
            
        Returns:
            Dict with AI response and session status for web client
        """
        
        print(f"🔍 Debug: Starting process_mentor_message")
        print(f"🔍 Debug: session_id={session_id}, user_message='{user_message}'")
        print(f"🔍 Debug: db type: {type(db)}")
        
        try:
            print(f"🔍 Debug: About to call _load_session_state")
            # Step 1: Load current state from database
            # WHY: Agent needs conversation history to provide intelligent responses
            current_state = self._load_session_state(session_id, db)
            
            print(f"📂 Loaded session {session_id}: {len(current_state['messages'])} messages")
            print(f"🔍 Debug: Current state keys: {list(current_state.keys())}")
            
            # Step 2: Process message using your existing agent logic
            # WHY: This is where your LangGraph intelligence and YAML prompts work
            print(f"🔍 Debug: About to process message with agent logic")
            print(f"🔍 Debug: current_state type: {type(current_state)}")
            print(f"🔍 Debug: current_state keys: {list(current_state.keys())}")
            
            try:
                print(f"🔍 Debug: Calling process_single_mentor_message...")
                result = process_single_mentor_message(current_state, user_message)
                print(f"🔍 Debug: process_single_mentor_message succeeded")
            except Exception as e:
                print(f"❌ Error in process_single_mentor_message: {e}")
                import traceback
                traceback.print_exc()
                raise e
            
            print(f"🤖 Agent processed message, complete: {result['mentor_complete']}")
            print(f"🔍 Debug: Agent result keys: {list(result.keys())}")
            
            # Step 3: Save updated state to database
            # WHY: Web is stateless, so we must persist conversation for next request
            print(f"🔍 Debug: About to save session state")
            self._save_session_state(
                session_id=session_id,
                updated_state=result['updated_state'],
                new_message=user_message,
                ai_response=result['ai_response'],
                db=db
            )
            
            print(f"💾 Saved session state to database")
            
            # Step 4: Extract the AI response (last assistant message)
            ai_response = result['ai_response']
            
            # Step 5: Return web-friendly response
            # WHY: FastAPI needs structured JSON response with all status info
            return {
                "success": True,
                "ai_response": ai_response,
                "session_id": session_id,
                "mentor_complete": result.get("mentor_complete", False),
                "student_ready_for_investor": result.get("student_ready", False),
                "question_count": result.get("question_count", 0),
                "student_info": result.get("student_info", {}),
                "next_phase": "investor" if result.get("mentor_complete", False) else "mentor"
            }
            
        except Exception as e:
            # Error handling for production readiness
            print(f"❌ Error in mentor service: {str(e)}")
            return {
                "success": False,
                "error": f"Mentor service error: {str(e)}",
                "ai_response": "I'm having trouble right now. Please try again.",
                "session_id": session_id,
                "mentor_complete": False,
                "student_ready_for_investor": False,
                "question_count": 0,
                "student_info": {},
                "next_phase": "mentor"
            }
    
    def get_session_status(self, session_id: str, db: DatabaseSession) -> Dict[str, Any]:
        """
        Get current session status without processing a message
        
        USEFUL FOR:
        - Frontend to check session state
        - Resuming conversations after page refresh
        - Progress tracking and analytics
        """
        
        current_state = self._load_session_state(session_id, db)
        db_session = crud.get_session(db, session_id)
        
        return {
            "session_exists": db_session is not None,
            "message_count": len(current_state["messages"]),
            "question_count": current_state["question_count"],
            "mentor_complete": current_state["mentor_complete"],
            "student_ready_for_investor": current_state.get("student_ready_for_investor", False),
            "student_info": current_state["student_info"],
            "current_phase": "investor" if current_state["mentor_complete"] else "mentor"
        }


# Global service instance
# WHY: FastAPI will import this and use it in endpoints
mentor_service = MentorService()


# Testing function to verify service works before FastAPI integration
def test_mentor_service():
    """
    Test the service layer before connecting to FastAPI
    This simulates exactly how FastAPI will use the service
    """
    from pitchquest_api.database import SessionLocal
    
    print("🧪 Testing Mentor Service Layer...")
    print("=" * 60)
    
    # Create database session (like FastAPI dependency injection)
    db = SessionLocal()
    
    try:
        # Test conversation flow
        session_id = "test_service_session"
        
        print("📍 Test 1: Initial mentor interaction")
        result1 = mentor_service.process_mentor_message(
            session_id=session_id,
            user_message="Hi, I need help with my pitch",
            db=db
        )
        print(f"🤖 Response: {result1['ai_response']}")
        print(f"📊 Status: Complete={result1['mentor_complete']}, Ready={result1['student_ready_for_investor']}")
        
        if not result1["success"]:
            print(f"❌ Error in Test 1: {result1.get('error', 'Unknown error')}")
            return
        print()
        
        print("📍 Test 2: Provide student information")
        result2 = mentor_service.process_mentor_message(
            session_id=session_id,
            user_message="My hobby is photography and I want to create a photo editing app for beginners",
            db=db
        )
        print(f"🤖 Response: {result2['ai_response']}")
        
        if result2["success"]:
            print(f"📊 Student Info: {result2['student_info']}")
        else:
            print(f"❌ Error in Test 2: {result2.get('error', 'Unknown error')}")
            return
        print()
        
        print("📍 Test 3: Check session status")
        status = mentor_service.get_session_status(session_id, db)
        print(f"📊 Session Status: {status}")
        print()
        
        print("✅ Service layer working perfectly!")
        print("🎯 Ready for FastAPI endpoint integration!")
        
    finally:
        db.close()


if __name__ == "__main__":
    test_mentor_service()