# evaluator_agent.py - Comprehensive Pitch Evaluation Agent
from typing import TypedDict, List, Dict, Any
from langchain_openai import ChatOpenAI
import os
from datetime import datetime
from config import OPENAI_API_KEY, MODEL_NAME
from prompts.evaluator_prompt_loader import (
    get_pitch_performance_scoring_prompt,
    get_evaluator_analysis_prompt,
    get_evaluator_feedback_prompt,
    StudentAnalysis
)

class EvaluatorState(TypedDict):
    """State structure for evaluator agent"""
    # Inherited from investor
    student_info: Dict[str, Any]
    messages: List[Dict[str, str]]
    investor_persona: str
    pitch_complete: bool
    exchange_count: int  
    
    # Evaluator-specific  
    evaluation_summary: Dict[str, Any]
    feedback_document_path: str
    evaluator_complete: bool


def parse_scores(score_text: str) -> Dict[str, str]:
    """Parse LLM scoring output into dictionary"""
    scores = {}
    
    for line in score_text.strip().split('\n'):
        if ':' in line:
            criterion, score = line.split(':', 1)
            criterion = criterion.strip()
            score = score.strip()
            
            # Validate score
            if score in ['excellent', 'good', 'needs_work']:
                scores[criterion] = score
    
    return scores

def calculate_weighted_score(criterion_scores: Dict[str, str]) -> int:
    """Calculate overall weighted score from criterion scores"""
    
    # Score mapping
    score_values = {
        'excellent': 90,
        'good': 75,
        'needs_work': 50
    }
    
    # Weights from your YAML
    weights = {
        'problem_articulation': 0.20,
        'solution_clarity': 0.20,
        'market_understanding': 0.15,
        'competitive_advantage': 0.15,
        'business_model': 0.10,
        'communication_skills': 0.10,
        'adaptability': 0.10
    }
    
    total_score = 0
    total_weight = 0
    
    for criterion, score_text in criterion_scores.items():
        if criterion in weights and score_text in score_values:
            weight = weights[criterion]
            score = score_values[score_text]
            total_score += score * weight
            total_weight += weight
    
    # Handle missing criteria gracefully
    if total_weight > 0:
        return int(total_score / total_weight)
    else:
        return 50  # Default fallback

def get_performance_level(overall_score: int) -> str:
    """Convert numeric score to performance level"""
    if overall_score >= 80:
        return "advanced"
    elif overall_score >= 65:
        return "intermediate" 
    else:
        return "beginner"


def extract_conversation_transcript(messages: List[Dict[str, str]]) -> str:
    """Convert messages list to readable transcript"""
    transcript_lines = []
    
    for msg in messages:
        role = "STUDENT" if msg["role"] == "user" else "INVESTOR"
        content = msg["content"]
        transcript_lines.append(f"{role}: {content}")
    
    return "\n\n".join(transcript_lines)

def extract_investor_decision(messages: List[Dict[str, str]]) -> tuple[str, List[str]]:
    """Extract investor decision and reasons from final message"""
    if not messages:
        return "unknown", ["No conversation recorded"]
    
    # Get last investor message (final evaluation)
    last_investor_msg = None
    for msg in reversed(messages):
        if msg["role"] == "assistant":
            last_investor_msg = msg["content"]
            break
    
    if not last_investor_msg:
        return "unknown", ["No investor response"]
    
    # Simple heuristic to determine decision
    positive_signals = ["convinced", "interested", "invest", "excited", "impressed"]
    negative_signals = ["not convinced", "pass", "concerns", "issues", "not ready"]
    
    last_msg_lower = last_investor_msg.lower()
    
    if any(signal in last_msg_lower for signal in positive_signals):
        decision = "convinced"
    elif any(signal in last_msg_lower for signal in negative_signals):
        decision = "not convinced"
    else:
        decision = "neutral"
    
    # Extract key reasons (simple approach)
    reasons = []
    if "strengths" in last_msg_lower or "good" in last_msg_lower:
        reasons.append("Has strengths in presentation")
    if "improve" in last_msg_lower or "work on" in last_msg_lower:
        reasons.append("Areas need improvement")
    if not reasons:
        reasons = ["Standard evaluation provided"]
    
    return decision, reasons

def create_evaluation_filename(student_info: Dict[str, Any]) -> str:
    """Generate filename for evaluation document"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    student_name = student_info.get("name", "student").lower().replace(" ", "_")
    
    return f"evaluation_{student_name}_{timestamp}.md"

def ensure_evaluations_directory() -> str:
    """Create evaluations directory if it doesn't exist"""
    eval_dir = "evaluations"
    if not os.path.exists(eval_dir):
        os.makedirs(eval_dir)
    return eval_dir


