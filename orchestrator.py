# session_orchestrator.py - FIXED Multi-Agent Workflow
from typing import TypedDict, Dict, Any, List, Literal
from langgraph.graph import StateGraph, END

# Import agents
from agents.mentor_agent import MentorState, mentor_node
from agents.investor_agent import InvestorState, investor_node
from agents.evaluator_agent import EvaluatorState, evaluator_node

class SessionState(TypedDict):
    """Complete session state combining all agents"""
    # Core student data
    student_info: Dict[str, Any]
    
    # Mentor fields
    mentor_complete: bool
    student_ready_for_investor: bool  # NEW: Mentor's readiness assessment
    question_count: int

    # Investor fields
    messages: List[Dict[str, str]]
    investor_persona: str
    pitch_complete: bool
    exchange_count: int

    # Evaluator fields  
    evaluation_summary: Dict[str, Any]
    feedback_document_path: str
    evaluator_complete: bool

    # Session phase
    current_phase: Literal["mentor", "investor", "evaluator", "complete"]

# 🔧 FIX 1: THREE-WAY ROUTING FUNCTIONS
def should_continue_mentor(state: SessionState) -> str:
    """Route from mentor: continue mentor OR go to investor OR end if not ready"""
    if not state.get("mentor_complete", False):
        return "continue_mentor"  # Keep mentoring
    elif state.get("student_ready_for_investor", False):
        return "to_investor"      # Student is ready - proceed!
    else:
        return "end_not_ready"    # End gracefully - student needs more work

def should_continue_investor(state: SessionState) -> str:
    """Route from investor: continue investor OR go to evaluator"""
    if state.get("pitch_complete", False):
        return "to_evaluator"
    else:
        return "continue_investor"

def should_continue_evaluator(state: SessionState) -> str:
    """Route from evaluator: should always end"""
    return "end"

# 🔧 FIX 2: CLEAN LINEAR GRAPH CREATION
def create_session_graph():
    """Create the complete multi-agent workflow graph with LINEAR flow"""
    workflow = StateGraph(SessionState)

    # Add agent nodes
    workflow.add_node("mentor", mentor_node)
    workflow.add_node("investor", investor_node) 
    workflow.add_node("evaluator", evaluator_node)

    # Set entry point
    workflow.set_entry_point("mentor")

    # 🎯 ENHANCED THREE-WAY ROUTING
    # Mentor: loop, go to investor, or end if not ready
    workflow.add_conditional_edges(
        "mentor",
        should_continue_mentor,
        {
            "continue_mentor": "mentor",      # Loop back to mentor
            "to_investor": "investor",        # Move to investor (student ready)
            "end_not_ready": END             # End gracefully (student not ready)
        }
    )

    # Investor: loop or go to evaluator  
    workflow.add_conditional_edges(
        "investor", 
        should_continue_investor,
        {
            "continue_investor": "investor",  # Loop back to investor
            "to_evaluator": "evaluator"       # Move to evaluator
        }
    )

    # Evaluator: always end
    workflow.add_conditional_edges(
        "evaluator",
        should_continue_evaluator, 
        {
            "end": END                        # Always end
        }
    )

    return workflow.compile()

# 🧪 STATE TRANSFER DEBUGGING FUNCTIONS
def log_state_transfer(phase: str, state: SessionState):
    """Add logging to trace state transfers"""
    print(f"\n📊 STATE CHECK - {phase.upper()}:")
    print(f"  👤 Student Info: {bool(state.get('student_info'))}")
    print(f"  💬 Messages: {len(state.get('messages', []))}")
    print(f"  ✅ Mentor Complete: {state.get('mentor_complete', False)}")
    print(f"  🎓 Student Ready: {state.get('student_ready_for_investor', False)}")  # NEW
    print(f"  🎯 Pitch Complete: {state.get('pitch_complete', False)}")
    print(f"  📝 Evaluator Complete: {state.get('evaluator_complete', False)}")
    print(f"  🔄 Current Phase: {state.get('current_phase', 'unknown')}")

