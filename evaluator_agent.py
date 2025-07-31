"""
Evaluator Agent - Comprehensive Pitch Feedback System
Demonstrates production-ready AI agent architecture with educational focus
"""

import openai
import json
import re
import os
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import logging

# Import our custom prompt loader
from prompts.evaluator_prompt_loader import (
    EvaluatorPromptLoader, 
    StudentAnalysis,
    get_evaluator_feedback_prompt,
    get_evaluator_analysis_prompt,
    assess_student_level,
    get_evaluator_config
)

# 🧠 LEARNING POINT: Structured Data Models for Educational AI
@dataclass
class EvaluationResult:
    """
    Comprehensive evaluation result structure
    
    🎯 KEY CONCEPT: Structured Output Design
    - Ensures consistent evaluation format across all students
    - Enables easy integration with databases, dashboards, reports
    - Provides clear separation between different types of feedback
    """
    # Core Assessment
    overall_score: str  # "excellent", "good", "needs_improvement"
    strengths: List[str]
    improvement_areas: List[str]
    
    # Detailed Analysis
    detailed_feedback: str  # Full markdown feedback document
    specific_quotes: List[Dict[str, str]]  # {"quote": "...", "analysis": "..."}
    
    # Learning Resources
    recommended_resources: List[Dict[str, str]]
    action_plan: List[Dict[str, Any]]
    
    # Metadata
    skill_level: str
    evaluation_timestamp: str
    conversation_length: int
    token_usage: Dict[str, int]

