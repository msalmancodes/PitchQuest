# 🚀 Developer Onboarding Guide - August 12, 2025
## Building the Orchestrator Service: The Final Piece

---

## 👋 Welcome Back!

Whether you're returning after a break or jumping in fresh, this guide will get you up to speed quickly. Today, we're building the **orchestrator service** - the crown jewel that ties everything together into one elegant API.

### **What You're Building Today:**
A single endpoint (`/api/orchestrator/message`) that automatically routes messages to the correct agent (mentor, investor, or evaluator) based on session state. Think of it as an intelligent traffic controller for your multi-agent system.

---

## 🏗️ Current System Architecture

### **What's Already Built (and Working!):**

```
PitchQuest/
├── agents/                      ✅ Core agent logic (DO NOT MODIFY)
│   ├── mentor_agent.py         ✅ Working - handles mentoring
│   ├── investor_agent.py       ✅ Working - handles pitching
│   └── evaluator_agent.py      ✅ Working - generates feedback
│
├── pitchquest_api/             
│   ├── services/               ✅ Web service layer
│   │   ├── mentor_service.py   ✅ Complete - your template!
│   │   ├── investor_service.py ✅ Complete
│   │   ├── evaluator_service.py ✅ Complete
│   │   └── orchestrator_service.py 🎯 TODAY'S TASK
│   │
│   ├── routers/                ✅ API endpoints
│   │   ├── mentor.py           ✅ Working
│   │   ├── investor.py         ✅ Working
│   │   ├── evaluator.py        ✅ Working
│   │   └── orchestrator.py     🎯 TODAY'S TASK
│   │
│   ├── database.py             ✅ PostgreSQL connection
│   ├── models.py               ✅ Database schema (sessions, messages, evaluations)
│   ├── crud.py                 ✅ Database operations
│   ├── schemas.py              ✅ Request/response models
│   └── main.py                 ✅ FastAPI app (needs orchestrator registration)
│
├── session_orchestrator.py      📚 REFERENCE - Shows local LangGraph flow
└── evaluations/                 📁 Where feedback documents are saved
```

---

## 🎯 Today's Mission: The Orchestrator

### **Why We Need It:**
Currently, the frontend would need to:
1. Know which agent to call
2. Track session state
3. Handle phase transitions
4. Manage special cases

**The orchestrator eliminates all this complexity!**

### **How It Works:**

```python
# Frontend just does this:
POST /api/orchestrator/message
{
    "session_id": "abc-123",  # Optional - auto-generated if not provided
    "message": "Hi, I need help with my pitch"
}

# Orchestrator automatically:
1. Checks session state (or creates new)
2. Determines current phase (mentor/investor/evaluator)
3. Routes to correct service
4. Returns unified response
```

---

## 📋 Step-by-Step Implementation Guide

### **📍 Step 1: Understand the Routing Logic**

The orchestrator needs to determine which agent to use:

```python
def determine_phase(session):
    if not session:
        return "mentor"  # New sessions start with mentor
    
    if not session.mentor_complete:
        return "mentor"  # Continue mentoring
    
    if not session.investor_complete:
        return "investor"  # Move to investor
    
    if not session.evaluator_complete:
        return "evaluator"  # Time for evaluation
    
    return "complete"  # All done!
```

### **📍 Step 2: Create the Orchestrator Service**

**File:** `pitchquest_api/services/orchestrator_service.py`

**Key Patterns to Follow:**
1. **Import all three services** (mentor, investor, evaluator)
2. **Load session state** using crud operations
3. **Route based on phase** 
4. **Return unified response**

**Template Structure:**
```python
class OrchestratorService:
    def process_message(self, session_id: Optional[str], message: str, db: DatabaseSession):
        # 1. Generate session_id if not provided
        # 2. Load session from database
        # 3. Determine current phase
        # 4. Route to appropriate service
        # 5. Return unified response
```

### **📍 Step 3: Create the Router**

**File:** `pitchquest_api/routers/orchestrator.py`

**Simple and Clean:**
```python
@router.post("/message")
async def process_message(request: OrchestratorMessageRequest, db: Session = Depends(get_db)):
    result = orchestrator_service.process_message(
        session_id=request.session_id,
        message=request.message,
        db=db
    )
    return OrchestratorMessageResponse(**result)
```

### **📍 Step 4: Register in main.py**

```python
from .routers import orchestrator  # Add this
app.include_router(orchestrator.router, prefix="/api/orchestrator", tags=["orchestrator"])
```

---

## 🔍 Critical Files to Reference

