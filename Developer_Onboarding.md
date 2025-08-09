# 🗂️ REPOSITORY SCAFFOLDING - Next Session Development Guide

## 🎯 QUICK START FOR NEXT SESSION

### **🚀 Immediate Setup (5 minutes):**
```bash
cd PitchQuest
source pitchquest_env/bin/activate
uvicorn pitchquest_api.main:app --reload --host 0.0.0.0 --port 8000
# Keep this running, open new terminal for work
```

### **🔍 Validation Check:**
- Visit: `http://localhost:8000/docs`
- Confirm mentor endpoints working
- Test one mentor message to verify bug fix

---

## 📁 FILE FOCUS MAP - What to Work On

### **🎯 SESSION 1: Investor Service (40 min)**

**📝 FILES TO CREATE:**
```
services/investor_service.py         # ⭐ MAIN TASK - Copy mentor_service.py pattern
routers/investor.py                  # 🔗 API endpoints - Copy mentor router pattern
```

**📖 TEMPLATE FILES (Copy From):**
```
services/mentor_service.py           # ⭐ PROVEN PATTERN - Your template
routers/mentor.py                    # 🔗 Working router - Copy this structure
```

**📚 REFERENCE FILES (Study First):**
```
agents/investor_agent.py             # 💼 UNDERSTAND: investor_node() function signature
prompts/investor_prompts.yaml        # 💼 UNDERSTAND: investor conversation logic  
prompts/investor_prompt_loader.py    # 💼 UNDERSTAND: prompt loading functions
```

**🔧 MODIFICATION FILES:**
```
pitchquest_api/main.py              # 🔗 ADD: investor router registration
pitchquest_api/schemas.py           # 📋 ADD: investor-specific request/response schemas
```

### **🎯 SESSION 2: Evaluator Service (40 min)**

**📝 FILES TO CREATE:**
```
services/evaluator_service.py        # 📊 MAIN TASK - Copy mentor pattern + transcript analysis
routers/evaluator.py                 # 🔗 API endpoints for evaluation
```

**📖 TEMPLATE FILES (Copy From):**
```
services/mentor_service.py           # ⭐ Base service pattern
routers/mentor.py                    # 🔗 Base router pattern
```

**📚 REFERENCE FILES (Study First):**
```
agents/evaluator_agent.py            # 📊 UNDERSTAND: evaluator_node() function signature
models.py                           # 🗄️ REVIEW: evaluations table schema
crud.py                             # 🗄️ CHECK: evaluation CRUD operations
```

### **🎯 SESSION 3: Orchestrator Service (40 min)**

**📝 FILES TO CREATE:**
```
services/orchestrator_service.py     # 🏗️ MAIN TASK - Complete workflow service
routers/orchestrator.py              # 🔗 Single workflow endpoint
```

**📖 TEMPLATE FILES (Study & Replicate):**
```
session_orchestrator.py              # ⭐ REPLICATE: Complete LangGraph logic
services/mentor_service.py           # 🔧 REUSE: Database patterns
```

**🔧 INTEGRATION FILES:**
```
pitchquest_api/main.py              # 🔗 ADD: orchestrator router registration
```

---

## 🧩 KEY PATTERNS TO REPLICATE

### **🎯 Service Layer Pattern (FROM mentor_service.py):**
```python
# 1. Agent Integration Pattern
from agents.[agent]_agent import [agent]_node, process_single_[agent]_message

# 2. State Loading Pattern  
def _load_session_state(session_id, db):
    # Get from database
    # Reconstruct agent state format
    # Handle field mapping

# 3. State Saving Pattern
def _save_session_state(session_id, updated_state, new_message, ai_response, db):
    # Map state to database fields
    # Create/update session record
    # Save conversation messages

# 4. Main Processing Pattern
def process_[agent]_message(session_id, user_message, db):
    # Load state → Process with agent → Save state → Return response
```

### **🔗 Router Pattern (FROM routers/mentor.py):**
```python
# 1. Import pattern
from ..services.[agent]_service import [agent]_service

# 2. Endpoint pattern
@router.post("/message")
async def process_message(request: MessageRequest, db: Session = Depends(get_db)):
    # Call service → Return result

# 3. Registration pattern (in main.py)
from .routers import [agent]
app.include_router([agent].router, prefix="/api/[agent]", tags=["[agent]"])
```

---

## 🔍 CRITICAL UNDERSTANDING POINTS

### **🤖 Agent Function Signatures (RESEARCH FIRST):**

**❓ Key Questions to Answer:**
- **Investor:** What does `investor_node(state)` expect? Same state structure as mentor?
- **Evaluator:** What does `evaluator_node(state)` expect? Needs conversation transcript?
- **State Compatibility:** Can we use same state loading/saving logic across all agents?

