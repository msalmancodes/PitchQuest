# import necessary libraries
from langgraph.graph import StateGraph, END # creates workflows
from typing import TypedDict, List, Dict, Any # for defining state structure 
from langchain_openai import ChatOpenAI # for LLM
from config import OPENAI_API_KEY, MODEL_NAME # for API key and model name
from prompts.mentor_prompt_loader import (
    get_mentor_system_prompt, 
    get_welcome_prompt, 
    get_extraction_prompt, 
    get_response_prompt,
    get_assessment_prompt,
    get_feedback_and_transition_prompt
)

class MentorState(TypedDict):
    """State struct for the mentor agent and overall system"""
    student_info: Dict[str, Any] # student info: hobby, experience etc
    messages: List[Dict[str, str]] # current conversation messages 
    mentor_complete: bool # whether the mentor has completed the conversation
    question_count: int # number of questions asked
    exchange_count: int # Tracking the number of exchanges

def mentor_node(state: MentorState) -> MentorState:
    """
    INTELLIGENT Mentor Agent node - uses YAML prompts for natural conversation
    Keeps your original structure but adds LLM-powered intelligence
    FIXED: Now preserves all state fields using **state pattern
    """
    # Your existing setup code - UNCHANGED
    messages = state.get("messages", [])
    student_info = state.get("student_info", {})
    question_count = state.get("question_count", 0)
    exchange_count = state.get("exchange_count", 0)  # NEW: Track exchanges
    
    # Your existing LLM initialization - UNCHANGED
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=MODEL_NAME,
        temperature=0.7
    )

    # CHANGE 1: Intelligent welcome message instead of hardcoded
    if question_count == 0:
        try:
            welcome_prompt = get_welcome_prompt()
            response = llm.invoke(welcome_prompt)
            mentor_response = response.content.strip()
        except:
            # Fallback to ensure it always works
            mentor_response = "Hi! I'm your mentor, here to help you prepare for pitching. What's your hobby, and do you have any business ideas you'd like to work on?"
        
        messages.append({"role": "assistant", "content": mentor_response})
        
        # 🔧 FIX 1: Preserve all state fields
        return {
            **state,  # ← PRESERVE all existing fields (investor_persona, pitch_complete, etc.)
            "student_info": student_info,
            "messages": messages,
            "question_count": 1,
            "exchange_count": 1,  # NEW: Initialize exchange count
            "mentor_complete": False,
            "student_ready_for_investor": False  # NEW: Initialize readiness
        }

    # CHANGE 2: Intelligent conversation logic instead of fixed questions
    elif question_count <= 10:  # NEW: Allow up to 10 exchanges instead of just 3
        # Your existing last_message logic - UNCHANGED
        last_message = ""
        if messages and messages[-1]["role"] == "user":
            last_message = messages[-1]["content"]

        # CHANGE 3: Enhanced info extraction using YAML prompts
        if question_count == 1:
            try:
                extraction_prompt = get_extraction_prompt(last_message)
                extraction_response = llm.invoke(extraction_prompt)
                lines = extraction_response.content.split('\n')
                
                for line in lines:
                    if line.startswith("Hobby:") and "none" not in line.lower():
                        student_info["hobby"] = line.replace('Hobby:', '').strip()
                    elif line.startswith('Business_idea:') and "none" not in line.lower():
                        student_info["business_idea"] = line.replace('Business_idea:', '').strip()
                    elif line.startswith('Name:') and "none" not in line.lower():
                        student_info["name"] = line.replace('Name:', '').strip()
                    elif line.startswith('Age:') and "none" not in line.lower():
                        student_info["age"] = line.replace('Age:', '').strip()
                    elif line.startswith('Location:') and "none" not in line.lower():
                        student_info["location"] = line.replace('Location:', '').strip()
            except:
                # Your original extraction as fallback
                if "guitar" in last_message.lower():
                    student_info["hobby"] = "guitar"

        # CHANGE 4: Check readiness after 4+ exchanges, force decision at 10
        if question_count >= 10:
            # Maximum exchanges reached - provide comprehensive feedback
            try:
                conversation_context = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in messages[-8:]])
                feedback_prompt = get_feedback_and_transition_prompt(conversation_context, question_count)
                
                response = llm.invoke(feedback_prompt)
                feedback_message = response.content.strip()
                
                # 🔧 CRITICAL FIX: Separate session completion from student readiness
                student_ready = (
                    "proceed_to_investor: yes" in feedback_message.lower() or 
                    ("proceed to investor" in feedback_message.lower() and "yes" in feedback_message.lower())
                )
                
                messages.append({"role": "assistant", "content": feedback_message})
                
                # 🔧 FIX 2: Always complete session after max exchanges, but set readiness separately
                return {
                    **state,  # ← PRESERVE all existing fields
                    "student_info": student_info,
                    "messages": messages,
                    "question_count": question_count + 1,
                    "exchange_count": exchange_count + 1,
                    "mentor_complete": True,  # ← ALWAYS complete after max exchanges
                    "student_ready_for_investor": student_ready  # ← Separate readiness decision
                }
            except:
                # Fallback - assume student needs more work
                final_message = "You've made good progress, but I think you need more practice before facing an investor. Keep working on your pitch!"
                messages.append({"role": "assistant", "content": final_message})
                
                # 🔧 FIX 3: Complete session but mark student as not ready
                return {
                    **state,  # ← PRESERVE all existing fields
                    "student_info": student_info,
                    "messages": messages,
                    "question_count": question_count + 1,
                    "exchange_count": exchange_count + 1,
                    "mentor_complete": True,  # ← Session is complete
                    "student_ready_for_investor": False  # ← But student isn't ready
                }

        elif question_count >= 4:
            # Always provide comprehensive feedback first
            try:
                conversation_context = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in messages[-8:]])
                
                # Use feedback prompt instead of assessment prompt
                feedback_prompt = get_feedback_and_transition_prompt(conversation_context, question_count)
                response = llm.invoke(feedback_prompt)
                feedback_message = response.content.strip()
                
                # 🔧 ENHANCED: Check if student is ready AND if we should complete the session
                student_ready = (
                    "proceed_to_investor: yes" in feedback_message.lower() or 
                    ("ready" in feedback_message.lower() and "investor" in feedback_message.lower())
                )
                
                # Check if mentor should complete session (could be yes even if student isn't ready)
                session_complete = (
                    "session_complete: yes" in feedback_message.lower() or
                    student_ready  # If student is ready, session is also complete
                )
                
                messages.append({"role": "assistant", "content": feedback_message})
                
                # 🔧 FIX 4: Set both completion and readiness flags
                return {
                    **state,  # ← PRESERVE all existing fields
                    "student_info": student_info,
                    "messages": messages,
                    "question_count": question_count + 1,
                    "exchange_count": exchange_count + 1,
                    "mentor_complete": session_complete,
                    "student_ready_for_investor": student_ready
                }
            except:
                pass  # Continue with regular response if assessment fails

        # CHANGE 5: Generate intelligent response using YAML prompts
        try:
            conversation_context = "\n".join([f"{msg['role'].upper()}: {msg['content']}" for msg in messages[-4:]])
            system_prompt = get_mentor_system_prompt(student_info, "info_gathering" if question_count <= 2 else "ideation")
            
            response_prompt = get_response_prompt(
                system_prompt=system_prompt,
                conversation_context=conversation_context,
                last_message=last_message,
                student_info=student_info
            )
            
            response = llm.invoke(response_prompt)
            next_question = response.content.strip()
        except:
            # Fallback responses that always work
            fallback_responses = [
                "That's interesting! Can you tell me more about your business idea?",
                "Great! What problem does your idea solve, and who would benefit from it?",
                "Excellent! How do you think your solution is different from what's already out there?"
            ]
            next_question = fallback_responses[min(question_count-1, len(fallback_responses)-1)]

        messages.append({"role": "assistant", "content": next_question})

        # 🔧 FIX 5: Preserve all state fields
        return {
            **state,  # ← PRESERVE all existing fields
            "student_info": student_info,
            "messages": messages,
            "question_count": question_count + 1,
            "exchange_count": exchange_count + 1,
            "mentor_complete": False,
            "student_ready_for_investor": False  # NEW: Not ready yet during regular conversation
        }

    # 🔧 FIX 6: Preserve all state fields (fallback return)
    return {
        **state,  # ← PRESERVE all existing fields
        "student_info": student_info,
        "messages": messages,
        "question_count": question_count + 1,
        "exchange_count": exchange_count + 1,
        "mentor_complete": True,
        "student_ready_for_investor": True  # ← Fallback assumes ready (shouldn't normally reach here)
    }

