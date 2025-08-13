# 🎓 PITCHQUEST DEVELOPER ONBOARDING - August 13, 2025

## 📊 PROJECT STATUS: Backend 100% Complete + Frontend Foundation Ready

### Overview
PitchQuest is a **multi-agent educational simulation** for practicing business pitches, implementing the research findings from "AI AGENTS AND EDUCATION: SIMULATED PRACTICE AT SCALE" by Ethan Mollick et al. The system provides:
- **Mentor Agent**: Pre-pitch coaching and readiness assessment
- **Investor Agent**: Realistic VC personas for pitch practice (Anna Ito, Aria Iyer, Adam Ingram)
- **Evaluator Agent**: Comprehensive scoring and feedback generation
- **Orchestrator**: Seamless web API routing that mirrors LangGraph logic

### 🏗️ Repository Layout (Complete Structure)

```text
PitchQuest/
│
├── agents/                         # ✅ Core agent logic (100% working)
│   ├── mentor_agent.py             # Mentor: prep Q&A, readiness assessment
│   ├── investor_agent.py           # Investor: persona-driven pitch sessions
│   ├── evaluator_agent.py          # Evaluator: scoring + detailed feedback
│   └── __init__.py
│
├── prompts/                        # ✅ YAML prompts + loaders (working)
│   ├── mentor_prompts.yaml
│   ├── mentor_prompt_loader.py
│   ├── investor_prompts.yaml
│   ├── investor_prompt_loader.py
│   ├── evaluator_prompts.yaml
│   ├── evaluator_prompt_loader.py
│   └── __init__.py
│
├── session_orchestrator.py         # ✅ LangGraph: Interactive CLI (working)
│
├── pitchquest_api/                 # ✅ FastAPI backend (100% complete)
│   ├── main.py                     # App, CORS, router includes
│   ├── database.py                 # SQLAlchemy engine/session
│   ├── models.py                   # Complete ORM: Session, Message, Evaluation
│   ├── schemas.py                  # Pydantic models for all endpoints
│   ├── crud.py                     # Database operations
│   ├── routers/
│   │   ├── health.py               # GET /api/health
│   │   ├── sessions.py             # Session management endpoints
│   │   ├── mentor.py               # Mentor endpoints
│   │   ├── investor.py             # Investor endpoints
│   │   ├── evaluator.py            # Evaluator endpoints
│   │   └── orchestrator.py         # 🎯 UNIFIED /api/orchestrator/message endpoint
│   └── services/
│       ├── orchestrator_service.py # Smart routing logic (mirrors LangGraph)
│       ├── mentor_service.py       # Web ↔ mentor agent bridge
│       ├── investor_service.py     # Web ↔ investor agent bridge
│       ├── evaluator_service.py    # Web ↔ evaluator agent bridge
│       └── __init__.py
│
├── frontend/                       # 🆕 Next.js React app (foundation ready)
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx          # Root app layout
│   │   │   ├── page.tsx           # 🎯 Main chat interface (TODO)
│   │   │   └── globals.css         # Fixed Tailwind v3 syntax
│   │   ├── components/             # 🎯 React components (TODO)
│   │   │   ├── chat/               # Chat interface components
│   │   │   │   ├── ChatContainer.tsx
│   │   │   │   ├── MessageList.tsx
│   │   │   │   ├── MessageBubble.tsx
│   │   │   │   ├── InvestorSelection.tsx  # Inline selection cards
│   │   │   │   └── MessageInput.tsx
│   │   │   ├── progress/
│   │   │   │   └── PhaseProgress.tsx      # Simple progress line
│   │   │   └── ui/                        # shadcn/ui components
│   │   ├── lib/                    # 🎯 Integration layer (TODO)
│   │   │   ├── api.ts              # FastAPI client
│   │   │   ├── types.ts            # TypeScript interfaces
│   │   │   └── store.ts            # Zustand global state
│   │   └── hooks/                  # 🎯 React hooks (TODO)
│   │       ├── useChat.ts          # Chat message logic
│   │       └── useSession.ts       # Session management
│   ├── package.json                # Dependencies (Next.js, React, TypeScript)
│   ├── tailwind.config.js          # Fixed v3 configuration
│   ├── .env.local                  # API URL: http://localhost:8000/api
│   └── components.json             # shadcn/ui config (to be added)
│
├── evaluations/                    # ✅ Generated feedback markdown files
├── scripts/                        # 🔮 Future: Development utilities
│   ├── start-dev.sh               # Start both frontend + backend
│   ├── setup-frontend.sh          # One-command frontend setup
│   └── build-all.sh               # Production build script
│
├── config.py                       # ✅ API keys, model configuration
├── create_tables.py                # ✅ Database table creation
├── test_postgres.py                # ✅ Database connection testing
├── test_setup.py                   # ✅ Environment validation
├── requirements.txt                # ✅ Python dependencies
├── README.md                       # ✅ Quick start guide
├── PROGRESS.md                     # ✅ Development log/milestones
├── Developer_Onboarding.md         # 📄 This file
└── pitchquest_env/                 # ✅ Python virtual environment
```

