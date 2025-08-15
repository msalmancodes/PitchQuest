"""
Orchestrator Service - Web API version of your LangGraph routing logic

MIRRORS session_orchestrator.py routing functions:
- should_continue_mentor() → _determine_routing_after_mentor()
- should_continue_investor() → _determine_routing_after_investor()
- should_continue_evaluator() → always complete

SEAMLESS FLOW: Mentor → Investor → Evaluator → Complete → New Session
"""

import uuid
import logging
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from .mentor_service import mentor_service
from .investor_service import investor_service
from .evaluator_service import evaluator_service
from .. import crud

logger = logging.getLogger(__name__)

class OrchestratorService:
    """
    Central orchestrator that replicates your LangGraph workflow in web API form
    
    CORE CONCEPT: 
    Provides single endpoint that automatically routes messages to the correct agent
    based on session state, exactly like your working LangGraph implementation.
    """
    
    def process_message(self, session_id: Optional[str], message: str, selected_investor: Optional[str], db: Session) -> Dict[str, Any]:
        """
        Process message with automatic routing (mirrors LangGraph behavior)
        
        FLOW LOGIC (from your session_orchestrator.py):
        1. Determine current phase from database state
        2. Route to appropriate service (mentor/investor/evaluator)
        3. Check for automatic phase transitions
        4. Handle session completion and new session creation
        
        Args:
            session_id: Existing session or None for new session
            message: User's message
            selected_investor: User's investor choice (Aria, Anna, Adam)
            db: Database session
            
        Returns:
            Unified response with routing metadata
        """
        
        logger.info(f"🎯 Orchestrator processing message for session: {session_id}")
        
        # Step 1: Handle session creation
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"🆕 Generated new session: {session_id}")
        
        # Step 2: Load session and determine current phase
        db_session = crud.get_session(db, session_id)
        
        # 🔧 FIX: Create session in DB if it doesn't exist
        if not db_session:
            crud.create_session(db, {
                "id": session_id,
                "current_phase": "mentor"
            })
            db_session = crud.get_session(db, session_id)
            logger.info(f"📝 Created new session in DB: {session_id}")
        
        current_phase = self._determine_phase(db_session)
        
        logger.info(f"📍 Session {session_id} → Phase: {current_phase}")
        
        # Step 3: Route to appropriate handler
        try:
            if current_phase == "mentor":
                result = self._handle_mentor_phase(session_id, message, db)
                
            elif current_phase == "investor":
                result = self._handle_investor_phase(session_id, message, selected_investor, db)
                
            elif current_phase == "evaluator":
                result = self._handle_evaluator_phase(session_id, db)
                
            elif current_phase == "complete":
                result = self._handle_complete_session(session_id, message)
                
            elif current_phase == "ended_not_ready":
                result = self._handle_not_ready_session(session_id, message)
                
            else:
                raise ValueError(f"Unknown phase: {current_phase}")
            
            # Step 4: Add orchestrator metadata
            result.update({
                "orchestrator_info": {
                    "routed_to": current_phase,
                    "original_session_id": session_id,
                    "routing_successful": True,
                    "timestamp": str(uuid.uuid4())[:8]  # Short ID for logging
                }
            })
            
            logger.info(f"✅ Successfully routed to {current_phase}")
            return result
            
        except Exception as e:
            logger.error(f"❌ Orchestrator error: {e}")
            return self._handle_error(session_id, current_phase, str(e))
    
    def _determine_phase(self, db_session) -> str:
        """
        Determine current phase from database state
        
        MIRRORS your LangGraph routing logic exactly:
        - should_continue_mentor() from session_orchestrator.py
        - should_continue_investor() from session_orchestrator.py
        - should_continue_evaluator() from session_orchestrator.py
        """
        
        if not db_session:
            return "mentor"  # New session starts with mentor
        
        # Check for terminated sessions first
        if db_session.current_phase == "ended_not_ready":
            return "ended_not_ready"
        
        if db_session.current_phase == "complete":
            return "complete"
        
        # Mirror should_continue_mentor() logic:
        # if mentor_complete and student_ready → "to_investor"
        # if mentor_complete and not student_ready → "end_not_ready"
        # else → "continue_mentor"
        
        if not db_session.mentor_complete:
            return "mentor"  # Continue mentoring
        
        # CRITICAL ROUTING DECISION (mirrors your LangGraph):
        if db_session.mentor_complete and not db_session.student_ready_for_investor:
            return "ended_not_ready"  # Session ends here (like LangGraph END)
        
        # Mirror should_continue_investor() logic:
        # if pitch_complete → "to_evaluator"
        # else → "continue_investor"
        
        if not db_session.investor_complete:
            return "investor"  # Ready for pitching
        
        # Mirror should_continue_evaluator() logic:
        # always returns "end"
        
        if not db_session.evaluator_complete:
            return "evaluator"  # Auto-trigger evaluation
        
        return "complete"  # All phases done
    
    def _handle_mentor_phase(self, session_id: str, message: str, db: Session) -> Dict[str, Any]:
        """
        Handle mentor phase with transition detection
        
        LOGIC: Process message → Check completion → Detect readiness → Route accordingly
        """
        
        logger.info(f"🎓 Processing mentor message for {session_id}")
        
        # Use existing mentor service
        mentor_result = mentor_service.process_mentor_message(session_id, message, db)
        
        # Normalize response format (convert "ai_response" → "response")
        normalized = {
            "session_id": session_id,
            "response": mentor_result.get("ai_response", ""),  # Normalize key name
            "current_phase": "mentor",
            "phase_complete": mentor_result.get("mentor_complete", False),
            
            # Include routing fields for frontend visibility
            "mentor_complete": mentor_result.get("mentor_complete", False),
            "student_ready_for_investor": mentor_result.get("student_ready_for_investor", False),
            
            "success": mentor_result.get("success", True),
            "metadata": {
                "question_count": mentor_result.get("question_count", 0),
                "student_info": mentor_result.get("student_info", {})
            }
        }
        
        # Check for phase transition (mirror LangGraph should_continue_mentor)
        if mentor_result.get("mentor_complete"):
            student_ready = mentor_result.get("student_ready_for_investor", False)
            
            if student_ready:
                # Successful transition to investor (like LangGraph "to_investor")
                # 🔧 FIX: Persist transition to DB
                crud.update_session(db, session_id, {
                    "current_phase": "investor",
                    "mentor_complete": True,
                    "student_ready_for_investor": True
                })
                
                normalized.update({
                    "next_phase": "investor",
                    "transition_message": "🎯 Excellent! You're ready to pitch. Please select an investor and send your first message.",
                    "auto_advance": True
                })
                logger.info(f"✅ {session_id} → Ready for investor")
                
            else:
                # Session ends (like LangGraph "end_not_ready") 
                crud.update_session(db, session_id, {"current_phase": "ended_not_ready"})
                normalized.update({
                    "next_phase": "ended_not_ready",
                    "session_ended": True,
                    "end_reason": "mentor_recommends_more_preparation",
                    "end_message": "📚 Your mentor recommends more preparation before pitching to investors. Take time to refine your business idea!"
                })
                logger.info(f"⏹️ {session_id} → Session ended (not ready)")
        
        return normalized
    
    def _handle_investor_phase(self, session_id: str, message: str, selected_investor: Optional[str], db: Session) -> Dict[str, Any]:
        """
        Handle investor phase with TRUE auto-evaluation
        
        LOGIC: Process pitch → Check completion → Immediately run evaluation → Return combined response
        🔧 FIXED: Handles investor selection AND runs evaluation automatically when pitch completes
        """
        
        logger.info(f"💼 Processing investor message for {session_id}")
        
        # 🔧 FIX #1: Handle investor selection
        if selected_investor:
            logger.info(f"👥 User selected investor: {selected_investor}")
            # Store selection in session
            crud.update_session(db, session_id, {"selected_investor": selected_investor})
        
        # Use existing investor service
        investor_result = investor_service.process_investor_message(session_id, message, db)
        
        # Normalize response format (investor already uses "response" key)
        normalized = {
            "session_id": session_id,
            "response": investor_result.get("response", ""),
            "current_phase": "investor",
            "phase_complete": investor_result.get("pitch_complete", False),
            
            # Include routing fields
            "investor_complete": investor_result.get("pitch_complete", False),
            "mentor_complete": investor_result.get("mentor_complete", True),
            "student_ready_for_investor": investor_result.get("student_ready_for_investor", True),
            
            "metadata": {
                "investor_persona": investor_result.get("investor_persona"),
                "exchange_count": investor_result.get("exchange_count", 0),
                "persona_selection_needed": investor_result.get("persona_selection_needed", False),
                "ready_for_pitch": investor_result.get("ready_for_pitch", False),
                "selected_investor": selected_investor  # Include selection
            }
        }
        
        # 🔧 FIX #2: TRUE auto-evaluation - run immediately when pitch completes
        if investor_result.get("pitch_complete"):
            logger.info(f"🎉 {session_id} → Pitch complete, running evaluation immediately")
            
            try:
                # Persist investor completion first
                crud.update_session(db, session_id, {
                    "investor_complete": True,
                    "current_phase": "evaluator"
                })
                
                # Run evaluation immediately
                eval_result = evaluator_service.evaluate_pitch(session_id, db)
                
                # Persist evaluation completion
                crud.update_session(db, session_id, {
                    "evaluator_complete": True,
                    "current_phase": "complete"
                })
                
                # 🔧 FIX #3: Use full markdown content instead of arrays
                evaluation_text = f"""

{eval_result.get('detailed_feedback', 'Evaluation not available')}

---

**Ready for another practice round?** Type anything to start fresh!"""
                
                # Return combined investor + evaluation response
                normalized.update({
                    "response": investor_result.get("response", "") + evaluation_text,
                    "current_phase": "complete",  # Skip directly to complete
                    "phase_complete": True,
                    "evaluator_complete": True,
                    "auto_triggered": True,
                    "evaluation_results": {
                        "overall_score": eval_result.get("overall_score", 0),
                        "performance_level": eval_result.get("performance_level", "beginner"),
                        "strengths": eval_result.get("strengths", []),
                        "improvements": eval_result.get("improvements", []),
                        "score_breakdown": eval_result.get("score_breakdown", {}),
                        "feedback_document_path": eval_result.get("feedback_document_path"),
                        "detailed_feedback": eval_result.get("detailed_feedback", "")
                    }
                })
                
                logger.info(f"✅ {session_id} → Auto-evaluation complete, session finished")
                
            except Exception as e:
                logger.error(f"❌ Auto-evaluation failed: {e}")
                # Fallback to manual evaluation
                normalized.update({
                    "next_phase": "evaluator",
                    "transition_message": "🎉 Excellent pitch! Please type 'evaluate' to see your feedback.",
                    "auto_advance": False
                })
        
        return normalized
    
    def _handle_evaluator_phase(self, session_id: str, db: Session) -> Dict[str, Any]:
        """
        Handle evaluator phase (triggered by routing when investor_complete = True)
        
        LOGIC: Run evaluation → Save results → Mark complete
        🔧 FIXED: Uses full markdown content instead of parsing arrays
        """
        
        logger.info(f"📊 Running evaluation for {session_id}")
        
        # Run evaluation (triggered by routing)
        eval_result = evaluator_service.evaluate_pitch(session_id, db)
        
        # 🔧 FIX: Persist evaluation completion to DB
        crud.update_session(db, session_id, {
            "evaluator_complete": True,
            "current_phase": "complete"
        })
        
        # 🔧 FIX: Use full markdown content instead of parsing arrays
        response_text = f"""{eval_result.get('detailed_feedback', 'Evaluation not available')}

---

**Ready for another practice round?** Type anything to start fresh!"""
        
        return {
            "session_id": session_id,
            "response": response_text,
            "current_phase": "complete",
            "phase_complete": True,
            
            # Include all completion flags
            "mentor_complete": True,
            "investor_complete": True,
            "evaluator_complete": True,
            
            "evaluation_results": {
                "overall_score": eval_result.get("overall_score", 0),
                "performance_level": eval_result.get("performance_level", "beginner"),
                "strengths": eval_result.get("strengths", []),
                "improvements": eval_result.get("improvements", []),
                "score_breakdown": eval_result.get("score_breakdown", {}),
                "feedback_document_path": eval_result.get("feedback_document_path"),
                "detailed_feedback": eval_result.get("detailed_feedback", "")
            },
            "success": eval_result.get("success", True)
        }
    
    def _handle_complete_session(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Handle messages to completed sessions → Start new session
        
        LOGIC: Complete session + new message = Fresh practice round
        """
        
        new_session_id = str(uuid.uuid4())
        logger.info(f"🔄 {session_id} complete → Creating new session {new_session_id}")
        
        return {
            "session_id": new_session_id,  # NEW session ID
            "response": f"🎉 Previous session complete! Starting a fresh practice round.\n\nHello! I'm your AI mentor. I'm here to help you develop and practice your business pitch. What would you like to work on today?",
            "current_phase": "mentor",
            "phase_complete": False,
            
            # Reset completion flags for new session
            "mentor_complete": False,
            "investor_complete": False,
            "evaluator_complete": False,
            "student_ready_for_investor": False,
            
            "new_session_created": True,
            "previous_session_id": session_id
        }
    
    def _handle_not_ready_session(self, session_id: str, message: str) -> Dict[str, Any]:
        """
        Handle messages to 'not ready' sessions → Start new session
        
        LOGIC: Previous mentor said not ready + new message = Fresh start
        """
        
        new_session_id = str(uuid.uuid4())
        logger.info(f"📚 {session_id} not ready → Creating new session {new_session_id}")
        
        return {
            "session_id": new_session_id,  # NEW session ID
            "response": f"📚 Your previous mentor recommended more preparation. No worries - let's start fresh!\n\nHello! I'm your AI mentor. Take your time to develop your business idea. What would you like to work on?",
            "current_phase": "mentor",
            "phase_complete": False,
            
            # Reset completion flags for new session
            "mentor_complete": False,
            "investor_complete": False, 
            "evaluator_complete": False,
            "student_ready_for_investor": False,
            
            "new_session_created": True,
            "previous_session_id": session_id,
            "previous_end_reason": "not_ready"
        }
    
    def _handle_error(self, session_id: str, phase: str, error: str) -> Dict[str, Any]:
        """Handle errors gracefully while maintaining session continuity"""
        return {
            "session_id": session_id,
            "response": "I encountered an issue processing your message. Please try again - I'm here to help!",
            "current_phase": phase,
            "phase_complete": False,
            "error": True,
            "error_details": error,
            "success": False,
            "orchestrator_info": {
                "routed_to": phase,
                "error_occurred": True,
                "routing_successful": False
            }
        }

# Create singleton instance
orchestrator_service = OrchestratorService()