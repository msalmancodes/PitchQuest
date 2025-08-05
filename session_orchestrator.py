# simple_interactive_orchestrator.py - Working LangGraph Implementation
from typing import TypedDict, Dict, Any, List, Literal, Optional, Union
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import uuid
import logging
import sys
import time
from datetime import datetime

# Import your existing agents
from agents.mentor_agent import mentor_node, run_mentor_conversation
from agents.investor_agent import investor_node, run_investor_conversation  
from agents.evaluator_agent import evaluator_node

# Configure logging to hide HTTP requests
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Hide HTTP request logs
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)

class SessionState(TypedDict, total=False):
    """Complete session state - using total=False for flexibility"""
    # Core student data
    student_info: Dict[str, Any]
    messages: List[Dict[str, str]]
    
    # Mentor fields
    mentor_complete: bool
    student_ready_for_investor: bool
    question_count: int

    # Investor fields
    investor_persona: str
    pitch_complete: bool
    exchange_count: int

    # Evaluator fields  
    evaluation_summary: Dict[str, Any]
    feedback_document_path: str
    evaluator_complete: bool
    overall_score: Optional[Union[int, float]]

    # Session phase
    current_phase: Literal["mentor", "investor", "evaluator", "complete"]

# 🎨 CHATBOT UI FUNCTIONS

def print_header(title: str, subtitle: str = ""):
    """Print beautiful header for different phases"""
    print("\n" + "═" * 80)
    print(f"🎓 {title}")
    if subtitle:
        print(f"   {subtitle}")
    print("═" * 80)

def print_agent_message(agent_name: str, message: str, emoji: str = "🤖"):
    """Print agent message in chatbot style"""
    timestamp = datetime.now().strftime("%H:%M")
    print(f"\n┌─ {emoji} {agent_name} ({timestamp})")
    print("│")
    # Word wrap for better readability
    words = message.split()
    line = "│ "
    for word in words:
        if len(line + word) > 75:
            print(line)
            line = "│ " + word + " "
        else:
            line += word + " "
    if line.strip() != "│":
        print(line)
    print("└─" + "─" * 77)

def print_user_prompt():
    """Print user input prompt in chatbot style"""
    timestamp = datetime.now().strftime("%H:%M")
    print(f"\n┌─ 👤 You ({timestamp})")
    print("│")
    user_input = input("│ ").strip()
    print("└─" + "─" * 77)
    return user_input

def print_phase_transition(from_phase: str, to_phase: str, reason: str = ""):
    """Print beautiful phase transition"""
    print("\n" + "▓" * 80)
    print(f"🔄 TRANSITIONING: {from_phase.upper()} → {to_phase.upper()}")
    if reason:
        print(f"   Reason: {reason}")
    print("▓" * 80)
    time.sleep(1)  # Brief pause for effect

def print_session_complete(score: int, performance: str, feedback_path: str):
    """Print final session results in beautiful format"""
    print("\n" + "★" * 80)
    print("🎉 SESSION COMPLETE - CONGRATULATIONS!")
    print("★" * 80)
    print(f"📊 Overall Score: {score}/100")
    print(f"📈 Performance Level: {performance.upper()}")
    print(f"📄 Detailed Feedback: {feedback_path}")
    print("★" * 80)

# 🎯 WORKFLOW DIAGRAM FUNCTIONS

def save_workflow_diagram():
    """Save workflow diagram as PNG and Mermaid"""
    try:
        graph = create_simple_interactive_graph()
        
        # Generate PNG image
        img_data = graph.get_graph().draw_mermaid_png()
        
        # Save to file
        with open("simple_interactive_workflow.png", "wb") as f:
            f.write(img_data)
        
        print("✅ Workflow diagram saved as 'simple_interactive_workflow.png'")
        
        # Also save Mermaid source
        mermaid_text = graph.get_graph().draw_mermaid()
        with open("simple_interactive_workflow.mmd", "w") as f:
            f.write(mermaid_text)
        
        print("✅ Mermaid source saved as 'simple_interactive_workflow.mmd'")
        print("📋 Expected flow: MENTOR → INVESTOR → EVALUATOR → END")
        
    except Exception as e:
        print(f"❌ Could not save diagram: {e}")
        print("💡 Diagram generation requires graphviz. Install with: pip install graphviz")