# 🚀 NEW: CONDITIONAL EDGE FUNCTION
def should_continue(state: MentorState) -> str:
    """
    Determines if conversation should continue or end
    This is the 'brain' that decides the flow!
    """
    if state["mentor_complete"]:
        return "end"  # Go to END node
    else:
        return "continue"  # Stay in mentor loop

# 🚀 NEW: CREATE THE LANGGRAPH
def create_mentor_graph():
    """
    Creates the LangGraph workflow
    Think of this as building the conversation 'railway tracks'
    """
    # Create the graph
    graph = StateGraph(MentorState)
    
    # Add our mentor node
    graph.add_node("mentor", mentor_node)
    
    # Set entry point (where conversation starts)
    graph.set_entry_point("mentor")
    
    # Add conditional edges (the decision logic)
    graph.add_conditional_edges(
        "mentor",           # From this node
        should_continue,    # Use this function to decide
        {
            "continue": "mentor",  # If "continue" → loop back to mentor
            "end": END            # If "end" → finish conversation
        }
    )
    
    # Compile the graph into a runnable workflow
    return graph.compile()

# 🚀 PROPER LANGGRAPH: INTERACTIVE CONVERSATION FUNCTION
def run_mentor_conversation():
    """
    Main conversation loop using LangGraph properly with streaming
    """
    print("🎓 Welcome to AgentAcademy - Mentor Session!")
    print("=" * 50)
    
    # Create the graph - WE DO USE IT!
    mentor_graph = create_mentor_graph()
    
    # Initialize state
    current_state = {
        "student_info": {},
        "messages": [],
        "question_count": 0,
        "exchange_count": 0,
        "mentor_complete": False
    }
    
    # Main conversation loop using LangGraph streaming
    while not current_state["mentor_complete"]:
        # Stream the graph execution - this gives us control!
        for output in mentor_graph.stream(current_state):
            # output is a dict like {"mentor": updated_state}
            if "mentor" in output:
                current_state = output["mentor"]
                
                # Get the latest mentor message
                if current_state["messages"]:
                    latest_message = current_state["messages"][-1]["content"]
                    print(f"\n🤖 Mentor: {latest_message}")
                
                # Check if conversation is complete
                if current_state["mentor_complete"]:
                    print("\n✅ Mentor session complete!")
                    print(f"📊 Student Info Collected: {current_state['student_info']}")
                    return current_state
                
                # Get user input and add to state
                user_input = input(f"\n👤 You: ")
                current_state["messages"].append({"role": "user", "content": user_input})
                
                # Break out of stream to restart with new state
                break
    
    return current_state