### **1. session_orchestrator.py** 
**Why:** Shows the complete LangGraph flow and routing logic
**Look for:** 
- `should_continue_mentor()` - routing logic
- Phase transition conditions
- State structure

### **2. services/mentor_service.py**
**Why:** Your best template for service patterns
**Look for:**
- `process_mentor_message()` - main processing pattern
- State loading/saving patterns
- Response structure

### **3. schemas.py**
**Why:** Has the request/response models you'll need
**Look for:**
- `OrchestratorMessageRequest`
- `OrchestratorMessageResponse`
- Field definitions

### **4. crud.py**
**Why:** Database operations you'll use
**Key functions:**
- `get_session()` - load session
- `create_session()` - new session
- `update_session()` - update phase

---

## ⚠️ Special Cases to Handle

### **1. Investor Persona Selection**
```python
if current_phase == "investor" and message.lower() in ["start", "begin"]:
    # Trigger persona selection interface
    message = "start"
```

### **2. Auto-Evaluation**
```python
if current_phase == "evaluator":
    # Don't wait for user message, auto-trigger evaluation
    result = evaluator_service.evaluate_pitch(session_id, db)
```

### **3. New Session Creation**
```python
if not session_id:
    session_id = str(uuid.uuid4())
    # Session will be created by mentor service on first message
```

---

## 🧪 Testing Your Implementation

### **Test Sequence:**

1. **New Session Test**
```bash
POST /api/orchestrator/message
{
    "message": "Hi, I need help"
}
# Should: Create session, route to mentor
```

2. **Complete Flow Test**
```bash
# Message 1-4: Mentor phase
# Message 5: Should auto-switch to investor
# Message 6: Should show persona selection
# Message 7-12: Investor conversation
# Message 13: Should auto-evaluate
```

3. **Edge Cases**
- Missing session_id (should auto-generate)
- Complete session (should return "complete" message)
- Invalid session_id (should handle gracefully)

---

## 💡 Pro Tips

### **1. Use Logging Liberally**
```python
logger.info(f"Session {session_id} in phase: {current_phase}")
```

### **2. Check the Database**
```sql
SELECT * FROM sessions WHERE id = 'your-session-id';
SELECT COUNT(*) FROM messages WHERE session_id = 'your-session-id';
```

### **3. Return Consistent Responses**
Always include: session_id, response, current_phase, phase_complete, metadata

### **4. Test via /docs**
FastAPI's interactive docs at `http://localhost:8000/docs` are your best friend!

---

## 🎯 Success Criteria

You'll know you're done when:

✅ **Single endpoint** handles entire conversation flow
✅ **Automatic routing** to correct agent based on state
✅ **Phase transitions** happen seamlessly
✅ **Special cases** handled (persona selection, auto-evaluation)
✅ **Complete session** works from start to finish through one endpoint

---

## 🚑 Troubleshooting Guide

### **Import Errors?**
- Check the import patterns in mentor_service.py
- Use relative imports for routers: `from ..services.orchestrator_service import orchestrator_service`

### **Phase Not Switching?**
- Check database: Is `mentor_complete` being set to `true`?
- Verify the routing logic matches the database field names

### **Evaluation Not Triggering?**
- The evaluator expects investor messages with `agent_type='investor'`
- Check messages table to ensure they're being saved correctly

### **Session Not Found?**
- Ensure session is created on first message
- Check if session_id is being passed correctly

---

## 📚 Quick Command Reference

```bash
# Start the server
cd PitchQuest
source pitchquest_env/bin/activate
uvicorn pitchquest_api.main:app --reload

# Test the orchestrator
curl -X POST "http://localhost:8000/api/orchestrator/message" \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello"}'

# Check database
python
>>> from pitchquest_api.database import SessionLocal
>>> from pitchquest_api import crud
>>> db = SessionLocal()
>>> session = crud.get_session(db, "your-session-id")
>>> print(session.current_phase)
```

---

## 🎉 You've Got This!

Remember:
- The hard work is already done (all agents are working)
- You're just building a smart traffic controller
- The patterns are all there in the existing services
- Take it step by step

### **Expected Time:**
- 30 minutes for implementation
- 10 minutes for testing
- 5 minutes for celebration! 🎉

---

## 📞 Next Steps After Orchestrator

Once the orchestrator is working:
1. **Quick Integration Test:** Run a complete session through the single endpoint
2. **Consider Frontend:** Simple Streamlit app to visualize the flow
3. **Polish:** Add any missing error handling
4. **Document:** Update API documentation

---

**Good luck! You're one service away from a complete multi-agent educational system!** 🚀

*Remember: The orchestrator is just a router. It doesn't do any AI work itself - it just knows where to send messages. Keep it simple!*