class EvaluatorAgent:
    """
    🎯 LEARNING POINT: Educational AI Agent Architecture
    
    This class demonstrates several advanced patterns:
    1. Prompt Management Integration: Uses specialized prompt loader
    2. Multi-Stage Processing: Analysis → Feedback → Resources → Action Plan
    3. Educational Adaptation: Adjusts complexity based on student level
    4. Production Readiness: Error handling, logging, cost tracking
    5. Structured Output: Consistent, parseable results for system integration
    """
    
    def __init__(self, model: str = "gpt-4o-mini", temperature: float = 0.7):
        """
        Initialize the evaluator agent
        
        🧠 KEY CONCEPT: Model Selection for Educational AI
        - gpt-4o-mini: Cost-effective for educational use cases
        - Temperature 0.7: Balance between consistency and creativity
        - Configurable parameters for different educational contexts
        """
        self.model = model
        self.temperature = temperature
        self.prompt_loader = EvaluatorPromptLoader()
        self.config = get_evaluator_config()
        
        # Set up logging for production monitoring
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Initialize OpenAI client
        self.client = openai.OpenAI()
    
    # 🔧 LEARNING POINT: Multi-Stage AI Processing Pipeline
    def evaluate_pitch_conversation(self, 
                                  conversation_transcript: str,
                                  investor_decision: str,
                                  investor_reasons: List[str],
                                  student_context: Optional[Dict[str, Any]] = None) -> EvaluationResult:
        """
        Complete evaluation pipeline for student pitch conversations
        
        🎯 KEY CONCEPT: Educational AI Pipeline Design
        
        STAGE 1: Analysis - What happened in the conversation?
        STAGE 2: Assessment - How did the student perform?
        STAGE 3: Feedback - What specific improvements are needed?
        STAGE 4: Resources - What materials will help them improve?
        STAGE 5: Action Plan - What concrete steps should they take?
        
        This multi-stage approach ensures comprehensive, actionable feedback
        """
        
        start_time = datetime.now()
        total_tokens = 0
        
        try:
            self.logger.info("Starting pitch evaluation pipeline")
            
            # STAGE 1: Parse and analyze the conversation
            parsed_conversation = self.parse_conversation_transcript(conversation_transcript)
            
            analysis_result, analysis_tokens = self._analyze_conversation(
                parsed_conversation["clean_transcript"], investor_decision, investor_reasons
            )
            total_tokens += analysis_tokens
            
            # STAGE 2: Assess student skill level using parsed data
            skill_level = self._assess_skill_level(
                parsed_conversation, investor_decision, analysis_result
            )
            
            # Create student analysis object using parsed data
            student_analysis = StudentAnalysis(
                strengths=analysis_result.get("strengths", []),
                improvement_areas=analysis_result.get("improvement_areas", []),
                skill_level=skill_level,
                conversation_length=parsed_conversation["conversation_length"],
                investor_decision=investor_decision,
                investor_reasons=investor_reasons
            )
            
            # STAGE 3: Generate comprehensive feedback
            feedback_result, feedback_tokens = self._generate_detailed_feedback(
                student_analysis, conversation_transcript
            )
            total_tokens += feedback_tokens
            
            # STAGE 4: Recommend learning resources
            resources_result, resources_tokens = self._recommend_resources(
                student_analysis, student_context or {}
            )
            total_tokens += resources_tokens
            
            # STAGE 5: Create action plan
            action_plan_result, plan_tokens = self._create_action_plan(
                feedback_result, student_analysis
            )
            total_tokens += plan_tokens
            
            # Compile final evaluation result
            evaluation_result = EvaluationResult(
                overall_score=self._calculate_overall_score(analysis_result),
                strengths=analysis_result.get("strengths", []),
                improvement_areas=analysis_result.get("improvement_areas", []),
                detailed_feedback=feedback_result,
                specific_quotes=analysis_result.get("quotes", []),
                recommended_resources=resources_result,
                action_plan=action_plan_result,
                skill_level=skill_level,
                evaluation_timestamp=datetime.now().isoformat(),
                conversation_length=student_analysis.conversation_length,
                token_usage={
                    "total_tokens": total_tokens,
                    "analysis_tokens": analysis_tokens,
                    "feedback_tokens": feedback_tokens,
                    "resources_tokens": resources_tokens,
                    "plan_tokens": plan_tokens,
                    "estimated_cost": total_tokens * 0.000002  # GPT-4o-mini pricing
                }
            )
            
            evaluation_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Evaluation completed in {evaluation_time:.2f}s, {total_tokens} tokens")
            
            return evaluation_result
            
        except Exception as e:
            self.logger.error(f"Evaluation failed: {str(e)}")
            raise
    
    # 🎯 LEARNING POINT: Structured LLM Analysis
    def _analyze_conversation(self, transcript: str, decision: str, 
                            reasons: List[str]) -> Tuple[Dict[str, Any], int]:
        """
        Analyze conversation to extract key insights and performance indicators
        
        🧠 KEY CONCEPT: Structured AI Analysis
        - Uses specialized prompts for consistent analysis
        - Extracts specific, actionable insights rather than general impressions
        - Returns structured data that other pipeline stages can use
        """
        
        prompt = get_evaluator_analysis_prompt(transcript, decision, reasons)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=1500
        )
        
        analysis_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Parse structured insights from analysis
        analysis_result = self._parse_analysis_response(analysis_text)
        
        return analysis_result, tokens_used
    
    # 🔧 LEARNING POINT: Educational AI Adaptation
    def _assess_skill_level(self, parsed_conversation: Dict[str, Any], decision: str, 
                          analysis: Dict[str, Any]) -> str:
        """
        Assess student skill level for adaptive feedback complexity
        
        🎯 KEY CONCEPT: Adaptive Educational AI
        - Analyzes multiple performance indicators from parsed conversation
        - Adjusts feedback complexity to student capability
        - Prevents overwhelming beginners or boring advanced students
        """
        
        conversation_length = parsed_conversation["conversation_length"]
        student_word_count = parsed_conversation["student_word_count"]
        improvement_areas = analysis.get("improvement_areas", [])
        
        # Enhanced assessment using parsed conversation data
        return assess_student_level(conversation_length, decision, improvement_areas)
    
    # 🚀 LEARNING POINT: Comprehensive Feedback Generation
    def _generate_detailed_feedback(self, student_analysis: StudentAnalysis,
                                  transcript: str) -> Tuple[str, int]:
        """
        Generate comprehensive, structured feedback document
        
        🧠 KEY CONCEPT: Educational Feedback Design
        - Uses student skill level to adjust complexity
        - Includes specific examples from conversation
        - Provides actionable improvement suggestions
        - Formats as readable learning document
        """
        
        prompt = get_evaluator_feedback_prompt(student_analysis, transcript)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=2000
        )
        
        feedback = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        return feedback, tokens_used
    
    # 📚 LEARNING POINT: Intelligent Resource Matching
    def _recommend_resources(self, student_analysis: StudentAnalysis,
                           student_context: Dict[str, Any]) -> Tuple[List[Dict[str, str]], int]:
        """
        Recommend specific learning resources based on student gaps
        
        🎯 KEY CONCEPT: Personalized Learning Paths
        - Matches resources to specific improvement areas
        - Considers student context (industry, experience level)
        - Provides actionable next steps, not just generic advice
        """
        
        from evaluator_prompt_loader import get_evaluator_resources_prompt
        
        prompt = get_evaluator_resources_prompt(
            student_analysis.improvement_areas, 
            student_context
        )
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=1000
        )
        
        resources_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Parse resources into structured format
        resources = self._parse_resources_response(resources_text)
        
        return resources, tokens_used
    
    # 🗺️ LEARNING POINT: Actionable Learning Plans
    def _create_action_plan(self, feedback: str, 
                          student_analysis: StudentAnalysis) -> Tuple[List[Dict[str, Any]], int]:
        """
        Create prioritized, time-bound action plan for improvement
        
        🧠 KEY CONCEPT: Educational Action Planning
        - Breaks down feedback into concrete steps
        - Prioritizes based on impact and difficulty
        - Provides timelines and success criteria
        - Transforms analysis into actionable learning path
        """
        
        from evaluator_prompt_loader import EvaluatorPromptLoader
        loader = EvaluatorPromptLoader()
        
        prompt = loader.get_action_plan_prompt(feedback, student_analysis.skill_level)
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=800
        )
        
        plan_text = response.choices[0].message.content
        tokens_used = response.usage.total_tokens
        
        # Parse action plan into structured format
        action_plan = self._parse_action_plan_response(plan_text)
        
        return action_plan, tokens_used
    
    # 🧠 LEARNING POINT: Better Alternative to Regex - Structured AI Output
    def _get_structured_analysis(self, transcript: str, decision: str, 
                               reasons: List[str]) -> Tuple[Dict[str, Any], int]:
        """
        Alternative approach: Request structured JSON output from AI
        
        🎯 KEY CONCEPT: Structured AI Responses
        - Instead of parsing free text with regex, request specific format
        - More reliable than regex parsing
        - Easier to validate and handle errors
        """
        
        prompt = f"""
        Analyze this pitch conversation and return valid JSON only:
        
        CONVERSATION:
        {transcript}
        
        INVESTOR DECISION: {decision}
        REASONS: {', '.join(reasons)}
        
        Return JSON in this exact format:
        {{
            "strengths": ["strength1", "strength2", "strength3"],
            "improvement_areas": ["area1", "area2", "area3", "area4", "area5"],
            "key_quotes": [
                {{"quote": "exact quote from conversation", "analysis": "why this quote is significant"}},
                {{"quote": "another key quote", "analysis": "analysis of this quote"}}
            ],
            "communication_patterns": ["pattern1", "pattern2"],
            "investor_reactions": ["positive reaction", "negative reaction"]
        }}
        
        Only return valid JSON, no other text.
        """
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,  # Lower temperature for more consistent JSON
            max_tokens=1000
        )
        
        try:
            analysis_json = json.loads(response.choices[0].message.content)
            return analysis_json, response.usage.total_tokens
        except json.JSONDecodeError:
            # Fallback to original method if JSON parsing fails
            self.logger.warning("JSON parsing failed, falling back to text parsing")
            return self._analyze_conversation(transcript, decision, reasons)

    # 🧠 LEARNING POINT: Response Parsing and Structuring
    def _parse_analysis_response(self, analysis_text: str) -> Dict[str, Any]:
        """
        Parse LLM analysis response into structured data
        
        🎯 KEY CONCEPT: AI Output Structuring
        - Converts free-form text into structured data
        - Enables programmatic processing of AI insights
        - Provides consistent format for downstream processing
        """
        
        # Extract strengths
        strengths = []
        if "STRONGEST MOMENTS:" in analysis_text:
            strengths_section = analysis_text.split("STRONGEST MOMENTS:")[1].split("CRITICAL GAPS:")[0]
            strengths = [line.strip("- ").strip() for line in strengths_section.split('\n') if line.strip().startswith('-')]
        
        # Extract improvement areas
        improvement_areas = []
        if "CRITICAL GAPS:" in analysis_text:
            gaps_section = analysis_text.split("CRITICAL GAPS:")[1].split("MISSED OPPORTUNITIES:")[0]
            improvement_areas = [line.strip("- ").strip() for line in gaps_section.split('\n') if line.strip().startswith('-')]
        
        # Extract quotes (simplified parsing)
        quotes = []
        quote_pattern = r'"([^"]*)"'
        found_quotes = re.findall(quote_pattern, analysis_text)
        for quote in found_quotes[:3]:  # Limit to most relevant quotes
            quotes.append({"quote": quote, "analysis": "Key conversation moment"})
        
        return {
            "strengths": strengths[:3],  # Top 3 strengths
            "improvement_areas": improvement_areas[:5],  # Top 5 areas
            "quotes": quotes
        }
    
    def _parse_resources_response(self, resources_text: str) -> List[Dict[str, str]]:
        """Parse resource recommendations into structured format"""
        resources = []
        
        # Simple parsing - could be enhanced with more sophisticated NLP
        lines = resources_text.split('\n')
        current_resource = {}
        
        for line in lines:
            if line.startswith('📖') or line.startswith('**'):
                if current_resource:
                    resources.append(current_resource)
                # Extract resource name
                name = line.replace('📖', '').replace('**', '').strip()
                current_resource = {"name": name, "description": "", "action": ""}
            elif line.startswith('• Why it helps:'):
                current_resource["description"] = line.replace('• Why it helps:', '').strip()
            elif line.startswith('• Action item:'):
                current_resource["action"] = line.replace('• Action item:', '').strip()
        
        if current_resource:
            resources.append(current_resource)
        
        return resources[:3]  # Limit to prevent overwhelm
    
    def _parse_action_plan_response(self, plan_text: str) -> List[Dict[str, Any]]:
        """Parse action plan into structured format"""
        action_items = []
        
        # Extract priority sections
        priorities = ["PRIORITY 1", "PRIORITY 2", "PRIORITY 3"]
        
        for i, priority in enumerate(priorities):
            if priority in plan_text:
                section = plan_text.split(priority)[1]
                if i < len(priorities) - 1 and priorities[i + 1] in section:
                    section = section.split(priorities[i + 1])[0]
                
                # Extract timeframe
                timeframe = "This Week" if "Week" in priority else "2 Weeks" if "2" in priority else "Month 1"
                
                # Simple action extraction
                lines = [line.strip() for line in section.split('\n') if line.strip()]
                if lines:
                    action_items.append({
                        "priority": i + 1,
                        "timeframe": timeframe,
                        "action": lines[0] if lines else "Improve pitch based on feedback",
                        "description": " ".join(lines[1:3]) if len(lines) > 1 else ""
                    })
        
        return action_items
    
    def _calculate_overall_score(self, analysis: Dict[str, Any]) -> str:
        """Calculate overall performance score"""
        strengths_count = len(analysis.get("strengths", []))
        gaps_count = len(analysis.get("improvement_areas", []))
        
        if strengths_count >= 3 and gaps_count <= 2:
            return "excellent"
        elif strengths_count >= 2 and gaps_count <= 4:
            return "good"
        else:
            return "needs_improvement"
    
    # 🔧 LEARNING POINT: Conversation Format Handling
    def parse_conversation_transcript(self, raw_transcript: str) -> Dict[str, Any]:
        """
        Parse conversation transcript into structured format
        
        🧠 KEY CONCEPT: Data Structure Normalization
        - Handles different transcript formats consistently
        - Extracts metadata like conversation length, participant roles
        - Cleans up formatting for better AI analysis
        """
        
        # Split by participant markers
        messages = []
        current_speaker = None
        current_message = ""
        
        for line in raw_transcript.split('\n'):
            line = line.strip()
            if not line:
                continue
                
            if line.startswith('🤖') or line.startswith('👤'):
                # Save previous message if exists
                if current_speaker and current_message:
                    messages.append({
                        "speaker": current_speaker,
                        "message": current_message.strip()
                    })
                
                # Start new message
                if line.startswith('🤖'):
                    current_speaker = "investor"
                    current_message = line.replace('🤖', '').strip()
                else:
                    current_speaker = "student" 
                    current_message = line.replace('👤', '').strip()
            else:
                # Continue current message
                current_message += " " + line
        
        # Don't forget the last message
        if current_speaker and current_message:
            messages.append({
                "speaker": current_speaker,
                "message": current_message.strip()
            })
        
        # Extract metadata
        student_messages = [msg for msg in messages if msg["speaker"] == "student"]
        investor_messages = [msg for msg in messages if msg["speaker"] == "investor"]
        
        return {
            "messages": messages,
            "conversation_length": len(student_messages),
            "total_exchanges": len(messages),
            "student_word_count": sum(len(msg["message"].split()) for msg in student_messages),
            "clean_transcript": "\n".join([f"{msg['speaker'].title()}: {msg['message']}" for msg in messages])
        }

    # 📁 LEARNING POINT: File-Based Output for Student Reference
    def save_evaluation_to_file(self, evaluation: EvaluationResult, 
                               student_name: str = "student", 
                               format_type: str = "markdown") -> str:
        """
        Save evaluation to file for student reference
        
        🎯 KEY CONCEPT: Persistent Learning Documents
        - Creates files students can reference repeatedly
        - Supports multiple formats (markdown, txt, json)
        - Enables offline study and progress tracking
        """
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "markdown":
            filename = f"pitch_evaluation_{student_name}_{timestamp}.md"
            content = self.format_evaluation_for_display(evaluation)
        elif format_type == "json":
            filename = f"pitch_evaluation_{student_name}_{timestamp}.json"
            content = json.dumps(asdict(evaluation), indent=2, default=str)
        else:  # txt format
            filename = f"pitch_evaluation_{student_name}_{timestamp}.txt"
            content = self.format_evaluation_for_display(evaluation).replace('#', '').replace('*', '')
        
        # Create evaluations directory if it doesn't exist
        os.makedirs("evaluations", exist_ok=True)
        filepath = os.path.join("evaluations", filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        self.logger.info(f"Evaluation saved to: {filepath}")
        return filepath

    # 🎨 LEARNING POINT: User-Friendly Output Formatting
    def format_evaluation_for_display(self, evaluation: EvaluationResult) -> str:
        """
        Format evaluation result for student display
        
        🧠 KEY CONCEPT: Educational UX Design
        - Presents complex analysis in digestible format
        - Uses visual hierarchy and emojis for engagement
        - Balances comprehensive feedback with readability
        """
        
        formatted_output = f"""
# 🎯 PITCH EVALUATION RESULTS

**Overall Performance:** {evaluation.overall_score.title()} ⭐
**Skill Level:** {evaluation.skill_level.title()}
**Evaluation Date:** {evaluation.evaluation_timestamp[:10]}

---

## ✅ STRENGTHS - What You Did Well

{chr(10).join(f"• {strength}" for strength in evaluation.strengths)}

---

## 🔧 AREAS FOR IMPROVEMENT

{chr(10).join(f"• {area}" for area in evaluation.improvement_areas)}

---

{evaluation.detailed_feedback}

---

## 📚 RECOMMENDED RESOURCES

{chr(10).join(f"**{res.get('name', 'Resource')}**{chr(10)}{res.get('description', '')}{chr(10)}" for res in evaluation.recommended_resources)}

---

## 🗺️ YOUR ACTION PLAN

{chr(10).join(f"**Priority {item.get('priority', 1)} ({item.get('timeframe', 'Soon')}):** {item.get('action', '')}" for item in evaluation.action_plan)}

---

*Evaluation completed in {evaluation.token_usage.get('total_tokens', 0)} tokens*
*Estimated cost: ${evaluation.token_usage.get('estimated_cost', 0):.4f}*
        """
        
        return formatted_output.strip()

# 🔄 LEARNING POINT: Data Integration Patterns
def integrate_with_investor_agent(investor_conversation_data: Dict[str, Any]) -> EvaluationResult:
    """
    Integration function showing how evaluator connects with investor agent
    
    🧠 KEY CONCEPT: Agent-to-Agent Data Flow
    - Standardized data format between agents
    - Error handling for missing or malformed data
    - Clean separation of concerns between agents
    
    Expected investor_conversation_data format:
    {
        "transcript": "full conversation text",
        "final_decision": "convinced" or "not convinced", 
        "decision_reasons": ["reason1", "reason2", "reason3"],
        "student_info": {"name": "...", "hobby": "..."},
        "conversation_metadata": {"length": 5, "persona": "anna"}
    }
    """
    
    # Validate required data
    required_fields = ["transcript", "final_decision", "decision_reasons"]
    for field in required_fields:
        if field not in investor_conversation_data:
            raise ValueError(f"Missing required field: {field}")
    
    # Extract data with defaults
    transcript = investor_conversation_data["transcript"]
    decision = investor_conversation_data["final_decision"]
    reasons = investor_conversation_data["decision_reasons"]
    student_context = investor_conversation_data.get("student_info", {})
    
    # Create evaluator and run evaluation
    evaluator = EvaluatorAgent()
    result = evaluator.evaluate_pitch_conversation(
        conversation_transcript=transcript,
        investor_decision=decision,
        investor_reasons=reasons,
        student_context=student_context
    )
    
    # Save evaluation file
    student_name = student_context.get("name", "student").lower().replace(" ", "_")
    evaluator.save_evaluation_to_file(result, student_name, "markdown")
    
    return result

# 🌟 LEARNING POINT: Simple Interface for Complex System
def evaluate_student_pitch(conversation_transcript: str,
                         investor_decision: str, 
                         investor_reasons: List[str],
                         student_context: Optional[Dict[str, Any]] = None) -> EvaluationResult:
    """
    Simple interface for evaluating student pitch conversations
    
    🎯 KEY CONCEPT: API Design for Educational AI
    - Hides complexity behind simple function call
    - Provides comprehensive evaluation with minimal input
    - Returns structured data for easy integration
    """
    evaluator = EvaluatorAgent()
    return evaluator.evaluate_pitch_conversation(
        conversation_transcript, investor_decision, investor_reasons, student_context
    )

# 🧪 LEARNING POINT: Educational AI Testing Strategy
def test_evaluator_agent():
    """Test the evaluator agent with sample data"""
    print("🧪 Testing Evaluator Agent")
    print("=" * 50)
    
    # Sample conversation transcript
    sample_transcript = """
    🤖 Anna Ito: Hi there! I'm Anna Ito, and I'm excited to hear your elevator pitch today.
    👤 You: I am Muhammad Salman an AI Engineer with a passion to revolutionise the worlds education infrastructure using AI
    🤖 Anna Ito: That's great! Can you elaborate on the specific problem you're targeting?
    👤 You: i will be using AI to teach underpreviledged student in a one on one setting
    🤖 Anna Ito: How do you plan to ensure the AI adapts to different learning styles?
    👤 You: i dont know
    """
    
    try:
        evaluator = EvaluatorAgent()
        
        result = evaluator.evaluate_pitch_conversation(
            conversation_transcript=sample_transcript,
            investor_decision="not convinced",
            investor_reasons=["Unclear solution details", "No market research", "Insufficient planning"],
            student_context={"hobby": "programming", "age": "25", "location": "Boston"}
        )
        
        print("✅ Evaluation completed successfully!")
        print(f"📊 Overall Score: {result.overall_score}")
        print(f"🎯 Skill Level: {result.skill_level}")
        print(f"💰 Token Usage: {result.token_usage['total_tokens']}")
        print(f"💵 Estimated Cost: ${result.token_usage['estimated_cost']:.4f}")
        print(f"📝 Strengths Found: {len(result.strengths)}")
        print(f"🔧 Improvement Areas: {len(result.improvement_areas)}")
        print(f"📚 Resources Recommended: {len(result.recommended_resources)}")
        print(f"🗺️ Action Items: {len(result.action_plan)}")
        
        # Save evaluation to file instead of just printing
        print("\n" + "="*50)
        print("SAVING EVALUATION TO FILES:")
        print("="*50)
        
        # Save in multiple formats
        md_file = evaluator.save_evaluation_to_file(result, "muhammad_salman", "markdown")
        json_file = evaluator.save_evaluation_to_file(result, "muhammad_salman", "json")
        txt_file = evaluator.save_evaluation_to_file(result, "muhammad_salman", "txt")
        
        print(f"📄 Markdown: {md_file}")
        print(f"📊 JSON: {json_file}")
        print(f"📝 Text: {txt_file}")
        
        # Show preview of markdown content
        print("\n" + "="*50)
        print("MARKDOWN PREVIEW (first 500 chars):")
        print("="*50)
        formatted = evaluator.format_evaluation_for_display(result)
        print(formatted[:500] + "..." if len(formatted) > 500 else formatted)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_evaluator_agent()