def display_workflow_info():
    """Display workflow information"""
    print_header("WORKFLOW ARCHITECTURE", "LangGraph Interactive Orchestrator")
    
    print("🏗️  WORKFLOW STRUCTURE:")
    print("   ┌─ MENTOR (interactive)")
    print("   │  ├─ Continue mentoring if not complete")
    print("   │  ├─ Go to INVESTOR if student ready")
    print("   │  └─ END if student not ready")
    print("   │")
    print("   ├─ INVESTOR (interactive)")
    print("   │  ├─ Continue pitching if not complete")
    print("   │  └─ Go to EVALUATOR if pitch complete")
    print("   │")
    print("   ├─ EVALUATOR (automated)")
    print("   │  └─ Always END after evaluation")
    print("   │")
    print("   └─ END")
    
    print(f"\n🔧 ROUTING LOGIC:")
    print("   • Mentor readiness assessment controls flow")
    print("   • State preserved across all transitions")
    print("   • Interactive functions wrapped in LangGraph nodes")
    print("   • Professional logging with HTTP requests hidden")
    
    print(f"\n🎯 SUCCESS CRITERIA:")
    print("   • Mentor: student_ready_for_investor = True")
    print("   • Investor: pitch_complete = True") 
    print("   • Evaluator: comprehensive feedback generated")

# Updated wrapper functions with beautiful UI
def interactive_mentor_wrapper(state: SessionState) -> SessionState:
    """Wrapper that uses your existing interactive mentor function with beautiful UI"""
    print_header("MENTOR SESSION", "Building Your Perfect Pitch")
    
    # Use your existing interactive function
    mentor_result = run_mentor_conversation()
    
    # Parse mentor's readiness assessment and extract student info from messages
    student_ready = True
    extracted_student_info = mentor_result.get("student_info", {})
    
    # Check the mentor's messages for both assessment and student info
    messages = mentor_result.get("messages", [])
    if messages:
        last_mentor_message = ""
        user_responses = []
        
        # Collect user responses and last mentor message
        for msg in messages:
            if msg.get("role") == "assistant":
                last_mentor_message = msg.get("content", "").lower()
            elif msg.get("role") == "user":
                user_responses.append(msg.get("content", "").lower())
        
        # Parse mentor's readiness assessment
        if "proceed_to_investor: no" in last_mentor_message:
            student_ready = False
            print_phase_transition("MENTOR", "ENDED", "Student needs more preparation")
        elif "proceed_to_investor: yes" in last_mentor_message:
            student_ready = True
            print_phase_transition("MENTOR", "INVESTOR", "Student is ready to pitch!")
        
        # Extract student info from user responses if mentor didn't capture it
        if not extracted_student_info or not any(extracted_student_info.values()):
            for response in user_responses:
                if "education" in response and "ai" in response:
                    extracted_student_info["business_idea"] = "Education and AI"
                    extracted_student_info["hobby"] = "Education technology"
    
    # Merge results into session state
    updated_state = {**state}
    updated_state.update({
        "student_info": extracted_student_info,
        "mentor_complete": mentor_result.get("mentor_complete", False),
        "student_ready_for_investor": student_ready,
        "question_count": mentor_result.get("question_count", 0),
        "current_phase": "investor" if mentor_result.get("mentor_complete") else "mentor"
    })
    
    logger.info(f"Mentor session completed. Ready for investor: {student_ready}")
    return updated_state

def interactive_investor_wrapper(state: SessionState) -> SessionState:
    """Wrapper that uses your existing interactive investor function with beautiful UI"""
    print_header("INVESTOR PITCH SESSION", "Time to Shine - Present Your Vision")
    
    # Get student info from mentor session
    student_info = state.get("student_info", {})
    business_idea = student_info.get("business_idea", "your business idea")
    
    print(f"📋 Pitching: {business_idea}")
    print("🎯 Remember: Be confident, clear, and compelling!")
    
    # Use your existing interactive function
    investor_result = run_investor_conversation(student_info)
    
    # Check if pitch was successful
    pitch_complete = investor_result.get("pitch_complete", False)
    investor_persona = investor_result.get("investor_persona", "Unknown")
    
    if pitch_complete:
        print_phase_transition("INVESTOR", "EVALUATOR", f"Pitch completed with {investor_persona.title()}")
    
    # Merge results into session state
    updated_state = {**state}
    updated_state.update({
        "messages": investor_result.get("messages", []),
        "investor_persona": investor_persona,
        "pitch_complete": pitch_complete,
        "exchange_count": investor_result.get("exchange_count", 0),
        "current_phase": "evaluator" if pitch_complete else "investor"
    })
    
    logger.info(f"Investor session completed. Pitch complete: {pitch_complete}")
    return updated_state

