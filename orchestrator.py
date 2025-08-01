# session_orchestrator.py - Complete Multi-Agent Workflow
from typing import TypedDict, Dict, Any, List, Literal
from langgraph.graph import StateGraph, END

# Import agents
from agents.mentor_agent import MentorState, mentor_node
from agents.investor_agent import InvestorState, investor_node
from agents.evaluator_agent import EvaluatorState, evaluator_node
from IPython.display import Image, display
# Define state types
class SessionState(TypedDict):
    """Complete session state combining all agents"""
    # Core student data
    student_info: Dict[str, Any]
    

    ## Mentor fields
    mentor_complete: bool
    question_count: int

    ## Investor fields
    messages: List[Dict[str, str]]
    investor_persona: str
    pitch_complete: bool
    exchange_count: int

    # Evaluator fields  
    evaluation_summary: Dict[str, Any]
    feedback_document_path: str
    evaluator_complete: bool

    # session phase
    current_phase: Literal["mentor", "investor", "evaluator", "complete"]




def visualize_workflow():
    """Display the workflow graph as an image"""
    
    # Create the graph
    graph = session_graph()
    
    try:
        # Generate and display the image
        img = graph.get_graph().draw_mermaid_png()
        display(Image(img))
        print("✅ Workflow diagram displayed above")
        
    except Exception as e:
        print(f"❌ Could not generate diagram: {e}")
        
        # Fallback: print text diagram
        print("📋 Workflow Structure:")
        print("START → MENTOR → INVESTOR → EVALUATOR → END")


def route_workflow(state: SessionState) -> str:
    """Determine next phase based on current state"""
    if not state.get("mentor_complete", False):
        return "mentor"
    elif not state.get("pitch_complete", False):
        return "investor"
    elif not state.get("evaluator_complete", False):
        return "evaluator"
    else:
        return "end"


def session_graph():
    """ create the complete mulit-agent workflow graph"""
    workflow = StateGraph(SessionState)

    # add agent nodes

    workflow.add_node("mentor", mentor_node)
    workflow.add_node("investor", investor_node)
    workflow.add_node("evaluator", evaluator_node)

    # set entry point
    workflow.set_entry_point("mentor")

    # add routing from agent 
    workflow.add_conditional_edges(
        'mentor',
        route_workflow,
        {
            "mentor": "mentor",
            "investor": "investor",
            "evaluator": "evaluator",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        'investor',
        route_workflow,
        {
            "mentor": "mentor",
            "investor": "investor",
            "evaluator": "evaluator",
            "end": END
        }
    )

    workflow.add_conditional_edges(
        'evaluator',
        route_workflow,
        {
            "mentor": "mentor",
            "investor": "investor",
            "evaluator": "evaluator",
            "end": END
        }
    )
    return workflow.compile()


def run_complete_session(initial_student_info: Dict[str, Any] = None) -> SessionState:
    """Run the complete mentor → investor → evaluator workflow"""
    
    print("🚀 Starting Complete AgentAcademy Session")
    print("=" * 50)
    
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
    
    print(f"📋 Initial phase: {initial_state['current_phase']}")
    
    # Create and run workflow
    try:
        graph = session_graph()
        print("✅ Workflow graph created successfully")
        
        print("\n🎯 Starting multi-agent workflow...")
        final_state = graph.invoke(initial_state)
        
        print(f"\n✅ Session Complete!")
        print(f"📊 Final phase: {final_state.get('current_phase', 'unknown')}")
        print(f"📈 Evaluation score: {final_state.get('evaluation_summary', {}).get('overall_score', 'N/A')}")
        print(f"📄 Feedback saved to: {final_state.get('feedback_document_path', 'N/A')}")
        
        return final_state
        
    except Exception as e:
        print(f"❌ Session failed: {e}")
        return initial_state


def save_workflow_diagram():
    """Save workflow diagram as PNG image file"""
    
    graph = session_graph()
    
    try:
        # Generate PNG image
        img_data = graph.get_graph().draw_mermaid_png()
        
        # Save to file
        with open("workflow_diagram.png", "wb") as f:
            f.write(img_data)
        
        print("✅ Workflow diagram saved as 'workflow_diagram.png'")
        print("📁 You can now open the file to view the diagram")
        
        # Also save Mermaid source
        mermaid_text = graph.get_graph().draw_mermaid()
        with open("workflow_diagram.mmd", "w") as f:
            f.write(mermaid_text)
        
        print("💾 Mermaid source saved as 'workflow_diagram.mmd'")
        
    except Exception as e:
        print(f"❌ Could not save diagram: {e}")
        print("📋 Fallback: Here's the workflow structure")
        print("MENTOR → INVESTOR → EVALUATOR → END")

def visualize_workflow():
    """Save and show how to view workflow diagram"""
    
    print("🎨 Generating Workflow Diagram...")
    save_workflow_diagram()
    
    print("\n📖 How to view:")
    print("1. Open 'workflow_diagram.png' in any image viewer")
    print("2. Or paste 'workflow_diagram.mmd' content at https://mermaid.live/")


def test_orchestrator():
    """Test the complete orchestrator workflow"""
    print("🧪 Testing Session Orchestrator")
    print("=" * 50)

    # visualize the workflow
    visualize_workflow()
    
    # Sample student info
    test_student_info = {
        "name": "TestStudent",
        "hobby": "AI applications", 
        "business_idea": "Educational platform"
    }
    
    print("Running complete session...")
    result = run_complete_session(test_student_info)
    
    print(f"✅ Test complete!")
    return result

if __name__ == "__main__":
    test_orchestrator()