def run_complete_session_with_logging(initial_student_info: Dict[str, Any] = None) -> SessionState:
    """Run complete session with detailed state transfer logging"""
    
    print("🚀 DEBUGGING: Complete AgentAcademy Session with State Logging")
    print("=" * 70)
    
    # Initialize session state
    initial_state: SessionState = {
        "student_info": initial_student_info or {},
        "mentor_complete": False,
        "question_count": 0,
        "messages": [],
        "investor_persona": "",
        "pitch_complete": False, 
        "exchange_count": 0,
        "evaluation_summary": {},
        "feedback_document_path": "",
        "evaluator_complete": False,
        "current_phase": "mentor"
    }
    
    log_state_transfer("INITIAL", initial_state)
    
    try:
        graph = create_session_graph()
        print("\n✅ Fixed workflow graph created successfully!")
        
        print("\n🎯 Starting linear multi-agent workflow...")
        
        # 🔍 STEP-BY-STEP EXECUTION WITH LOGGING
        current_state = initial_state
        
        for step_output in graph.stream(current_state):
            for node_name, updated_state in step_output.items():
                print(f"\n🔄 Executed: {node_name.upper()}")
                log_state_transfer(f"AFTER_{node_name.upper()}", updated_state)
                current_state = updated_state
        
        print(f"\n🎉 SESSION COMPLETE!")
        print("=" * 70)
        print(f"📊 Final Score: {current_state.get('evaluation_summary', {}).get('overall_score', 'N/A')}")
        print(f"📄 Feedback File: {current_state.get('feedback_document_path', 'N/A')}")
        
        return current_state
        
    except Exception as e:
        print(f"❌ Session failed: {e}")
        import traceback
        traceback.print_exc()
        return initial_state

def run_complete_session(initial_student_info: Dict[str, Any] = None) -> SessionState:
    """Run the complete mentor → investor → evaluator workflow (no logging)"""
    
    print("🚀 Starting Complete AgentAcademy Session")
    print("=" * 50)
    
    # Initialize session state
    initial_state: SessionState = {
        "student_info": initial_student_info or {},
        "mentor_complete": False,
        "question_count": 0,
        "messages": [],
        "investor_persona": "aria",  # 🔧 FIX: Default to Aria instead of empty string
        "pitch_complete": False,
        "exchange_count": 0,
        "evaluation_summary": {},
        "feedback_document_path": "",
        "evaluator_complete": False,
        "current_phase": "mentor"
    }
    
    try:
        graph = create_session_graph()
        print("✅ Workflow graph created successfully")
        
        print("\n🎯 Starting multi-agent workflow...")
        final_state = graph.invoke(initial_state)
        
        print(f"\n✅ Session Complete!")
        print(f"📊 Final Score: {final_state.get('evaluation_summary', {}).get('overall_score', 'N/A')}")
        print(f"📄 Feedback saved to: {final_state.get('feedback_document_path', 'N/A')}")
        
        return final_state
        
    except Exception as e:
        print(f"❌ Session failed: {e}")
        return initial_state

def save_workflow_diagram():
    """Save clean workflow diagram as PNG"""
    graph = create_session_graph()
    
    try:
        # Generate PNG image
        img_data = graph.get_graph().draw_mermaid_png()
        
        # Save to file
        with open("clean_workflow_diagram.png", "wb") as f:
            f.write(img_data)
        
        print("✅ Clean workflow diagram saved as 'clean_workflow_diagram.png'")
        
        # Also save Mermaid source
        mermaid_text = graph.get_graph().draw_mermaid()
        with open("clean_workflow_diagram.mmd", "w") as f:
            f.write(mermaid_text)
        
        print("💾 Mermaid source saved as 'clean_workflow_diagram.mmd'")
        print("📋 Expected flow: MENTOR → INVESTOR → EVALUATOR → END")
        
    except Exception as e:
        print(f"❌ Could not save diagram: {e}")

