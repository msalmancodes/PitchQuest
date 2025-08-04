"""
Evaluator Prompt Loader - Advanced prompt management for comprehensive feedback
Demonstrates professional-grade prompt engineering and resource optimization
"""

import yaml
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# 🧠 LEARNING POINT: Type hints and dataclasses improve code quality and IDE support
@dataclass
class StudentAnalysis:
    """Structured container for student performance analysis"""
    strengths: List[str]
    improvement_areas: List[str]
    skill_level: str  # beginner, intermediate, advanced
    conversation_length: int
    investor_decision: str
    investor_reasons: List[str]

class EvaluatorPromptLoader:
    """
    🎯 LEARNING POINT: Advanced Prompt Management Architecture
    
    This class demonstrates several key software engineering principles:
    1. Separation of Concerns: Data (YAML) vs Logic (Python) vs Presentation (Prompts)
    2. Performance Optimization: Caching, selective loading, lazy evaluation
    3. Educational AI Design: Content filtering, resource matching, adaptive complexity
    4. Professional Patterns: Error handling, logging, configuration management
    """
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir
        self._cache = {}  # Performance optimization through caching
        self._resource_cache = {}  # Separate cache for processed resources
    
    # 🔧 LEARNING POINT: Lazy Loading Pattern
    # Only load data when actually needed, not at initialization
    def load_prompts(self) -> Dict[str, Any]:
        """
        Load evaluator prompts with caching for performance
        
        🧠 KEY CONCEPT: Caching Pattern
        - Check cache first (O(1) lookup)
        - Load from disk only if needed (expensive I/O)
        - Store result for future use
        """
        if "evaluator_prompts" in self._cache:
            return self._cache["evaluator_prompts"]
        
        filepath = os.path.join(self.prompts_dir, "evaluator_prompts.yaml")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                prompts = yaml.safe_load(file)
                self._cache["evaluator_prompts"] = prompts
                return prompts
        except FileNotFoundError:
            raise FileNotFoundError(f"Evaluator prompt file not found: {filepath}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in evaluator prompts: {e}")
    
    # 🎯 LEARNING POINT: Data Transformation Methods
    # Convert complex data structures into LLM-friendly formats
    def format_evaluation_criteria(self, criteria_dict: Dict[str, Any]) -> str:
        """
        Transform criteria dictionary into readable prompt text
        
        🧠 KEY CONCEPT: Data Serialization for LLMs
        - Structured data (dicts/lists) → Human-readable text
        - Preserves all information while being LLM-parseable
        - Maintains consistent formatting across all evaluations
        """
        formatted_criteria = []
        total_weight = sum(criterion["weight"] for criterion in criteria_dict.values())
        
        formatted_criteria.append("EVALUATION RUBRIC:")
        formatted_criteria.append("=" * 50)
        
        for criterion_name, details in criteria_dict.items():
            percentage = (details["weight"] / total_weight) * 100
            formatted_criteria.extend([
                f"\n📊 {criterion_name.upper().replace('_', ' ')} ({percentage:.0f}%)",
                f"   Description: {details['description']}",
                f"   🌟 Excellent: {details['excellent']}",
                f"   ✅ Good: {details['good']}",
                f"   🔧 Needs Work: {details['needs_work']}"
            ])
        
        return "\n".join(formatted_criteria)
    
    # 🎯 LEARNING POINT: Intelligent Resource Filtering
    # This is where AI becomes truly educational - personalized recommendations
    def filter_relevant_resources(self, improvement_areas: List[str], 
                                 max_resources: int = 3) -> Dict[str, Any]:
        """
        Select most relevant resources based on student's specific needs
        
        🧠 KEY CONCEPT: Adaptive Content Delivery
        - Analyze student gaps against available resources
        - Prioritize resources that address multiple gaps
        - Limit cognitive load (max 3 resources to avoid overwhelm)
        - This transforms generic advice into personalized learning plans
        """
        prompts = self.load_prompts()
        all_resources = prompts["evaluator"]["resource_templates"]
        
        # Create resource-to-improvement mapping
        resource_relevance = {}
        
        # Map improvement areas to resource categories
        area_mapping = {
            "problem_articulation": ["improvement_resources", "market_research"],
            "solution_clarity": ["pitch_frameworks", "core_pitch_principles"],
            "market_understanding": ["improvement_resources", "market_research"],
            "competitive_advantage": ["improvement_resources", "competitive_analysis"],
            "business_model": ["improvement_resources", "business_models"],
            "communication_skills": ["core_pitch_principles", "improvement_resources"],
            "adaptability": ["practice_and_feedback", "core_pitch_principles"]
        }
        
        # Score resources based on relevance to student's gaps
        filtered_resources = {}
        for area in improvement_areas:
            if area in area_mapping:
                for resource_category in area_mapping[area]:
                    if resource_category in all_resources:
                        filtered_resources[resource_category] = all_resources[resource_category]
        
        # 🎯 LEARNING POINT: Intelligent Truncation
        # If too many resources, prioritize core principles and frameworks
        if len(filtered_resources) > max_resources:
            priority_order = ["core_pitch_principles", "pitch_frameworks", "expert_resources"]
                # ✅ FIXED: Convert to list first, then slice, then back to dict
            priority_items = [
                (key, filtered_resources[key]) 
                for key in priority_order 
                if key in filtered_resources
            ][:max_resources]  # Now we can slice the list
            
            filtered_resources = dict(priority_items)  # Convert back to dict
                
        return filtered_resources
    
    # 🚀 LEARNING POINT: Composite Prompt Generation
    # This method demonstrates how to build complex, context-aware prompts
    def get_comprehensive_feedback_prompt(self, 
                                        student_analysis: StudentAnalysis,
                                        conversation_transcript: str) -> str:
        """
        Generate optimized prompt for comprehensive student feedback
        
        🧠 KEY CONCEPT: Context-Aware Prompt Engineering
        - Combines multiple data sources into coherent prompt
        - Adapts complexity based on student skill level
        - Includes only relevant resources (token optimization)
        - Maintains educational consistency across all evaluations
        """
        prompts = self.load_prompts()
        base_prompt = prompts["evaluator"]["base_system_prompt"]
        criteria = prompts["evaluator"]["evaluation_criteria"]
        
        # Format evaluation criteria for LLM consumption
        formatted_criteria = self.format_evaluation_criteria(criteria)
        
        # Get relevant resources based on student gaps
        relevant_resources = self.filter_relevant_resources(
            student_analysis.improvement_areas,
            max_resources=3
        )
        
        # 🎯 LEARNING POINT: Adaptive Complexity
        # Adjust prompt complexity based on student skill level
        complexity_guidance = {
            "beginner": "Focus on foundational concepts and basic improvements. Use encouraging language.",
            "intermediate": "Provide moderate detail with some advanced concepts. Balance challenge with support.",
            "advanced": "Offer sophisticated analysis with industry-level insights. Challenge them to think strategically."
        }
        
        # Build the complete prompt
        complete_prompt = prompts["evaluator"]["tasks"]["generate_detailed_feedback"].format(
            base_system_prompt=base_prompt,
            conversation_analysis=f"TRANSCRIPT:\n{conversation_transcript}\n\nINVESTOR DECISION: {student_analysis.investor_decision}\nREASONS: {', '.join(student_analysis.investor_reasons)}",
            evaluation_criteria=formatted_criteria,
            skill_level_guidance=complexity_guidance.get(student_analysis.skill_level, complexity_guidance["intermediate"]),
            relevant_resources=str(relevant_resources)
        )
        
        return complete_prompt
    
    # 🎯 LEARNING POINT: Specialized Prompt Methods
    # Each method handles a specific evaluation task with optimized prompts
    def get_analysis_prompt(self, conversation_transcript: str, 
                          investor_decision: str, investor_reasons: List[str]) -> str:
        """Generate prompt for conversation analysis phase"""
        prompts = self.load_prompts()
        base_prompt = prompts["evaluator"]["base_system_prompt"]
        
        return prompts["evaluator"]["tasks"]["analyze_full_conversation"].format(
            base_system_prompt=base_prompt,
            full_conversation=conversation_transcript,
            investor_decision=investor_decision,
            investor_reasons=", ".join(investor_reasons)
        )
    
    def get_resource_recommendation_prompt(self, improvement_areas: List[str],
                                         student_context: Dict[str, Any]) -> str:
        """Generate prompt for resource recommendations"""
        prompts = self.load_prompts()
        base_prompt = prompts["evaluator"]["base_system_prompt"]
        
        # Get filtered resources to avoid token bloat
        relevant_resources = self.filter_relevant_resources(improvement_areas)
        
        return prompts["evaluator"]["tasks"]["recommend_resources"].format(
            base_system_prompt=base_prompt,
            student_improvement_areas=", ".join(improvement_areas),
            student_context=str(student_context),
            available_resources=str(relevant_resources)
        )
    
    def get_action_plan_prompt(self, feedback_summary: str, 
                             skill_level: str) -> str:
        """Generate prompt for action plan creation"""
        prompts = self.load_prompts()
        base_prompt = prompts["evaluator"]["base_system_prompt"]
        
        return prompts["evaluator"]["tasks"]["create_action_plan"].format(
            base_system_prompt=base_prompt,
            feedback_summary=feedback_summary,
            student_skill_level=skill_level
        )
    
    # 🔧 LEARNING POINT: Configuration Management
    # Centralized settings that can be modified without code changes
    def get_config(self) -> Dict[str, Any]:
        """Get evaluator configuration settings"""
        prompts = self.load_prompts()
        return prompts.get("config", {})
    
    # 🎯 LEARNING POINT: Helper Methods for External Integration
    # These methods provide clean interfaces for other parts of the system
    def assess_student_skill_level(self, conversation_length: int, 
                                 investor_decision: str,
                                 improvement_areas: List[str]) -> str:
        """
        Assess student skill level based on performance indicators
        
        🧠 KEY CONCEPT: Automated Skill Assessment
        - Uses conversation metrics to infer competency
        - Enables adaptive feedback complexity
        - Supports personalized learning paths
        """
        # Simple heuristic - could be enhanced with ML in future
        if len(improvement_areas) <= 2 and investor_decision == "convinced":
            return "advanced"
        elif len(improvement_areas) <= 4 and conversation_length >= 5:
            return "intermediate"
        else:
            return "beginner"
    
    def extract_improvement_areas_from_criteria(self, evaluation_scores: Dict[str, str]) -> List[str]:
        """Extract areas needing improvement from evaluation scores"""
        improvement_areas = []
        for criterion, score in evaluation_scores.items():
            if score in ["needs_work", "poor"]:
                improvement_areas.append(criterion)
        return improvement_areas

    def get_pitch_performance_scoring_prompt(self, full_conversation: str, investor_decision: str, investor_reasons: List[str]) -> str:
        """Get prompt for scoring pitch performance"""
        prompts = self.load_prompts()
        base_prompt = prompts["evaluator"]["base_system_prompt"]
        
        return prompts["evaluator"]["tasks"]["score_pitch_performance"].format(
            base_system_prompt=base_prompt,
            full_conversation=full_conversation,
            investor_decision=investor_decision,
            investor_reasons=", ".join(investor_reasons)
        )