def evaluator_wrapper(state: SessionState) -> SessionState:
    """Wrapper for evaluator with beautiful UI"""
    print_header("PERFORMANCE EVALUATION", "Analyzing Your Pitch Excellence")
    
    print("🔍 Analyzing your conversation...")
    print("📊 Calculating performance metrics...")
    print("📝 Generating personalized feedback...")
    
    # Use your existing evaluator
    result = evaluator_node(state)
    
    # Extract evaluation results
    evaluation = result.get('evaluation_summary', {})
    score = evaluation.get('overall_score', 0)
    performance_level = evaluation.get('performance_level', 'unknown')
    feedback_path = result.get('feedback_document_path', 'No feedback file')
    
    # Show results with beautiful formatting
    print_session_complete(score, performance_level, feedback_path)
    
    result['current_phase'] = 'complete'
    logger.info(f"Evaluation completed. Score: {score}")
    
    return result

# Routing functions (your existing logic)
def should_continue_mentor(state: SessionState) -> str:
    """Route from mentor with fixed logic and debugging"""
    mentor_complete = state.get("mentor_complete", False)
    student_ready = state.get("student_ready_for_investor", False)
    
    # Add debugging
    logger.info(f"ROUTING: mentor_complete={mentor_complete}, student_ready={student_ready}")
    
    if mentor_complete and student_ready:
        logger.info("ROUTING: Going to investor")
        return "to_investor"
    elif mentor_complete and not student_ready:
        logger.info("ROUTING: Ending - student not ready")
        return "end_not_ready"
    else:
        logger.info("ROUTING: Continuing mentor")
        return "continue_mentor"

def should_continue_investor(state: SessionState) -> str:
    """Route from investor"""
    if state.get("pitch_complete", False):
        return "to_evaluator"
    else:
        return "continue_investor"

def should_continue_evaluator(state: SessionState) -> str:
    """Route from evaluator - always end"""
    return "end"

def create_simple_interactive_graph():
    """Create LangGraph with simple wrappers"""
    
    workflow = StateGraph(SessionState)

    # Add wrapper nodes that use your existing interactive functions
    workflow.add_node("mentor", interactive_mentor_wrapper)
    workflow.add_node("investor", interactive_investor_wrapper) 
    workflow.add_node("evaluator", evaluator_wrapper)

    # Set entry point
    workflow.set_entry_point("mentor")

    # Add routing logic
    workflow.add_conditional_edges(
        "mentor",
        should_continue_mentor,
        {
            "continue_mentor": "mentor",
            "to_investor": "investor",
            "end_not_ready": END
        }
    )

    workflow.add_conditional_edges(
        "investor", 
        should_continue_investor,
        {
            "continue_investor": "investor",
            "to_evaluator": "evaluator"
        }
    )

    workflow.add_conditional_edges(
        "evaluator",
        should_continue_evaluator, 
        {
            "end": END
        }
    )

    return workflow.compile()