if __name__ == "__main__":
    print("All imports successful")
    llm = ChatOpenAI(
        api_key = OPENAI_API_KEY,
        model = MODEL_NAME,
        temperature = 0.7
    )
    print("LLM initialized")

    # Test YAML prompts loading
    try:
        from prompts.mentor_prompt_loader import prompt_loader
        config = prompt_loader.get_config()
        print("✅ YAML prompts loaded successfully!")
    except Exception as e:
        print(f"❌ YAML prompt loading failed: {e}")
        print("Check your mentor_prompts.yaml file for syntax errors")
        exit(1)

    # Test graph creation
    print("\n🧪 Testing LangGraph Creation...")
    mentor_graph = create_mentor_graph()
    print("✅ LangGraph created successfully!")
    
    # 🎯 VISUALIZE THE GRAPH STRUCTURE
    print("\n📊 GRAPH VISUALIZATION:")
    print("=" * 50)
    
    # ASCII visualization (works everywhere)
    print("\n🔍 ASCII Structure:")
    try:
        print(mentor_graph.get_graph().draw_ascii())
    except:
        print("ASCII visualization not available")
    
    # Mermaid diagram (for web/markdown)
    print("\n🎨 Mermaid Diagram Code:")
    try:
        mermaid_code = mentor_graph.get_graph().draw_mermaid()
        print(mermaid_code)
        print("\n💡 Tip: Copy this code to https://mermaid.live to see visual diagram!")
    except:
        print("Mermaid visualization not available")
    
    # Graph info
    print(f"\n📈 Graph Info:")
    graph_info = mentor_graph.get_graph()
    print(f"Nodes: {list(graph_info.nodes.keys())}")
    print(f"Edges: {len(graph_info.edges)} connections")
    
    print("=" * 50)
    
    # Ask user what they want to do
    choice = input("\n🚀 What would you like to do?\n1. Run interactive conversation\n2. Just test the structure\nChoice (1 or 2): ")
    
    if choice == "1":
        print("\n🚀 Starting Interactive Conversation...")
        final_state = run_mentor_conversation()
    else:
        print("\n✅ Structure testing complete!")