# 🌟 LEARNING POINT: Global Instance Pattern
# Provides easy access while maintaining single instance for caching benefits
evaluator_prompt_loader = EvaluatorPromptLoader()

# 🎯 LEARNING POINT: Clean API Design
# These convenience functions provide simple interfaces for complex operations
def get_evaluator_feedback_prompt(student_analysis: StudentAnalysis, 
                                conversation_transcript: str) -> str:
    """Get comprehensive feedback prompt for student evaluation"""
    return evaluator_prompt_loader.get_comprehensive_feedback_prompt(
        student_analysis, conversation_transcript
    )

def get_evaluator_analysis_prompt(conversation_transcript: str,
                                investor_decision: str, 
                                investor_reasons: List[str]) -> str:
    """Get conversation analysis prompt"""
    return evaluator_prompt_loader.get_analysis_prompt(
        conversation_transcript, investor_decision, investor_reasons
    )

def get_evaluator_resources_prompt(improvement_areas: List[str],
                                 student_context: Dict[str, Any]) -> str:
    """Get resource recommendation prompt"""
    return evaluator_prompt_loader.get_resource_recommendation_prompt(
        improvement_areas, student_context
    )

def get_pitch_performance_scoring_prompt(full_conversation: str, investor_decision: str, investor_reasons: List[str]) -> str:
    """Get prompt for scoring pitch performance"""
    return evaluator_prompt_loader.get_pitch_performance_scoring_prompt(
        full_conversation, investor_decision, investor_reasons
    )

