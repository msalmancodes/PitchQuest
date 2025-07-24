# import necessary libraries
from langgraph.graph import StateGraph, END # creates workflows
from typing import TypedDict, List, Dict, Any # for defining state structure 
from langchain_openai import ChatOpenAI # for LLM
from config import OPENAI_API_KEY, MODEL_NAME # for API key and model name

class MentorState(TypedDict):
    """State struct for the mentor agent and overall system"""
    student_info: Dict[str, Any] # student info: hobby, experience etc
    messages: List[Dict[str, str]] # current conversation messages 
    mentor_complete: bool # whether the mentor has completed the conversation
    question_count: int # number of questions asked

def mentor_node(state: MentorState) -> MentorState:
    """
    Mentor Agent node - guides students through strategic questions 
    """
    #get current state
    messages = state.get("messages", [])
    student_info = state.get("student_info", {})
    question_count = state.get("question_count", 0)
    
    # Initialize LLM
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=MODEL_NAME,
        temperature=0.7
    )

    # Question 0: Ask for student info
    if question_count == 0:
        mentor_response = "Hi! I'm your mentor, here to help you prepare for pitching. Before we start, what's your hobby, age, and location?"
        messages.append({"role": "assistant", "content": mentor_response})
        return {
            "student_info": student_info,
            "messages": messages,
            "question_count": 1,
            "mentor_complete": False
        }

    elif question_count <= 3:
        # Get last message - ALWAYS set it to avoid UnboundLocalError
        last_message = ""
        if messages and messages[-1]["role"] == "user":
            last_message = messages[-1]["content"]

        # Question 1: Extract info + Ask for business idea
        if question_count == 1:
            # Extract essential info 
            extraction_message = f"""Extract the hobby, age, and location from this student response:
            "{last_message}"
            
            Return strictly in this format:
            Hobby: [hobby]
            Age: [age]
            Location: [location]
            """

            extraction_response = llm.invoke(extraction_message)
            lines = extraction_response.content.split('\n')
            for line in lines:
                if line.startswith("Hobby:"):
                    student_info["hobby"] = line.replace('Hobby:', '').strip()
                elif line.startswith('Age:'):
                    student_info["age"] = line.replace('Age:', '').strip()
                elif line.startswith('Location:'):
                    student_info["location"] = line.replace('Location:', '').strip()
            
            # Ask for business idea
            next_question = "Thanks for sharing! What business idea would you like to work on today?"
            messages.append({"role": "assistant", "content": next_question})

        # Question 2: Ask about problem/audience 
        elif question_count == 2:
            next_question = "Great! Now, what problem do you think your business idea solves? And who specifically would benefit from this solution?"
            messages.append({"role": "assistant", "content": next_question})

        # Question 3: Final transition to investor
        elif question_count == 3:
            next_question = "Excellent! You've got a solid foundation. It's time to practice your elevator pitch with an investor. Good luck!"
            messages.append({"role": "assistant", "content": next_question})
            return {
                "student_info": student_info,
                "messages": messages,
                "question_count": question_count + 1,
                "mentor_complete": True  # ← Done!
            }

        return {
            "student_info": student_info,
            "messages": messages,
            "question_count": question_count + 1,
            "mentor_complete": False
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