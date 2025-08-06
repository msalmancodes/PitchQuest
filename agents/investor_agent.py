# investor_agent.py - Clean Investor Agent Implementation with STATE PRESERVATION
from typing import TypedDict, List, Dict, Any, Literal
from langchain_openai import ChatOpenAI
from config import OPENAI_API_KEY, MODEL_NAME
from prompts.investor_prompt_loader import (
    get_investor_opening_prompt,
    get_investor_response_prompt, 
    get_investor_final_decision_prompt,
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
    FIXED: Now preserves all SessionState fields using **state pattern
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
        
        # 🔧 FIX 1: Preserve all SessionState fields
        return {
            **state,  # ← PRESERVE all existing fields (mentor_complete, student_ready_for_investor, etc.)
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
                # Generate final decision
                conversation_context = "\n".join([
                    f"{msg['role'].upper()}: {msg['content']}" 
                    for msg in messages[-6:] # Last 3 exchanges for context for the final decision
                ])
                
                decision_prompt = get_investor_final_decision_prompt(persona, conversation_context)
                response = llm.invoke(decision_prompt)
                decision = response.content.strip()
                
                # Add evaluation message
                messages.append({"role": "assistant", "content": decision})
                
                # 🔧 FIX 2: Preserve all SessionState fields
                return {
                    **state,  # ← PRESERVE all existing fields
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
                
                # 🔧 FIX 3: Preserve all SessionState fields
                return {
                    **state,  # ← PRESERVE all existing fields
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
        
        # 🔧 FIX 4: Preserve all SessionState fields
        return {
            **state,  # ← PRESERVE all existing fields
            "student_info": student_info,
            "messages": messages,
            "investor_persona": persona,
            "exchange_count": exchange_count + 1,
            "pitch_complete": False
        }
    
    # 🔧 FIX 5: Preserve all SessionState fields (fallback return)
    return {
        **state,  # ← PRESERVE all existing fields
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


# Add this to your investor_agent.py file (keep everything else the same!)

def process_single_investor_message(current_state: InvestorState, user_message: str) -> dict:
    """
    NEW FUNCTION: Process ONE investor message at a time for web interface
    
    This handles both:
    1. Persona selection step (if not selected yet)
    2. Regular pitch conversation
    
    Args:
        current_state: Current investor session state
        user_message: Single message from user
    
    Returns:
        Structured response for web interface
    """
    
    # Step 1: Handle persona selection if not done yet
    if "investor_persona" not in current_state or current_state.get("exchange_count", 0) == 0:
        return handle_persona_selection(current_state, user_message)
    
    # Step 2: Handle regular pitch conversation
    return handle_pitch_conversation(current_state, user_message)


def handle_persona_selection(current_state: InvestorState, user_message: str) -> dict:
    """
    Handle investor persona selection step
    
    Args:
        current_state: Current state  
        user_message: User's persona choice
    
    Returns:
        Response with persona selection or confirmation
    """
    student_info = current_state.get("student_info", {})
    
    # If this is the very first message, show persona selection
    if not user_message.strip() or user_message.lower() in ["start", "begin", "let's start"]:
        selection_interface = display_investor_selection(student_info)
        
        return {
            "ai_response": selection_interface,
            "updated_state": current_state,
            "pitch_complete": False,
            "persona_selection_needed": True,
            "investor_persona": None,
            "exchange_count": 0
        }
    
    # User has made a persona selection
    selected_persona = select_investor_persona(student_info, user_message)
    
    # Get persona info for confirmation
    profiles = get_investor_personas()
    persona_info = profiles[selected_persona]
    
    # Create confirmation message
    confirmation = f"""✅ **Perfect! You'll be pitching to {persona_info['name']} {persona_info['avatar']}**

• **Style**: {persona_info['style']}
• **Focus**: {persona_info['focus']}
• **Specialty**: {persona_info['specialty']}

🎯 **Ready to start your pitch practice!**

{persona_info['name']} is waiting to hear your business idea. Take a deep breath and begin whenever you're ready!"""
    
    # Initialize investor conversation state
    updated_state = {
        **current_state,
        "investor_persona": selected_persona,
        "exchange_count": 0,  # Will increment when actual pitch starts
        "pitch_complete": False,
        "messages": []
    }
    
    return {
        "ai_response": confirmation,
        "updated_state": updated_state,
        "pitch_complete": False,
        "persona_selection_needed": False,
        "investor_persona": selected_persona,
        "exchange_count": 0,
        "ready_for_pitch": True
    }


def handle_pitch_conversation(current_state: InvestorState, user_message: str) -> dict:
    """
    Handle regular pitch conversation (after persona selected)
    
    Args:
        current_state: Current investor state with persona selected
        user_message: User's pitch message
    
    Returns:
        Response with investor feedback
    """
    
    # Step 1: Add user message to state
    messages = current_state.get("messages", [])
    if user_message.strip():  # Only add non-empty messages
        messages.append({"role": "user", "content": user_message.strip()})
    
    # Step 2: Update state with user message  
    updated_state = {
        **current_state,
        "messages": messages
    }
    
    # Step 3: Process through investor_node logic
    processed_state = investor_node(updated_state)
    
    # Step 4: Extract the AI response (last assistant message)
    ai_response = ""
    if processed_state["messages"]:
        for msg in reversed(processed_state["messages"]):
            if msg["role"] == "assistant":
                ai_response = msg["content"]
                break
    
    # Step 5: Get persona info for response context
    profiles = get_investor_personas()
    persona = processed_state.get("investor_persona", "aria")
    persona_name = profiles[persona]["name"]
    
    # Step 6: Return structured response
    return {
        "ai_response": ai_response,
        "updated_state": processed_state,
        "pitch_complete": processed_state.get("pitch_complete", False),
        "investor_persona": persona,
        "investor_name": persona_name,
        "exchange_count": processed_state.get("exchange_count", 0),
        "persona_selection_needed": False,
        "ready_for_pitch": False  # Already in pitch mode
    }


def test_single_investor_processing():
    """
    Test function to verify single investor message processing works
    """
    print("🧪 Testing Single Investor Message Processing...")
    print("=" * 50)
    
    # Sample student info (passed from mentor session)
    sample_student_info = {
        "name": "Test Student",
        "hobby": "programming",
        "business_idea": "AI tutoring platform"
    }
    
    # Initialize empty investor state
    initial_state = {
        "student_info": sample_student_info,
        "messages": [],
        "exchange_count": 0,
        "pitch_complete": False
    }
    
    print("📍 Test 1: Request persona selection")
    result1 = process_single_investor_message(initial_state, "start")
    print(f"🎯 Persona Selection Needed: {result1['persona_selection_needed']}")
    print(f"📝 Response Preview: {result1['ai_response'][:100]}...")
    print()
    
    print("📍 Test 2: Select persona")
    result2 = process_single_investor_message(result1['updated_state'], "aria")
    print(f"👤 Selected Persona: {result2['investor_persona']}")
    print(f"📝 Confirmation: {result2['ai_response'][:100]}...")
    print(f"🚀 Ready for Pitch: {result2['ready_for_pitch']}")
    print()
    
    print("📍 Test 3: Start pitching")
    # Simulate starting the pitch
    pitch_ready_state = {
        **result2['updated_state'],
        "messages": [],  # Start fresh for pitch
        "exchange_count": 0  # Reset for pitch conversation
    }
    
    result3 = process_single_investor_message(
        pitch_ready_state, 
        "Hi! I have an AI tutoring platform that helps students learn programming"
    )
    print(f"🤖 Investor Response: {result3['ai_response'][:100]}...")
    print(f"💬 Exchange Count: {result3['exchange_count']}")
    print(f"✅ Pitch Complete: {result3['pitch_complete']}")
    print()
    
    print("✅ Single investor message processing working!")
    print("🎯 Ready for FastAPI integration!")


def simulate_web_investor_conversation():
    """
    Simulate how investor conversations will work with FastAPI
    Shows the complete flow: persona selection → pitch conversation
    """
    print("🌐 Simulating Web Investor Conversation...")
    print("(Complete flow: Persona Selection → Pitch Practice)")
    print("=" * 60)
    
    # Session storage simulation
    session_storage = {}
    
    def web_investor_chat(session_id: str, user_message: str, student_info: dict):
        """Simulate FastAPI investor endpoint"""
        
        # Load or create session
        if session_id not in session_storage:
            session_storage[session_id] = {
                "student_info": student_info,
                "messages": [],
                "exchange_count": 0,
                "pitch_complete": False
            }
            print(f"🆕 Created investor session: {session_id}")
        
        current_state = session_storage[session_id]
        print(f"📂 Loaded investor session {session_id}")
        
        # Process message
        result = process_single_investor_message(current_state, user_message)
        
        # Save updated state
        session_storage[session_id] = result['updated_state']
        print(f"💾 Saved investor session {session_id}")
        
        # Return web response
        return {
            "response": result['ai_response'],
            "session_id": session_id,
            "pitch_complete": result['pitch_complete'],
            "persona_selection_needed": result.get('persona_selection_needed', False),
            "investor_persona": result.get('investor_persona'),
            "ready_for_pitch": result.get('ready_for_pitch', False),
            "exchange_count": result.get('exchange_count', 0)
        }
    
    # Sample student info from mentor session
    student_info = {
        "name": "Salman",
        "hobby": "guitar playing",
        "business_idea": "music learning app"
    }
    
    session_id = "investor_session_456"
    
    print("\n🚀 PHASE 1: Persona Selection")
    print("📨 Request 1: Start investor session")
    response1 = web_investor_chat(session_id, "start", student_info)
    print(f"🎯 Persona Selection Needed: {response1['persona_selection_needed']}")
    print(f"📤 Response: Shows investor selection interface...")
    
    print("\n📨 Request 2: Select investor")
    response2 = web_investor_chat(session_id, "anna", student_info)
    print(f"👤 Selected: {response2['investor_persona']}")
    print(f"🚀 Ready for Pitch: {response2['ready_for_pitch']}")
    print(f"📤 Response: Confirmation message...")
    
    print("\n🎯 PHASE 2: Pitch Practice")
    print("📨 Request 3: Start pitch")
    response3 = web_investor_chat(session_id, "Hi Anna! I have a music learning app for guitar players", student_info)
    print(f"💬 Exchange: {response3['exchange_count']}")
    print(f"📤 Anna's Response: Investor feedback...")
    
    print("📨 Request 4: Continue pitch")
    response4 = web_investor_chat(session_id, "It helps beginners learn music theory through interactive lessons", student_info)
    print(f"💬 Exchange: {response4['exchange_count']}")
    print(f"✅ Pitch Complete: {response4['pitch_complete']}")
    
    print(f"\n📊 Final Session Status:")
    print(f"   • Investor: {response4['investor_persona']}")
    print(f"   • Exchanges: {response4['exchange_count']}")
    print(f"   • Complete: {response4['pitch_complete']}")
    print(f"   • Sessions Stored: {len(session_storage)}")
    
    print("\n🎯 This shows the complete investor web flow!")
    print("✅ Ready for FastAPI integration!")


# Add new test options to main block
if __name__ == "__main__":
    print("\n🚀 NEW: Single Investor Message Processing Available!")
    
    import sys
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        if command == "test-single":
            test_single_investor_processing()
        elif command == "test-web":
            simulate_web_investor_conversation()
        elif command == "test":
            test_investor_agent()
        else:
            print(f"❌ Unknown command: {command}")
    else:
        choice = input("""
🚀 What would you like to do?
1. Run original interactive investor conversation
2. Test single message processing
3. Simulate web investor conversation  
4. Test investor agent structure
Choice (1-4): """)
        
        if choice == "1":
            sample_student_info = {
                "name": "Salman",
                "hobby": "HCI applications", 
                "business_idea": "AI programming education platform",
                "location": "Boston"
            }
            final_state = run_investor_conversation(sample_student_info)
        elif choice == "2":
            test_single_investor_processing()
        elif choice == "3":
            simulate_web_investor_conversation()
        elif choice == "4":
            test_investor_agent()
        else:
            print("\n✅ Structure testing complete!")

# if __name__ == "__main__":
#     # Run test or interactive session
#     import sys
    
#     if len(sys.argv) > 1 and sys.argv[1] == "test":
#         test_investor_agent()
#     else:
#         # Interactive test
#         sample_student_info = {
#             "name": "Salman",
#             "hobby": "HCI applications", 
#             "business_idea": "AI programming education platform",
#             "location": "Boston"
#         }
        
#         final_state = run_investor_conversation(sample_student_info)