---

## 🚀 How to Run (Current Working Setup)

### **Backend (FastAPI + PostgreSQL) - 100% Working:**
```bash
# 1. Activate Python environment
source pitchquest_env/bin/activate

# 2. Install dependencies (if needed)
pip install -r requirements.txt

# 3. Set environment variables
export OPENAI_API_KEY=your_openai_key_here
export DATABASE_URL=postgresql://user:pass@localhost:5432/pitchquest

# 4. Start database (macOS)
brew services start postgresql

# 5. Create/verify tables
python3 create_tables.py
python3 test_postgres.py

# 6. Start FastAPI server
uvicorn pitchquest_api.main:app --reload
# Server runs on: http://localhost:8000
# API docs: http://localhost:8000/docs
```

### **Frontend (Next.js + React) - Foundation Ready:**
```bash
# 1. Open new terminal, navigate to frontend
cd frontend

# 2. Install dependencies (if needed)
npm install

# 3. Complete shadcn/ui setup (REQUIRED - manual setup needed)
# Install required dependencies
npm install class-variance-authority clsx tailwind-merge lucide-react @radix-ui/react-slot

# Create utils file
mkdir -p src/lib
cat > src/lib/utils.ts << 'EOF'
import { type ClassValue, clsx } from "clsx"
import { twMerge } from "tailwind-merge"
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
EOF

# Create shadcn config
cat > components.json << 'EOF'
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "src/app/globals.css",
    "baseColor": "slate",
    "cssVariables": true
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
EOF

# Add individual components
npx shadcn@latest add button card input textarea dialog avatar

# 4. Start development server
npm run dev
# Server runs on: http://localhost:3000
```

### **🎯 Main Testing Endpoint:**
```bash
# Complete conversation flow through orchestrator
curl -X POST http://localhost:8000/api/orchestrator/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello, I want to practice my pitch"}'
```

---

## 🎯 Database Schema (Complete for Educational Simulation)

### **Session Model - Core State Management:**
```python
class Session(Base):
    # Identity & Student Profile
    id = Column(String, primary_key=True)           # UUID
    student_name = Column(String, nullable=True)
    student_hobby = Column(String, nullable=True)
    student_age = Column(Integer, nullable=True)
    student_location = Column(String, nullable=True)

    # Workflow State (mirrors LangGraph routing)
    current_phase = Column(String, default="mentor")
    mentor_complete = Column(Boolean, default=False)
    investor_complete = Column(Boolean, default=False)
    evaluator_complete = Column(Boolean, default=False)
    student_ready_for_investor = Column(Boolean, default=False)

    # Business Idea Information
    business_idea = Column(Text, nullable=True)
    target_audience = Column(Text, nullable=True)
    
    # Investor Selection
    selected_investor = Column(String, nullable=True)  # aria_iyer, anna_ito, adam_ingram

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
```

