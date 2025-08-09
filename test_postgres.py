# create a file called check_db.py in your project root
from pitchquest_api.database import SessionLocal
from pitchquest_api import crud

def check_session_state():
    db = SessionLocal()
    try:
        session_id = "test-session-001"
        
        print("🔍 SESSION DATA:")
        print("=" * 50)
        session = crud.get_session(db, session_id)
        if session:
            print(f"Session ID: {session.id}")
            print(f"Current Phase: {session.current_phase}")
            print(f"Mentor Complete: {session.mentor_complete}")
            print(f"Student Info:")
            print(f"  - Name: {session.student_name}")
            print(f"  - Hobby: {session.student_hobby}")
            print(f"  - Age: {session.student_age}")
            print(f"  - Location: {session.student_location}")
            print(f"  - Business Idea: {session.business_idea}")
            print(f"  - Target Audience: {session.target_audience}")
        else:
            print("❌ Session not found!")
        
        print("\n🔍 MESSAGE HISTORY:")
        print("=" * 50)
        messages = crud.get_messages_by_session(db, session_id)
        for i, msg in enumerate(messages, 1):
            print(f"Message {i} ({msg.role}):")
            print(f"  Content: {msg.content[:100]}...")
            print(f"  Agent Type: {msg.agent_type}")
            print(f"  Created: {msg.created_at}")
            print()
            
    finally:
        db.close()

if __name__ == "__main__":
    check_session_state()