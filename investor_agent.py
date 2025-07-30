# investor_agent.py - Clean Investor Agent Implementation
from typing import TypedDict, List, Dict, Any, Literal
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from prompts.investor_prompt_loader import (
    get_investor_opening_prompt,
    get_investor_response_prompt, 
    get_investor_evaluation_prompt,
    get_investor_personas,
    recommend_investor_persona
)

class InvestorState(TypedDict):
    """State structure for investor agent interactions"""
    student_info: Dict[str, Any]           # From mentor handoff
    messages: List[Dict[str, str]]         # Conversation with investor
    investor_persona: Literal["aria", "anna", "adam"]  # Selected persona
    pitch_complete: bool                   # Session finished
    exchange_count: int                    # Track conversation length

def display_investor_selection(student_info: Dict[str, Any]) -> str:
    """
    Generate investor selection interface for student
    
    Args:
        student_info: Student information from mentor session
    
    Returns:
        Formatted selection interface text
    """
    profiles = get_investor_personas()
    recommended = recommend_investor_persona(student_info)
    
    interface = "🎯 **CHOOSE YOUR INVESTOR**\n\n"
    interface += f"Based on your business idea, we recommend: **{profiles[recommended]['name']}** {profiles[recommended]['avatar']}\n\n"
    
    interface += "All available investors:\n\n"
    for persona_id, profile in profiles.items():
        star = "⭐ **RECOMMENDED**" if persona_id == recommended else ""
        interface += f"""{profile['avatar']} **{profile['name']}** {star}
• **Specialty**: {profile['specialty']}
• **Style**: {profile['style']}  
• **Focus**: {profile['focus']}
• **Best for**: {profile['best_for']}
• **Difficulty**: {profile['difficulty']}

"""
    
    interface += "🎲 **Type 'random'** for surprise assignment!\n"
    interface += f"💡 **Type persona name** (aria/anna/adam) or just press Enter for {profiles[recommended]['name']}"
    
    return interface

def select_investor_persona(student_info: Dict[str, Any], user_choice: str = "") -> str:
    """
    Handle investor persona selection logic
    
    Args:
        student_info: Student information
        user_choice: Student's selection input
    
    Returns:
        Selected persona ID
    """
    import random
    
    user_choice = user_choice.lower().strip()
    
    # Handle different selection options
    if user_choice == "random":
        return random.choice(["aria", "anna", "adam"])
    elif user_choice in ["aria", "anna", "adam"]:
        return user_choice
    elif user_choice == "":
        # Default to recommendation
        return recommend_investor_persona(student_info)
    else:
        # Invalid input, default to recommendation
        return recommend_investor_persona(student_info)

def investor_node(state: InvestorState) -> InvestorState:
    """
    Investor Agent Node - Conducts realistic pitch sessions
    Clean implementation using dedicated prompt loader
    """
    # Get current state
    messages = state.get("messages", [])
    student_info = state.get("student_info", {})
    persona = state.get("investor_persona", "aria")
    exchange_count = state.get("exchange_count", 0)
    
    # Initialize LLM
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=MODEL_NAME,
        temperature=0.7
    )
    
    # First exchange: Opening greeting
    if exchange_count == 0:
        try:
            opening_prompt = get_investor_opening_prompt(persona)
            response = llm.invoke(opening_prompt)
            investor_response = response.content.strip()
        except Exception as e:
            # Fallback greeting
            persona_names = {"aria": "Aria Iyer", "anna": "Anna Ito", "adam": "Adam Ingram"}
            investor_response = f"Hello! I'm {persona_names[persona]}, and I'm excited to hear your elevator pitch. Please, go ahead and tell me about your business idea!"
        
        messages.append({"role": "assistant", "content": investor_response})
        
        return {
            "student_info": student_info,
            "messages": messages,
            "investor_persona": persona,
            "exchange_count": 1,
            "pitch_complete": False
        }
    
    # Regular conversation exchanges (up to 8 exchanges)
    elif exchange_count <= 8:
        # Get last user message
        last_message = ""
        if messages and messages[-1]["role"] == "user":
            last_message = messages[-1]["content"]
        
        # Check for natural ending signals
        ending_signals = [
            "thank you", "that's all", "any questions", "i'm done", 
            "that's my pitch", "finished", "complete", "end"
        ]
        is_natural_ending = any(signal in last_message.lower() for signal in ending_signals)
        
        # Force evaluation at max exchanges or natural ending after minimum exchanges
        if exchange_count >= 8 or (exchange_count >= 3 and is_natural_ending):
            try:
                # Generate comprehensive evaluation
                full_conversation = "\n".join([
                    f"{msg['role'].upper()}: {msg['content']}" 
                    for msg in messages
                ])
                
                evaluation_prompt = get_investor_evaluation_prompt(full_conversation)
                response = llm.invoke(evaluation_prompt)
                evaluation = response.content.strip()
                
                # Add evaluation message
                messages.append({"role": "assistant", "content": evaluation})
                
                return {
                    "student_info": student_info,
                    "messages": messages,
                    "investor_persona": persona,
                    "exchange_count": exchange_count + 1,
                    "pitch_complete": True
                }
                
            except Exception as e:
                # Fallback evaluation
                persona_names = {"aria": "Aria Iyer", "anna": "Anna Ito", "adam": "Adam Ingram"}
                fallback_eval = f"""Thank you for that pitch! As {persona_names[persona]}, I appreciate your passion and the thought you've put into this idea.

**STRENGTHS:** You showed genuine enthusiasm for solving a real problem, and your concept has potential.

**AREAS FOR IMPROVEMENT:** Consider diving deeper into your target market analysis and competitive positioning. Think about your go-to-market strategy and how you'll acquire your first customers.

**NEXT STEPS:** Refine your value proposition and practice articulating what makes your solution unique. Keep developing your business model!

Great work on this practice session!"""
                
                messages.append({"role": "assistant", "content": fallback_eval})
                
                return {
                    "student_info": student_info,
                    "messages": messages,
                    "investor_persona": persona,
                    "exchange_count": exchange_count + 1,
                    "pitch_complete": True
                }
        
        # Generate regular conversational response
        try:
            conversation_context = "\n".join([
                f"{msg['role'].upper()}: {msg['content']}" 
                for msg in messages[-6:]  # Last 3 exchanges for context
            ])
            
            response_prompt = get_investor_response_prompt(
                persona, conversation_context, last_message
            )
            
            response = llm.invoke(response_prompt)
            investor_response = response.content.strip()
            
        except Exception as e:
            # Fallback responses based on persona
            fallback_responses = {
                "aria": "That's interesting. Can you tell me more about your target market and how you plan to reach them?",
                "anna": "I'd like to understand the technical aspects better. How do you plan to build and scale this solution?", 
                "adam": "I love the enthusiasm! Help me understand what makes your approach unique compared to existing solutions."
            }
            investor_response = fallback_responses.get(persona, "Can you tell me more about that?")
        
        messages.append({"role": "assistant", "content": investor_response})
        
        return {
            "student_info": student_info,
            "messages": messages,
            "investor_persona": persona,
            "exchange_count": exchange_count + 1,
            "pitch_complete": False
        }
    
    # Fallback return (should rarely reach here)
    return {
        "student_info": student_info,
        "messages": messages,
        "investor_persona": persona,
        "exchange_count": exchange_count + 1,
        "pitch_complete": True
    }