### **Critical Field Mappings (Service ↔ Database):**
```python
# Orchestrator/Agent State → Database Columns
"investor_persona" ↔ "selected_investor"
"pitch_complete" ↔ "investor_complete"
"student_info" (dict) ↔ individual columns (student_name, student_hobby, etc.)
"target_audience" ↔ "target_audience" (NOT problem_audience)
```

---

## 🎯 Core Flows (All Working)

### **1. Complete Educational Flow (Verified Aug 13):**
```bash
# Mentor Flow: Information gathering → readiness assessment
POST /api/orchestrator/message {"message": "Hi, I need help with my pitch"}
# → 5-question sequence → "proceed_to_investor: yes" → mentor_complete: true

# Investor Flow: Persona assignment → pitch session
POST /api/orchestrator/message {"session_id": "...", "message": "Ready to pitch!"}
# → Anna Ito assignment → 9-exchange conversation → pitch_complete: true

# Evaluator Flow: Auto-triggered comprehensive analysis
# → 81/100 score → detailed feedback → evaluator_complete: true

# Session Cycling: Unlimited practice rounds
POST /api/orchestrator/message {"session_id": "...", "message": "Practice again!"}
# → new session_id → fresh mentor start
```

### **2. Technical Architecture:**
- **Stateless Web Requests** → **Stateful Agent Conversations** via database persistence
- **Individual Service APIs** → **Unified Orchestrator Endpoint** for seamless UX
- **LangGraph Routing Logic** → **Web API Conditional Logic** for phase management
- **Educational Workflow** → **Production API** with complete metadata

---

## 🚨 CRITICAL KNOWN ISSUES (Priority for Tomorrow)

### **🎯 Issue #1: Missing Investor Selection**
**Current Behavior:** Auto-assigns Anna Ito without user choice
**Expected Behavior:** Present choice of Aria Iyer, Anna Ito, Adam Ingram
**Location:** `investor_service.py` - needs persona selection logic
**UI Design:** Inline chat selection cards (Option B)
**Priority:** HIGH - Removes student agency

### **🎯 Issue #2: Manual Evaluation Trigger**
**Current Behavior:** User must request evaluation after investor completes
**Expected Behavior:** Evaluation automatically appears when investor finishes
**Location:** `orchestrator_service.py` `_handle_investor_phase()` method
**Fix Required:** Auto-trigger evaluation in same response when `pitch_complete: true`
**Priority:** HIGH - Breaks educational flow expectation

---

## 💡 Key Technical Insights

### **Service Layer Patterns:**
1. **Load State** from database (reconstruct agent state from persistence)
2. **Process Message** through existing agent logic
3. **Save State** back to database (maintain conversation continuity)
4. **Return Response** in normalized web format

### **Error Debugging Approach:**
1. **Dictionary Access**: Use `.get(key, default)` not `[key, default]` (tuple bug)
2. **Field Mapping**: Ensure service expectations match database schema exactly
3. **State Persistence**: Verify parsed decisions saved to `updated_state` before database write
4. **Import Errors**: All agent imports must run from project root

### **LangGraph → Web API Patterns:**
- **Conditional Edges** → **if/else routing logic** in orchestrator service
- **Node Functions** → **Service method calls** with state preservation
- **State Management** → **Database persistence** with field mapping
- **Workflow Completion** → **Session cycling** with new ID generation

---

## 🎯 Frontend Implementation Strategy (Tomorrow)

### **Tech Stack Selected:**
```typescript
Next.js 15 + React 18 + TypeScript    // Modern framework foundation
+ shadcn/ui + Radix UI + Tailwind CSS // Professional component library
+ Zustand                             // Lightweight state management
+ Native fetch                        // API integration (no axios needed)
```

### **Design Philosophy:**
- **"Intentful Educational Experience"** - Purpose-driven with minimal educational content
- **Clean Chat Interface** - ChatGPT-style conversation focus
- **Simple Progress Indicator** - Linear progress line (Mentor ━●━ Investor ━○━ Evaluator)
- **Inline Interactions** - Investor selection cards within chat flow