def run_interactive_session():
    """Run complete interactive session using individual agent conversation functions"""
    
    print("🎓 Welcome to AgentAcademy - Interactive Multi-Agent Experience!")
    print("=" * 65)
    print("You'll have real conversations with: MENTOR → INVESTOR → EVALUATOR")
    print("=" * 65)
    
    try:
        # Import the individual interactive functions
        from agents.mentor_agent import run_mentor_conversation
        from agents.investor_agent import run_investor_conversation
        from agents.evaluator_agent import evaluator_node
        
        # PHASE 1: Interactive Mentor Conversation
        print("\n🎓 PHASE 1: MENTOR SESSION")
        print("=" * 40)
        print("Your AI mentor will help you develop your business idea...")
        
        mentor_result = run_mentor_conversation()
        
        # Check if mentor session completed successfully
        if not mentor_result.get("mentor_complete", False):
            print("\n⚠️ Mentor session didn't complete properly.")
            return mentor_result
        
        print(f"\n✅ Mentor session complete!")
        print(f"📊 Student info collected: {list(mentor_result['student_info'].keys())}")
        
        # Check if student is ready for investor (if we implemented the readiness logic)
        student_ready = mentor_result.get("student_ready_for_investor", True)  # Default to True for now
        
        if not student_ready:
            print("\n🎓 MENTOR FEEDBACK: You need more preparation before facing an investor.")
            print("💡 Keep working on your business idea and come back when you're ready!")
            return mentor_result
        
        # PHASE 2: Interactive Investor Conversation  
        print("\n💼 PHASE 2: INVESTOR PITCH SESSION")
        print("=" * 40)
        print("Time to pitch your business idea to a real investor!")
        
        # Convert mentor state to investor-compatible format
        investor_input_state = {
            "student_info": mentor_result["student_info"],
            "messages": [],  # Fresh conversation for investor
            "investor_persona": "aria",  # Default persona
            "exchange_count": 0,
            "pitch_complete": False
        }
        
        investor_result = run_investor_conversation(mentor_result["student_info"])
        
        # Check if investor session completed
        if not investor_result.get("pitch_complete", False):
            print("\n⚠️ Investor session didn't complete properly.")
            return investor_result
            
        print(f"\n✅ Investor pitch session complete!")
        print(f"💼 Conversation length: {len(investor_result.get('messages', []))} exchanges")
        
        # PHASE 3: Automated Evaluator Analysis
        print("\n📊 PHASE 3: PERFORMANCE EVALUATION")
        print("=" * 40)
        print("Analyzing your pitch performance...")
        
        # Convert investor state to evaluator-compatible format
        evaluator_input_state = {
            **investor_result,  # Include all investor data
            "evaluation_summary": {},
            "feedback_document_path": "",
            "evaluator_complete": False
        }
        
        evaluator_result = evaluator_node(evaluator_input_state)
        
        # Show final results
        print(f"\n🎉 COMPLETE AGENTALACADEMY SESSION FINISHED!")
        print("=" * 65)
        
        evaluation_summary = evaluator_result.get("evaluation_summary", {})
        overall_score = evaluation_summary.get("overall_score", "N/A")
        performance_level = evaluation_summary.get("performance_level", "N/A")
        feedback_path = evaluator_result.get("feedback_document_path", "")
        
        print(f"📊 Your Overall Score: {overall_score}/100")
        print(f"📈 Performance Level: {performance_level}")
        print(f"📄 Detailed Feedback: {feedback_path}")
        
        if feedback_path:
            print(f"\n💡 Open '{feedback_path}' to read your complete evaluation!")
        
        return evaluator_result
        
    except Exception as e:
        print(f"❌ Interactive session failed: {e}")
        import traceback
        traceback.print_exc()
        return {}
    """Test state transfer with debugging"""
    print("🧪 DEBUGGING: State Transfer Investigation")
    print("=" * 60)
    
    # Sample student info
    test_student_info = {
        "name": "TestStudent",
        "hobby": "AI applications",
        "business_idea": "Educational platform",
        "location": "Boston"
    }
    
    print("📊 Testing with detailed state logging...")
    result = run_complete_session_with_logging(test_student_info)
    
    print(f"\n✅ State transfer test complete!")
    return result

def test_state_transfer():
    """Test state transfer with debugging"""
    print("🧪 DEBUGGING: State Transfer Investigation")
    print("=" * 60)
    
    # Sample student info
    test_student_info = {
        "name": "TestStudent",
        "hobby": "AI applications",
        "business_idea": "Educational platform",
        "location": "Boston"
    }
    
    print("📊 Testing with detailed state logging...")
    result = run_complete_session_with_logging(test_student_info)
    
    print(f"\n✅ State transfer test complete!")
    return result

def test_clean_orchestrator():
    """Test the fixed orchestrator"""
    print("🧪 Testing FIXED Session Orchestrator")
    print("=" * 50)

    # Generate clean diagram
    save_workflow_diagram()
    
    # Sample student info
    test_student_info = {
        "name": "TestStudent", 
        "hobby": "AI applications",
        "business_idea": "Educational platform"
    }
    
    print("\n🚀 Running complete session...")
    result = run_complete_session(test_student_info)
    
    print(f"✅ Test complete!")
    return result

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "debug":
        test_state_transfer()  # Debug with detailed logging
    elif len(sys.argv) > 1 and sys.argv[1] == "interactive":
        run_interactive_session()  # Interactive conversation mode
    else:
        # Show options to user
        print("🚀 AgentAcademy Orchestrator")
        print("=" * 50)
        print("Choose your mode:")
        print("1. Interactive Session (talk to agents)")  
        print("2. Debug Mode (detailed state logging)")
        print("3. Clean Test (automated testing)")
        
        choice = input("\nEnter choice (1, 2, or 3): ").strip()
        
        if choice == "1":
            run_interactive_session()
        elif choice == "2": 
            test_state_transfer()
        elif choice == "3":
            test_clean_orchestrator()
        else:
            print("Invalid choice. Running interactive mode...")
            run_interactive_session()