def evaluator_node(state: EvaluatorState) -> EvaluatorState:
    """
    Evaluator Agent Node - Comprehensive pitch feedback generation
    Following clean architecture pattern from investor agent
    """
    # Extract data from state
    student_info = state.get("student_info", {})
    messages = state.get("messages", [])
    investor_persona = state.get("investor_persona", "aria")
    
    # Initialize LLM
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=MODEL_NAME,
        temperature=0.3  # Lower temperature for consistent evaluation
    )
    
    try:
        # Step 1: Extract conversation data
        conversation_transcript = extract_conversation_transcript(messages)
        investor_decision, investor_reasons = extract_investor_decision(messages)
        conversation_length = len([msg for msg in messages if msg["role"] == "user"])
        
        # Step 2: Get structured scores
        scoring_prompt = get_pitch_performance_scoring_prompt(
            conversation_transcript, investor_decision, investor_reasons
        )
        
        score_response = llm.invoke(scoring_prompt)
        criterion_scores = parse_scores(score_response.content)
        
        # Step 3: Calculate overall performance
        overall_score = calculate_weighted_score(criterion_scores)
        performance_level = get_performance_level(overall_score)
        
        # Step 4: Generate comprehensive feedback
        student_analysis = StudentAnalysis(
            strengths=[],  # Will be filled by LLM analysis
            improvement_areas=list(criterion_scores.keys()),  # Areas that need work
            skill_level=performance_level,
            conversation_length=conversation_length,
            investor_decision=investor_decision,
            investor_reasons=investor_reasons
        )
        
        feedback_prompt = get_evaluator_feedback_prompt(student_analysis, conversation_transcript)
        feedback_response = llm.invoke(feedback_prompt)
        comprehensive_feedback = feedback_response.content
        
        # Step 5: Save feedback document
        eval_dir = ensure_evaluations_directory()
        filename = create_evaluation_filename(student_info)
        filepath = os.path.join(eval_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(comprehensive_feedback)
        
        # Step 6: Build evaluation summary
        evaluation_summary = {
            "overall_score": overall_score,
            "performance_level": performance_level,  
            "score_breakdown": criterion_scores,
            "investor_decision": investor_decision,
            "conversation_length": conversation_length,
            "feedback_generated": True,
            "detailed_feedback": comprehensive_feedback,
            "strengths": [],
            "improvements": []
        }
        
        # Return updated state
        return {
            **state,  # Keep all existing fields
            "evaluation_summary": evaluation_summary,
            "feedback_document_path": filepath,
            "evaluator_complete": True
        }
        
    except Exception as e:
        # Fallback handling
        print(f"⚠️ Evaluator error: {e}")
        
        # Create basic fallback evaluation
        fallback_summary = {
            "overall_score": 50,
            "performance_level": "beginner", 
            "score_breakdown": {},
            "error": str(e),
            "feedback_generated": False
        }
        
        return {
            **state,
            "evaluation_summary": fallback_summary,
            "feedback_document_path": "",
            "evaluator_complete": True
        }




def test_evaluator_agent():
    """Test the evaluator agent with sample data"""
    print("🧪 Testing Evaluator Agent")
    print("=" * 50)
    
    # Sample state from investor session
    sample_state = {
        "student_info": {
            "name": "Salman",
            "hobby": "HCI applications",
            "business_idea": "AI programming education platform",
            "location": "Boston"
        },
        "messages": [
            {"role": "assistant", "content": "Hello! I'm Aria Iyer, excited to hear your pitch!"},
            {"role": "user", "content": "Hi! I'm building an AI-powered platform that helps students learn programming through personalized tutoring."},
            {"role": "assistant", "content": "Interesting! Can you tell me more about your target market?"},
            {"role": "user", "content": "I'm targeting computer science students who struggle with coding concepts."},
            {"role": "assistant", "content": "Great concept! Your passion shows and you've identified a real problem. However, I'd like to see more market research and competitive analysis. Overall, this has potential but needs refinement before investment."}
        ],
        "investor_persona": "aria",
        "pitch_complete": True,
        "exchange_count": 3
    }
    
    try:
        # Test helper functions
        print("📝 Testing helper functions...")
        
        transcript = extract_conversation_transcript(sample_state["messages"])
        print(f"✅ Transcript generated: {len(transcript)} characters")
        
        decision, reasons = extract_investor_decision(sample_state["messages"])
        print(f"✅ Decision extracted: '{decision}' with {len(reasons)} reasons")
        
        filename = create_evaluation_filename(sample_state["student_info"])
        print(f"✅ Filename generated: {filename}")
        
        # Test scoring functions
        print("\n🔢 Testing scoring functions...")
        
        sample_scores = {
            "problem_articulation": "good",
            "solution_clarity": "excellent", 
            "market_understanding": "needs_work"
        }
        
        overall_score = calculate_weighted_score(sample_scores)
        performance_level = get_performance_level(overall_score)
        print(f"✅ Score calculation: {overall_score} ({performance_level})")
        
        # Test full evaluator (without LLM call to save costs)
        print("\n🎯 Testing evaluator structure...")
        print("✅ All components ready for full evaluation")
        print(f"💡 Sample state has {len(sample_state['messages'])} messages")
        print(f"🎓 Student: {sample_state['student_info']['name']}")
        print(f"💼 Investor: {sample_state['investor_persona']}")
        
        print("\n🚀 Evaluator agent ready for deployment!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

def run_full_evaluator_test():
    """Run complete evaluator with LLM calls (costs ~$0.01)"""
    print("🧪 Full Evaluator Test with LLM")
    print("=" * 50)
    
    # Sample state
    sample_state = {
        "student_info": {"name": "TestStudent", "business_idea": "AI tutoring"},
        "messages": [
            {"role": "assistant", "content": "Hello! Tell me about your business."},
            {"role": "user", "content": "I'm building an AI tutoring platform for students."},
            {"role": "assistant", "content": "Interesting concept but I need more details about market size and competition."}
        ],
        "investor_persona": "aria",
        "pitch_complete": True,
        "exchange_count": 2
    }
    
    print("Running full evaluation...")
    result_state = evaluator_node(sample_state)
    
    print(f"✅ Evaluation complete!")
    print(f"📊 Overall score: {result_state['evaluation_summary']['overall_score']}")
    print(f"📈 Performance level: {result_state['evaluation_summary']['performance_level']}")
    print(f"📄 Feedback saved to: {result_state['feedback_document_path']}")

# Main execution
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "full":
        run_full_evaluator_test()  # Costs money
    else:
        test_evaluator_agent()     # Free testing