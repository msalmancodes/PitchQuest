"""
Investor Prompt Loader - Dedicated loader for investor agent
Keeps investor prompts separate and organized
"""

import yaml
import os
from typing import Dict, Any

class InvestorPromptLoader:
    """
    Handles investor-specific prompt loading and management
    Parallel structure to mentor prompt loader for consistency
    """
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir
        self._cache = {}  # Cache for performance
    
    def load_prompts(self) -> Dict[str, Any]:
        """
        Load investor prompts from YAML with caching
        
        Returns:
            Complete investor prompt configuration
        """
        if "investor_prompts" in self._cache:
            return self._cache["investor_prompts"]
        
        filepath = os.path.join(self.prompts_dir, "investor_prompts.yaml")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                prompts = yaml.safe_load(file)
                self._cache["investor_prompts"] = prompts
                return prompts
        except FileNotFoundError:
            raise FileNotFoundError(f"Investor prompt file not found: {filepath}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in investor prompts: {e}")
    
    def get_persona_info(self, persona: str) -> Dict[str, Any]:
        """
        Get specific investor persona information
        
        Args:
            persona: "aria", "anna", or "adam"
        
        Returns:
            Persona configuration including name, personality, voice mapping
        """
        prompts = self.load_prompts()
        personas = prompts["investor"]["personas"]
        
        if persona not in personas:
            raise ValueError(f"Unknown persona: {persona}. Available: {list(personas.keys())}")
        
        return personas[persona]
    
    def get_base_system_prompt(self) -> str:
        """Get the base system prompt used by all investor personas"""
        prompts = self.load_prompts()
        return prompts["investor"]["base_system_prompt"]
    
    def get_opening_prompt(self, persona: str) -> str:
        """
        Get opening greeting prompt for specific persona
        
        Args:
            persona: Investor persona to use
        
        Returns:
            Complete prompt for generating opening greeting
        """
        prompts = self.load_prompts()
        persona_info = self.get_persona_info(persona)
        base_prompt = self.get_base_system_prompt()
        
        return prompts["investor"]["tasks"]["generate_opening"].format(
            base_system_prompt=base_prompt,
            persona_personality=persona_info["personality"],
            persona_name=persona_info["name"]
        )
    
    def get_response_prompt(self, persona: str, conversation_context: str, 
                           last_message: str) -> str:
        """
        Get response generation prompt for ongoing conversation
        
        Args:
            persona: Investor persona
            conversation_context: Recent conversation history
            last_message: Student's last message
        
        Returns:
            Complete prompt for generating contextual response
        """
        prompts = self.load_prompts()
        persona_info = self.get_persona_info(persona)
        base_prompt = self.get_base_system_prompt()
        
        return prompts["investor"]["tasks"]["generate_response"].format(
            base_system_prompt=base_prompt,
            persona_personality=persona_info["personality"],
            persona_name=persona_info["name"],
            conversation_context=conversation_context,
            last_message=last_message
        )
    
    def get_final_decision_prompt(self, persona: str, conversation_context: str) -> str:
        """
        Get final investment decision prompt for session wrap-up
        
        Args:
            persona: Investor persona making the decision
            conversation_context: Recent conversation summary
        
        Returns:
            Prompt for generating structured investment decision
        """
        prompts = self.load_prompts()
        persona_info = self.get_persona_info(persona)
        base_prompt = self.get_base_system_prompt()
        
        return prompts["investor"]["tasks"]["generate_final_decision"].format(
            base_system_prompt=base_prompt,
            persona_personality=persona_info["personality"],
            persona_name=persona_info["name"],
            conversation_context=conversation_context
        )
    
    def get_config(self) -> Dict[str, Any]:
        """Get investor configuration settings"""
        prompts = self.load_prompts()
        return prompts.get("config", {})
    
    def get_persona_profiles(self) -> Dict[str, Dict[str, str]]:
        """
        Get user-friendly persona profiles for selection interface
        
        Returns:
            Simplified profiles for student selection
        """
        profiles = {}
        persona_info = self.load_prompts()["investor"]["personas"]
        
        # Map persona data to user-friendly profiles
        profile_mapping = {
            "aria": {
                "name": "Aria Iyer",
                "specialty": "Early-stage startups",
                "style": "Analytical but friendly",
                "focus": "Market fit, competitive advantage, unit economics",
                "best_for": "Students with clear business models",
                "difficulty": "Medium",
                "avatar": "👩‍💼"
            },
            "anna": {
                "name": "Anna Ito",
                "specialty": "Technical deep-dives", 
                "style": "Rigorous and challenging",
                "focus": "Technical feasibility, scalability, implementation",
                "best_for": "Tech-focused startups",
                "difficulty": "Hard",
                "avatar": "👩‍💻"
            },
            "adam": {
                "name": "Adam Ingram",
                "specialty": "Growth and scaling",
                "style": "Supportive and enthusiastic",
                "focus": "Customer acquisition, market expansion, team building", 
                "best_for": "First-time entrepreneurs",
                "difficulty": "Easy",
                "avatar": "👨‍💼"
            }
        }
        
        return profile_mapping
    
    def recommend_persona(self, student_info: Dict[str, Any]) -> str:
        """
        Recommend best investor persona based on student profile
        
        Args:
            student_info: Student information from mentor session
        
        Returns:
            Recommended persona ID ("aria", "anna", or "adam")
        """
        business_idea = student_info.get("business_idea", "").lower()
        hobby = student_info.get("hobby", "").lower()
        
        # Tech-focused ideas → Anna (technical deep-dive)
        tech_keywords = ["ai", "programming", "software", "app", "platform", 
                        "algorithm", "hci", "machine learning", "data", "tech"]
        if any(keyword in business_idea + hobby for keyword in tech_keywords):
            return "anna"
        
        # Business/market focused → Aria (analytical)
        business_keywords = ["market", "business", "revenue", "customers", 
                           "monetize", "sales", "growth", "strategy"]
        if any(keyword in business_idea for keyword in business_keywords):
            return "aria"
        
        # Default/first-time entrepreneurs → Adam (supportive)
        return "adam"
    
    def get_persona_voice_mapping(self, persona: str) -> str:
        """
        Get voice mapping for persona (for future voice integration)
        
        Args:
            persona: Investor persona
        
        Returns:
            Voice ID for text-to-speech systems
        """
        persona_info = self.get_persona_info(persona)
        return persona_info.get("voice_mapping", "alloy")