def assess_student_level(conversation_length: int, investor_decision: str,
                        improvement_areas: List[str]) -> str:
    """Assess student skill level for adaptive feedback"""
    return evaluator_prompt_loader.assess_student_skill_level(
        conversation_length, investor_decision, improvement_areas
    )

def get_evaluator_config() -> Dict[str, Any]:
    """Get evaluator configuration"""
    return evaluator_prompt_loader.get_config()

# 🧪 LEARNING POINT: Comprehensive Testing Strategy
def test_evaluator_prompt_loader():
    """Test the evaluator prompt loader functionality"""
    print("🧪 Testing Evaluator Prompt Loader")
    print("=" * 50)
    
    try:
        # Test basic loading
        config = get_evaluator_config()
        print("✅ Config loaded successfully")
        print(f"   Minimum conversation length: {config['evaluation_settings']['minimum_conversation_length']}")
        
        # Test criteria formatting
        loader = EvaluatorPromptLoader()
        prompts = loader.load_prompts()
        criteria = prompts["evaluator"]["evaluation_criteria"]
        formatted = loader.format_evaluation_criteria(criteria)
        print(f"✅ Criteria formatted: {len(formatted)} characters")
        
        # Test resource filtering
        improvement_areas = ["problem_articulation", "communication_skills"]
        filtered = loader.filter_relevant_resources(improvement_areas)
        print(f"✅ Resource filtering: {len(filtered)} categories selected")
        
        # Test skill assessment
        skill_level = assess_student_level(5, "not convinced", improvement_areas)
        print(f"✅ Skill assessment: {skill_level}")
        
        # Test prompt generation
        student_analysis = StudentAnalysis(
            strengths=["Clear passion", "Good problem identification"],
            improvement_areas=improvement_areas,
            skill_level=skill_level,
            conversation_length=5,
            investor_decision="not convinced",
            investor_reasons=["Unclear solution", "No market research"]
        )
        
        prompt = loader.get_comprehensive_feedback_prompt(
            student_analysis, "Sample conversation transcript"
        )
        print(f"✅ Comprehensive prompt generated: {len(prompt)} characters")
        print(f"   Token estimate: ~{len(prompt.split()) * 1.3:.0f} tokens")
        
        print("\n🎯 All tests passed!")
        print(f"💡 Estimated cost per evaluation: ~${len(prompt.split()) * 1.3 * 0.000002:.4f}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_evaluator_prompt_loader()