"""
Professional YAML Prompt Loader
Industry standard approach for managing LLM prompts
"""

import yaml
import os
from typing import Dict, Any

class PromptLoader:
    """
    Professional prompt management system using YAML
    Used by companies like OpenAI, Anthropic for prompt engineering
    """
    
    def __init__(self, prompts_dir: str = "prompts"):
        self.prompts_dir = prompts_dir
        self._cache = {}  # Cache loaded prompts for performance
    
    def load_prompts(self, filename: str) -> Dict[str, Any]:
        """
        Load prompts from YAML file with caching
        
        Args:
            filename: YAML filename (without extension)
        
        Returns:
            Dictionary containing all prompts from the file
        """
        if filename in self._cache:
            return self._cache[filename]
        
        filepath = os.path.join(self.prompts_dir, f"{filename}.yaml")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                prompts = yaml.safe_load(file)
                self._cache[filename] = prompts
                return prompts
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {filepath}")
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {filepath}: {e}")
    
    def get_mentor_prompt(self, student_info: Dict[str, Any] = None, 
                         phase: str = "info_gathering") -> str:
        """
        Get complete mentor system prompt with context
        
        Args:
            student_info: Student's hobby, business idea, etc.
            phase: Current conversation phase
        
        Returns:
            Complete system prompt for mentor
        """
        prompts = self.load_prompts("mentor_prompts")
        mentor_config = prompts["mentor"]
        
        # Start with base system prompt
        system_prompt = mentor_config["system_prompt"]
        
        # Add student context if available
        if student_info and student_info.get("hobby"):
            hobby_context = mentor_config["context"]["hobby_context"].format(
                hobby=student_info["hobby"]
            )
            system_prompt += "\n\n" + hobby_context
        
        # Add phase-specific guidance
        phase_prompt = mentor_config["phases"].get(phase, 
                                                 mentor_config["phases"]["info_gathering"])
        system_prompt += "\n\n" + phase_prompt
        
        return system_prompt
    
    def get_task_prompt(self, task: str, **kwargs) -> str:
        """
        Get prompt for specific task with variable substitution
        
        Args:
            task: Task name (welcome, extract_info, etc.)
            **kwargs: Variables to substitute in prompt template
        
        Returns:
            Formatted prompt ready for LLM
        """
        prompts = self.load_prompts("mentor_prompts")
        task_prompt = prompts["mentor"]["tasks"][task]
        
        # Format template with provided variables
        return task_prompt.format(**kwargs)
    
    def get_config(self) -> Dict[str, Any]:
        """Get configuration settings for prompts"""
        prompts = self.load_prompts("mentor_prompts")
        return prompts.get("config", {})

# Global instance for easy access
prompt_loader = PromptLoader()

# Convenience functions for your existing code
def get_mentor_system_prompt(student_info: Dict[str, Any] = None, 
                           phase: str = "info_gathering") -> str:
    """Get mentor system prompt - matches your existing function signature"""
    return prompt_loader.get_mentor_prompt(student_info, phase)

def get_welcome_prompt() -> str:
    """Get welcome message prompt"""
    base_prompt = prompt_loader.get_mentor_prompt()
    task_prompt = prompt_loader.get_task_prompt("welcome")
    return base_prompt + "\n\n" + task_prompt

def get_extraction_prompt(message: str) -> str:
    """Get information extraction prompt"""
    return prompt_loader.get_task_prompt("extract_info", message=message)

def get_response_prompt(system_prompt: str, conversation_context: str, 
                       last_message: str, student_info: dict) -> str:
    """Get contextual response generation prompt"""
    return prompt_loader.get_task_prompt(
        "generate_response",
        system_prompt=system_prompt,
        conversation_context=conversation_context,
        last_message=last_message,
        student_info=student_info
    )

def get_assessment_prompt(conversation: str, exchange_count: int) -> str:
    """Get readiness assessment prompt"""
    return prompt_loader.get_task_prompt("assess_readiness",
                                       conversation=conversation, 
                                       exchange_count=exchange_count)

def get_feedback_and_transition_prompt(conversation: str, exchange_count: int) -> str:
    """Get comprehensive feedback prompt for max exchanges reached"""
    return prompt_loader.get_task_prompt("feedback_and_transition", 
                                       conversation=conversation,
                                       exchange_count=exchange_count)