# Global instance for easy access
investor_prompt_loader = InvestorPromptLoader()

# Convenience functions for clean imports
def get_investor_opening_prompt(persona: str) -> str:
    """Get investor opening prompt"""
    return investor_prompt_loader.get_opening_prompt(persona)

def get_investor_response_prompt(persona: str, conversation_context: str, 
                                last_message: str) -> str:
    """Get investor response prompt"""
    return investor_prompt_loader.get_response_prompt(persona, conversation_context, last_message)

def get_investor_final_decision_prompt(persona: str, conversation_context: str) -> str:
    """Get investor final decision prompt"""
    return investor_prompt_loader.get_final_decision_prompt(persona, conversation_context)

def get_investor_personas() -> Dict[str, Dict[str, str]]:
    """Get investor persona profiles"""
    return investor_prompt_loader.get_persona_profiles()

def recommend_investor_persona(student_info: Dict[str, Any]) -> str:
    """Recommend investor persona based on student info"""
    return investor_prompt_loader.recommend_persona(student_info)

def get_investor_config() -> Dict[str, Any]:
    """Get investor configuration"""
    return investor_prompt_loader.get_config()

# Testing function
def test_investor_prompt_loader():
    """Test the investor prompt loader functionality"""
    print("🧪 Testing Investor Prompt Loader")
    print("=" * 50)
    
    try:
        # Test basic loading
        config = get_investor_config()
        print("✅ Config loaded successfully")
        
        # Test persona profiles
        profiles = get_investor_personas()
        print(f"✅ Found {len(profiles)} investor personas:")
        for persona_id, profile in profiles.items():
            print(f"  - {profile['name']} ({profile['difficulty']})")
        
        # Test recommendation system
        student_info = {"business_idea": "AI programming education", "hobby": "HCI"}
        recommended = recommend_investor_persona(student_info)
        print(f"✅ Recommendation for tech student: {recommended}")
        
        # Test prompt generation
        opening_prompt = get_investor_opening_prompt("aria")
        print(f"✅ Opening prompt generated: {len(opening_prompt)} characters")
        
        print("\n🎯 All tests passed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_investor_prompt_loader()