def run_simple_interactive_session():
    """Run interactive session with beautiful chatbot UI"""
    
    # Welcome header
    print("\n" + "🌟" * 80)
    print("🎓 Welcome to AgentAcademy - Interactive AI Mentorship Platform")
    print("🚀 Powered by LangGraph • Professional Pitch Training")
    print("🌟" * 80)
    
    print("\n📋 SESSION OVERVIEW:")
    print("   🎓 Phase 1: Mentor - Develop your business idea")
    print("   💼 Phase 2: Investor - Practice your pitch")  
    print("   📊 Phase 3: Evaluator - Receive detailed feedback")
    
    # Initialize session state
    initial_state: SessionState = {
        "student_info": {},
        "messages": [],
        "mentor_complete": False,
        "student_ready_for_investor": False,
        "question_count": 0,
        "investor_persona": "",
        "pitch_complete": False,
        "exchange_count": 0,
        "evaluation_summary": {},
        "feedback_document_path": "",
        "evaluator_complete": False,
        "current_phase": "mentor"
    }
    
    try:
        # Create the graph
        graph = create_simple_interactive_graph()
        
        logger.info("Starting AgentAcademy session")
        print("\n🔥 Initializing AI agents...")
        time.sleep(1)
        print("✅ Session ready!")
        
        # Run the workflow - LangGraph will handle routing automatically
        final_state = graph.invoke(initial_state)
        
        # Check how the session ended
        current_phase = final_state.get('current_phase', 'unknown')
        student_ready = final_state.get('student_ready_for_investor', False)
        mentor_complete = final_state.get('mentor_complete', False)
        
        if mentor_complete and not student_ready:
            # Session ended because student wasn't ready
            print_header("SESSION ENDED", "Mentor Recommendation: More Preparation Needed")
            
            print("📚 Your mentor has provided comprehensive feedback above.")
            print("💡 Take time to refine your business idea and return when ready!")
            print("🔄 Focus Areas:")
            print("   • Clarify your unique value proposition")
            print("   • Identify specific problems your solution solves")
            print("   • Research your target market and competition")
            print("   • Develop measurable success metrics")
            
            logger.info("Session ended - student not ready for investor")
            return final_state
        
        # Session completed successfully - results already shown by evaluator_wrapper
        logger.info("Session completed successfully")
        return final_state
        
    except Exception as e:
        print("\n❌ SESSION ERROR")
        print("═" * 50)
        print(f"Error: {e}")
        print("💡 Please try again or contact support")
        logger.error(f"Session failed: {e}")
        import traceback
        traceback.print_exc()
        return initial_state

def compare_approaches():
    """Compare different architectural approaches with beautiful formatting"""
    print_header("ARCHITECTURAL APPROACHES", "Evolution of Your LangGraph System")
    
    print("🏗️  ARCHITECTURE COMPARISON:")
    print()
    
    print("1️⃣ ORIGINAL (Manual Chaining):")  
    print("   ✅ Works perfectly for basic flow")
    print("   ✅ Simple to understand and debug")
    print("   ❌ No LangGraph orchestration benefits")
    print("   ❌ Manual state management")
    print("   ❌ Limited error recovery")
    
    print("\n2️⃣ CURRENT SYSTEM (LangGraph Wrappers):")
    print("   ✅ Full LangGraph orchestration with routing logic")
    print("   ✅ Preserves your existing interactive functions")
    print("   ✅ Professional UI with chatbot styling")
    print("   ✅ HTTP request logs hidden")
    print("   ✅ Workflow diagrams generated")
    print("   ✅ Robust error handling and logging")
    print("   ✅ Production-ready architecture")
    
    print("\n3️⃣ ADVANCED INTERACTIVE (Future Enhancement):")
    print("   🔮 Full pause/resume with advanced LangGraph APIs")
    print("   🔮 Real-time state streaming")
    print("   🔮 Advanced checkpointing and recovery")
    print("   🔮 Multi-user concurrent sessions")
    
    print(f"\n🎯 CURRENT STATUS: Production-Ready Success!")
    print("   Your system now combines the best of both worlds:")
    print("   • LangGraph orchestration with proper routing")
    print("   • Beautiful chatbot UI experience")
    print("   • Your existing interactive agent quality")
    print("   • Professional logging and error handling")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "compare":
            compare_approaches()
        elif command == "diagram":
            save_workflow_diagram()
        elif command == "info":
            display_workflow_info()
        elif command == "help":
            print_header("AGENTALCADEMY COMMANDS")
            print("🚀 Available commands:")
            print("   python session_orchestrator.py          # Run interactive session")
            print("   python session_orchestrator.py compare  # Compare architectures") 
            print("   python session_orchestrator.py diagram  # Generate workflow diagram")
            print("   python session_orchestrator.py info     # Show workflow information")
            print("   python session_orchestrator.py help     # Show this help")
        else:
            print(f"❌ Unknown command: {command}")
            print("💡 Use 'python session_orchestrator.py help' for available commands")
    else:
        # Default: Run interactive session
        run_simple_interactive_session()