# pitchquest_api/services/evaluator_service.py
"""
Evaluator Service - Analyzes pitch conversations and generates feedback
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session as DatabaseSession
from datetime import datetime
import logging
import json

# Set up logging
logger = logging.getLogger(__name__)

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

# Import evaluator agent
from agents.evaluator_agent import evaluator_node, EvaluatorState

# Import database operations
from pitchquest_api import models, crud

class EvaluatorService:
    """Service layer for evaluator agent"""
    
    def __init__(self):
        """Initialize evaluator service"""
        pass
    
    def evaluate_pitch(
        self,
        session_id: str,
        db: DatabaseSession
    ) -> Dict[str, Any]:
        """
        Evaluate a completed pitch session
        
        Args:
            session_id: Session to evaluate
            db: Database session
            
        Returns:
            Evaluation results with feedback
        """
        
        # Load session from database
        db_session = crud.get_session(db, session_id)
        
        if not db_session:
            return {
                "success": False,
                "error": "Session not found",
                "session_id": session_id
            }
        
        # Check if already evaluated
        existing_evaluation = crud.get_evaluation_by_session(db, session_id)
        if existing_evaluation:
            return {
                "success": True,
                "session_id": session_id,
                "already_evaluated": True,
                "overall_score": existing_evaluation.overall_score,
                "strengths": existing_evaluation.strengths,
                "improvements": existing_evaluation.improvements,
                "detailed_feedback": existing_evaluation.detailed_feedback
            }
        
        # Get investor messages for transcript
        messages = crud.get_messages_by_agent(db, session_id, "investor")
        
        # Convert to agent format
        agent_messages = []
        for msg in messages:
            agent_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        # Build state for evaluator agent
        evaluator_state: EvaluatorState = {
            # Student info from session
            "student_info": {
                "name": db_session.student_name or "Student",
                "hobby": db_session.student_hobby,
                "business_idea": db_session.business_idea,
                "location": db_session.student_location
            },
            # Investor conversation
            "messages": agent_messages,
            "investor_persona": db_session.selected_investor or "aria",
            "pitch_complete": db_session.investor_complete or False,
            "exchange_count": len([m for m in agent_messages if m["role"] == "user"]),
            # Evaluator fields (will be filled)
            "evaluation_summary": {},
            "feedback_document_path": "",
            "evaluator_complete": False
        }
        
        try:
            # Run evaluator agent
            result_state = evaluator_node(evaluator_state)
            
            # Extract evaluation summary
            evaluation_summary = result_state.get("evaluation_summary", {})
            
            # Create evaluation record in database
            evaluation_data = {
                "session_id": session_id,
                "overall_score": evaluation_summary.get("overall_score", 0),
                "hook_score": None,  # Can be extracted from score_breakdown if needed
                "problem_score": None,
                "solution_score": None,
                "strengths": json.dumps(evaluation_summary.get("strengths", [])),
                "improvements": json.dumps(evaluation_summary.get("improvements", [])),
                "detailed_feedback": evaluation_summary.get("detailed_feedback", "No feedback generated")
            }
            
            # Extract specific scores if available
            score_breakdown = evaluation_summary.get("score_breakdown", {})
            if score_breakdown:
                # Map to database fields if they match
                if "hook" in score_breakdown:
                    evaluation_data["hook_score"] = self._score_to_number(score_breakdown["hook"])
                if "problem_articulation" in score_breakdown:
                    evaluation_data["problem_score"] = self._score_to_number(score_breakdown["problem_articulation"])
                if "solution_clarity" in score_breakdown:
                    evaluation_data["solution_score"] = self._score_to_number(score_breakdown["solution_clarity"])
            
            # Save evaluation to database
            db_evaluation = crud.create_evaluation(db, evaluation_data)
            
            # Update session to mark evaluator complete
            session_updates = {
                "evaluator_complete": True,
                "current_phase": "complete"
            }
            crud.update_session(db, session_id, session_updates)
            
            # Save evaluation message
            eval_msg_data = {
                "session_id": session_id,
                "role": "assistant",
                "content": f"Evaluation Complete. Score: {evaluation_summary.get('overall_score', 0)}/100. Performance Level: {evaluation_summary.get('performance_level', 'beginner')}",
                "agent_type": "evaluator"
            }
            crud.create_message(db, eval_msg_data)
            
            return {
                "success": True,
                "session_id": session_id,
                "overall_score": evaluation_summary.get("overall_score", 0),
                "performance_level": evaluation_summary.get("performance_level", ""),
                "score_breakdown": score_breakdown,
                "strengths": evaluation_summary.get("strengths", []),
                "improvements": evaluation_summary.get("improvements", []),
                "investor_decision": evaluation_summary.get("investor_decision", ""),
                "feedback_document_path": result_state.get("feedback_document_path", ""),
                "evaluator_complete": True,
                "current_phase": "complete"
            }
            
        except Exception as e:
            logger.error(f"Evaluation error for session {session_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "session_id": session_id
            }
    
    def _score_to_number(self, score_text: str) -> int:
        """Convert text scores to numbers"""
        mapping = {
            "excellent": 90,
            "good": 75,
            "needs_work": 50
        }
        return mapping.get(score_text, 50)
    
    def get_evaluation_status(self, session_id: str, db: DatabaseSession) -> Dict[str, Any]:
        """
        Get evaluation status for a session
        
        Args:
            session_id: Session identifier
            db: Database session
            
        Returns:
            Evaluation status
        """
        db_session = crud.get_session(db, session_id)
        
        if not db_session:
            return {"exists": False, "error": "Session not found"}
        
        evaluation = crud.get_evaluation_by_session(db, session_id)
        
        if evaluation:
            return {
                "exists": True,
                "evaluated": True,
                "overall_score": evaluation.overall_score,
                "strengths": evaluation.strengths,
                "improvements": evaluation.improvements,
                "detailed_feedback": evaluation.detailed_feedback,
                "created_at": evaluation.created_at.isoformat() if evaluation.created_at else None
            }
        else:
            return {
                "exists": True,
                "evaluated": False,
                "ready_for_evaluation": db_session.investor_complete or False
            }

# Create singleton
evaluator_service = EvaluatorService()