def should_continue_investor(state: InvestorState) -> str:
    """Determines if investor conversation should continue"""
    if state["pitch_complete"]:
        return "end"
    else:
        return "continue"

def run_investor_conversation(student_info: Dict[str, Any]) -> InvestorState:
    """
    Interactive investor conversation with persona selection
    
    Args:
        student_info: Student information from mentor session
    
    Returns:
        Final investor session state
    """
    print("🎯 Welcome to Investor Pitch Practice!")
    print("=" * 50)
    
    # Display investor selection interface
    selection_interface = display_investor_selection(student_info)
    print(selection_interface)
    
    # Get user's choice
    user_choice = input("\n👤 Your selection: ").strip()
    selected_persona = select_investor_persona(student_info, user_choice)
    
    # Confirm selection
    profiles = get_investor_personas()
    print(f"\n✅ You'll be pitching to: **{profiles[selected_persona]['name']}** {profiles[selected_persona]['avatar']}")
    print(f"Style: {profiles[selected_persona]['style']}")
    print("=" * 50)
    
    # Initialize investor state
    current_state = {
        "student_info": student_info,
        "messages": [],
        "investor_persona": selected_persona,
        "exchange_count": 0,
        "pitch_complete": False
    }
    
    # Main investor conversation loop
    while not current_state["pitch_complete"]:
        # Process investor response
        current_state = investor_node(current_state)
        
        # Display investor message
        if current_state["messages"]:
            latest_message = current_state["messages"][-1]["content"]
            persona_name = profiles[selected_persona]["name"]
            print(f"\n🤖 {persona_name}: {latest_message}")
        
        # Check if pitch is complete
        if current_state["pitch_complete"]:
            print("\n✅ Pitch session complete!")
            print("🎯 Great job practicing your pitch!")
            break
        
        # Get user input
        user_input = input(f"\n👤 You: ")
        current_state["messages"].append({"role": "user", "content": user_input})
    
    return current_state

# Simple test function
def test_investor_agent():
    """Test the investor agent with sample data"""
    print("🧪 Testing Investor Agent")
    print("=" * 50)
    
    # Sample student info from mentor session
    sample_student_info = {
        "name": "Salman",
        "hobby": "HCI applications",
        "business_idea": "AI programming education platform",
        "location": "Boston"
    }
    
    # Test recommendation system
    recommended = recommend_investor_persona(sample_student_info)
    print(f"Recommended investor: {recommended}")
    
    # Test selection display
    selection_display = display_investor_selection(sample_student_info)
    print(selection_display)
    
    print("\n✅ Basic tests passed!")

if __name__ == "__main__":
    # Run test or interactive session
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_investor_agent()
    else:
        # Interactive test
        sample_student_info = {
            "name": "Salman",
            "hobby": "HCI applications", 
            "business_idea": "AI programming education platform",
            "location": "Boston"
        }
        
        final_state = run_investor_conversation(sample_student_info)