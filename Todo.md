Great catches — both are solvable in the orchestrator with small, surgical changes. Here are drop-in fixes so you get (1) explicit investor choice and (2) truly automatic evaluation.
1) Don’t auto-assign an investor persona
Problem: When selected_investor is missing, you’re defaulting to “Anna Ito”.
Fix: In the orchestrator’s investor handler, short-circuit and ask the client to choose, instead of auto-assigning.
Patch (orchestrator_service.py)
@@ def _handle_investor_phase(self, session_id: str, user_message: str, db: Session) -> Dict[str, Any]:
-    # (current code likely reads selected_investor and defaults to "anna")
-    selected = db_session.selected_investor or "anna"
+    selected = db_session.selected_investor
+    if not selected:
+        # Do NOT auto-assign. Tell the UI to present choices.
+        return {
+            "success": True,
+            "response": "Please choose your investor persona to continue: Aria Iyer, Anna Ito, or Adam Ingram.",
+            "current_phase": "investor",
+            "phase_complete": False,
+            "mentor_complete": bool(db_session.mentor_complete),
+            "student_ready_for_investor": bool(db_session.student_ready_for_investor),
+            "investor_complete": False,
+            "evaluator_complete": False,
+            "next_phase": "investor",
+            "auto_triggered": False,
+            "metadata": {
+                "persona_selection_needed": True,
+                "personas": [
+                    {"id": "aria", "name": "Aria Iyer"},
+                    {"id": "anna", "name": "Anna Ito"},
+                    {"id": "adam", "name": "Adam Ingram"},
+                ]
+            }
+        }
Frontend: when metadata.persona_selection_needed === true, open a modal and POST the choice back (e.g., "message":"__select_persona:anna" or a dedicated endpoint you may already have).
2) Auto-trigger the evaluator immediately when the investor completes
Problem: You set auto_evaluation_message but wait for another user turn.
Fix: Call the evaluator service inside the same request that finishes the investor phase and return its results right away.
Minimal helper (evaluator_service.py)
Add a tiny convenience wrapper (if you don’t already have one):
# pitchquest_api/services/evaluator_service.py
class EvaluatorService:
    # ... existing code ...

    def auto_evaluate(self, session_id: str, db) -> Dict[str, Any]:
        """
        Run evaluation immediately based on the current session transcript,
        without requiring a user prompt.
        """
        # If your process method requires a message, pass a sentinel that you ignore.
        return self.process_evaluator_message(session_id=session_id, user_message=None, db=db)

# Global
evaluator_service = EvaluatorService()
If your process_evaluator_message currently expects a non-empty string, make it treat None/"" as “evaluate now from transcript”.
Orchestrator change (orchestrator_service.py)
Call the evaluator right after the investor completes and return the evaluation as the response:
@@ def _handle_investor_phase(self, session_id: str, user_message: str, db: Session) -> Dict[str, Any]:
-    investor_result = investor_service.process_investor_message(session_id, user_message, db)
+    investor_result = investor_service.process_investor_message(session_id, user_message, db)

     # Normal investor turn (continue asking questions)
-    if not investor_result.get("investor_complete"):
+    if not investor_result.get("investor_complete"):
         return {
             "success": True,
             "response": investor_result["ai_response"],
             "current_phase": "investor",
             "phase_complete": False,
             "mentor_complete": bool(investor_result.get("mentor_complete", False)),
             "student_ready_for_investor": bool(investor_result.get("student_ready_for_investor", False)),
             "investor_complete": False,
             "evaluator_complete": False,
             "next_phase": "investor",
             "auto_triggered": False,
             "metadata": investor_result.get("metadata", {}),
         }

     # ✅ Investor just finished — immediately run evaluator
+    try:
+        eval_result = evaluator_service.auto_evaluate(session_id=session_id, db=db)
+    except Exception as e:
+        # Graceful fallback if evaluator throws; keep phase consistent
+        return {
+            "success": False,
+            "error": True,
+            "error_details": f"Auto-evaluation failed: {e}",
+            "response": "Your pitch concluded. I tried to generate feedback but hit an error. Please try again.",
+            "current_phase": "investor",
+            "phase_complete": True,
+            "mentor_complete": True,
+            "student_ready_for_investor": True,
+            "investor_complete": True,
+            "evaluator_complete": False,
+            "next_phase": "evaluator",
+            "auto_triggered": False,
+        }

+    # Happy path: return evaluator feedback immediately
+    return {
+        "success": True,
+        "error": False,
+        "response": eval_result["ai_response"],  # show feedback now
+        "current_phase": "evaluator",
+        "phase_complete": True,
+        "mentor_complete": True,
+        "student_ready_for_investor": True,
+        "investor_complete": True,
+        "evaluator_complete": True,  # mark done if your evaluator is single-turn
+        "next_phase": "complete",
+        "auto_triggered": True,
+        "auto_evaluation_message": None,
+        "evaluation_results": eval_result.get("evaluation_results"),
+        "metadata": {"ready_for_pitch": False},
+    }
If your evaluator is multi-turn, set evaluator_complete: False, phase_complete: False, and next_phase:"evaluator", but still return the first feedback chunk immediately.
Smoke tests (copy/paste)
A) Persona gating (should ask for a selection, not auto-assign)
Start a new session that hasn’t chosen an investor.
Send any message to enter investor phase.
Expect: metadata.persona_selection_needed = true and a personas array.
B) Auto-evaluation (should not wait for another user turn)
Proceed through investor Q&A until completion.
Expect (same response):
current_phase: "evaluator"
response: evaluator feedback
investor_complete: true, evaluator_complete: true
next_phase: "complete"
auto_triggered: true
Optional polish (schemas)
Make these defaults non-nullable in schemas.py to simplify the frontend:
success: bool = True
error: bool = False
phase_complete: bool = False
mentor_complete: bool = False
student_ready_for_investor: bool = False
investor_complete: bool = False
evaluator_complete: bool = False
Why this matches the pedagogy
Immediate, automatic hand-off preserves the learning loop and gives timely feedback without extra friction — exactly the flow emphasized in the PitchQuest design (mentor → practice → feedback with minimal student overhead). It keeps the cognitive focus on reflection rather than UI mechanics.
If you paste your current orchestrator_service.py (_handle_investor_phase) and evaluator_service.py signatures, I’ll tailor the diff to your exact function names/return shapes.