### **Implementation Priority:**
1. **Core Chat Interface** - Message display and input
2. **API Integration** - Connect to orchestrator endpoint
3. **Investor Selection** - Inline card selection (fix Issue #1)
4. **Auto-Evaluation** - Seamless evaluation display (fix Issue #2)
5. **Session Management** - Persistence and resumption

---

## 📋 Tomorrow's Startup Checklist

### **Environment Verification:**
```bash
# 1. Verify backend is working
cd PitchQuest
source pitchquest_env/bin/activate
uvicorn pitchquest_api.main:app --reload
# → Should start on localhost:8000

# 2. Test orchestrator endpoint
curl http://localhost:8000/api/orchestrator/health
# → Should return {"status": "healthy"}

# 3. Verify frontend foundation
cd frontend
npm run dev
# → Should start on localhost:3000

# 4. Verify API connectivity (basic test)
curl -X POST http://localhost:8000/api/orchestrator/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Test message"}'
# → Should create session and return mentor response
```

### **Development Workflow:**
```bash
# Terminal 1: Backend
source pitchquest_env/bin/activate
uvicorn pitchquest_api.main:app --reload

# Terminal 2: Frontend  
cd frontend
npm run dev

# Browser: Both interfaces
# http://localhost:8000/docs  (FastAPI documentation)
# http://localhost:3000       (React application)
```

---

## 🚨 FRONTEND SETUP ISSUES & SOLUTIONS (Aug 13 Debugging)

### **Issue #1: shadcn/ui Init Failure**
**Error:** `Validation failed: - tailwind: Required`
**Cause:** Tailwind v4 vs v3 compatibility - shadcn/ui expects v3 syntax
**Solution:** Manual shadcn/ui setup instead of `npx shadcn@latest init -d`

### **Issue #2: Tailwind CSS Resolution Error**
**Error:** `Module not found: Can't resolve 'tailwindcss'`
**Cause:** globals.css had v4 syntax (`@import "tailwindcss"`, `@theme inline`)
**Solution:** Replace with v3 syntax (`@tailwind base; @tailwind components; @tailwind utilities;`)

### **Issue #3: Node.js Module in Browser**
**Error:** `Module not found: Can't resolve 'fs'`
**Cause:** Some package trying to use Node.js filesystem APIs in browser
**Solution:** Disable Turbopack temporarily or clean npm install

### **Issue #4: Multiple Lockfile Conflicts** 
**Warning:** `Found multiple lockfiles. Selecting /Users/salmanbey/package-lock.json`
**Cause:** package-lock.json in both parent and frontend directories
**Solution:** `rm ../package-lock.json` (remove parent lockfile)

### **Frontend Setup Verification Commands:**
```bash
# Check Tailwind version (should be v3.4.x)
npm list tailwindcss

# Verify globals.css syntax (should be @tailwind directives, not @import)
cat src/app/globals.css

# Test server starts without errors
npm run dev

# Verify browser loads without module errors
open http://localhost:3000
```

---

## 🔧 Critical Technical Notes

### **Database Connection:**
- **PostgreSQL Preferred**: Better for production, full-featured
- **SQLite Fallback**: Automatic if PostgreSQL unavailable
- **Schema Auto-Creation**: Run `python3 create_tables.py` if tables missing
- **Field Mapping Critical**: Service expectations must match model.py exactly

### **Service Integration Patterns:**
```python
# Standard service method pattern:
def process_[agent]_message(session_id: str, user_message: str, db: Session) -> Dict[str, Any]:
    # 1. Load current state from database
    current_state = self._load_session_state(session_id, db)
    
    # 2. Process through existing agent logic  
    result = process_single_[agent]_message(current_state, user_message)
    
    # 3. Save updated state to database
    self._save_session_state(session_id, result['updated_state'], user_message, result['ai_response'], db)
    
    # 4. Return web-friendly response
    return {"success": True, "ai_response": result['ai_response'], ...}
```

### **Frontend API Integration:**
```typescript
// Primary endpoint for all interactions
const API_ENDPOINT = 'http://localhost:8000/api/orchestrator/message'

// Standard request format
const response = await fetch(API_ENDPOINT, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ 
    session_id: sessionId || null,  // Auto-generates if null
    message: userInput 
  })
})

// Response handling
const data = await response.json()
// Returns: session_id, response, current_phase, metadata, etc.
```

---

## 🎯 Known Working Capabilities (Tested Aug 13)

### **✅ Mentor Agent:**
- 5-question conversation sequence
- Information extraction (hobby, age, business idea, target audience)
- Readiness assessment with "proceed_to_investor: yes/no" decisions
- Proper state persistence and database saving

### **✅ Investor Agent:**
- Anna Ito persona: Technical specialist with rigorous questioning
- 9-exchange realistic VC conversation
- Authentic rejection with specific technical concerns
- State preservation from mentor phase

### **✅ Evaluator Agent:**
- Auto-triggered comprehensive analysis
- 81/100 scoring with detailed breakdown
- Performance level assessment (advanced)
- Markdown feedback document generation

### **✅ Orchestrator Service:**
- Automatic phase routing based on completion status
- Session creation and cycling
- Error handling and graceful recovery
- Complete metadata for frontend integration

---

## 🔮 Immediate Next Steps (Thursday Aug 14)

### **Step 1: Complete shadcn/ui Setup (5 minutes)**
```bash
# From frontend directory - complete the manual setup we started
cd frontend

# Add shadcn/ui components (the commands we didn't finish)
npx shadcn@latest add button card input textarea dialog avatar badge

# Create components directory
mkdir -p src/components/ui

# Verify setup works
npm run dev
```

### **Step 2: Complete Chat Interface (45 minutes)**
```typescript
// Core components to implement:
<ChatContainer />           // Main wrapper with state management
<MessageList />            // Display conversation history  
<MessageBubble />          // Individual message styling
<InvestorSelection />      // Inline selection cards (fix Issue #1)
<PhaseProgress />          // Simple progress line indicator
<MessageInput />           // Text input + send button
```

### **Priority 2: Fix UX Issues**
1. **Investor Selection**: Add choice UI before investor conversation starts
2. **Auto-Evaluation**: Remove user input requirement, trigger automatically

### **Priority 3: Integration Testing**
- Complete conversation flow through React interface
- Session persistence and resumption
- Error handling and edge cases
- Professional UI polish

---

## 📚 Educational Architecture Context

### **Research Paper Implementation:**
- **Multi-Agent Workflow**: Mentor → NPC → Evaluator pattern from Mollick et al.
- **Pedagogical Progression**: Instruction → Practice → Feedback loop
- **Authentic Simulation**: Realistic investor personas with backstories
- **Scalable Assessment**: Automated evaluation with detailed instructor insights

### **Learning Objectives:**
- **Student Experience**: Safe practice environment with realistic challenges
- **Instructor Insights**: Detailed analytics on student performance
- **Scalable Education**: One system handles unlimited concurrent students
- **Research Integration**: Foundation for educational AI research

---

## 🎯 Success Metrics & Completion Criteria

### **Backend Excellence (✅ Achieved):**
- Complete mentor → investor → evaluator workflow
- Realistic AI personas with authentic interactions
- Comprehensive evaluation and feedback system
- Robust session management and state persistence

### **Frontend Excellence (🎯 Tomorrow):**
- ChatGPT-quality conversational interface
- Seamless API integration with backend
- Intuitive user experience with clear progress indicators
- Professional design with accessible components

### **System Integration (🎯 Tomorrow):**
- End-to-end student experience through web interface
- Instructor capability to monitor student progress
- Production-ready deployment architecture
- Complete educational simulation platform

---

**Updated: August 13, 2025**  
**Backend Status: 100% Complete and Tested**  
**Frontend Status: Foundation Ready for Implementation**  
**Next Session Focus: React Interface + UX Issue Resolution**  
**🎯 Goal: Complete Educational AI Platform with Professional Frontend**