### **🗄️ Database Field Mappings (FROM Cursor Analysis):**

**Field Name Translations:**
```python
# session_orchestrator.py    →    Database Schema
investor_persona             →    selected_investor
pitch_complete              →    investor_complete  
student_ready_for_investor  →    (derived from text parsing)
exchange_count              →    (derived from message count)
```

### **📋 State Structure Requirements:**
```python
# Each agent needs:
SessionState = {
    "student_info": {},         # ✅ Working (mapped to individual columns)
    "messages": [],             # ✅ Working (messages table)
    "current_phase": "",        # ✅ Working (sessions.current_phase)
    
    # Mentor fields
    "mentor_complete": bool,         # ✅ Working
    "student_ready_for_investor": bool,  # ✅ Fixed with text parsing
    
    # Investor fields (TO IMPLEMENT)
    "investor_persona": str,         # Map to selected_investor
    "pitch_complete": bool,          # Map to investor_complete
    
    # Evaluator fields (TO IMPLEMENT)  
    "evaluation_summary": {},        # Map to evaluations table
    "overall_score": int             # evaluations.overall_score
}
```

---

## 🧪 TESTING STRATEGY

### **🔧 Development Testing Pattern:**
```bash
# 1. Test individual service in isolation
python -c "from services.[agent]_service import test_[agent]_service; test_[agent]_service()"

# 2. Test via FastAPI docs
# Visit http://localhost:8000/docs → Test endpoints

# 3. Test database persistence  
python test_postgres.py

# 4. Test complete workflow
# Use orchestrator endpoint for full mentor → investor → evaluator flow
```

### **📊 Validation Checklist:**
- [ ] Agent service processes messages correctly
- [ ] Database state saves and loads properly
- [ ] Field mappings work (orchestrator names ↔ database schema)
- [ ] Agent transitions happen correctly
- [ ] Educational workflow integrity maintained

---

## 🚨 POTENTIAL ISSUES TO WATCH FOR

### **⚠️ Known Challenges:**
1. **Agent Function Compatibility:** Investor/evaluator might expect different state structure
2. **Field Name Mismatches:** session_orchestrator.py vs. database schema naming
3. **State Transitions:** Complex logic for determining when to move between agents
4. **Persona Selection:** Investor agent needs persona choice logic
5. **Transcript Analysis:** Evaluator needs complete conversation history

### **🔧 Debug Resources:**
- **Database Check:** `python test_postgres.py`
- **Agent Testing:** Test agents individually before web integration
- **State Inspection:** Add logging to see what state structure agents expect
- **Message Flow:** Verify conversation messages save/load correctly

---

## 📋 SESSION WORKFLOW

### **🎯 Recommended Development Order:**

**1. Research Phase (10 minutes):**
- Study `agents/investor_agent.py` - understand function signature
- Review `prompts/investor_prompts.yaml` - understand conversation flow
- Check existing investor logic in session_orchestrator.py

**2. Investor Service (30 minutes):**
- Copy `mentor_service.py` → `investor_service.py`
- Adapt for investor_node() function
- Handle persona selection and pitch logic
- Test via FastAPI docs

**3. Evaluator Service (30 minutes):**
- Copy mentor pattern → `evaluator_service.py`  
- Adapt for transcript analysis
- Connect to evaluations database table
- Test evaluation generation

**4. Orchestrator Service (40 minutes):**
- Create single workflow service
- Replicate session_orchestrator.py routing logic
- Test complete educational flow
- Validate against local LangGraph behavior

**5. Integration Testing (20 minutes):**
- Test all endpoints working together
- Verify database consistency
- Validate educational workflow preservation

---

## 🎯 SUCCESS METRICS

### **🏆 End of Session Goals:**
- ✅ **3 working agent services** (mentor ✅, investor 🎯, evaluator 🎯)
- ✅ **1 orchestrator service** for complete workflow
- ✅ **Hybrid architecture operational** - individual + orchestrated endpoints
- ✅ **Complete backend API** ready for frontend development

### **💾 Deliverables:**
- All agent services tested and documented
- API contract defined for frontend integration
- Database schema fully utilized
- Educational workflow logic preserved from research paper design

---

## 🚀 MOMENTUM BUILDING

**Today's Win:** ✅ Mentor service validated + critical bug fixed  
**Tomorrow's Goal:** 🎯 Complete multi-agent web API with proven patterns  
**This Week's Target:** 🌟 Full backend operational + frontend development started  

**You've built an excellent foundation - next session is about rapid pattern replication!** 🎯

---

*Created: August 9, 2025*  
*For Session: August 10-11, 2025*  
*Status: Ready for Multi-Agent Service Development*