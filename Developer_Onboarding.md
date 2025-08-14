# 🎓 PITCHQUEST DEVELOPER ONBOARDING - August 14, 2025

## 📊 PROJECT STATUS: Frontend 90% Complete, Ready for Final Integration

### Quick Overview
PitchQuest is a **multi-agent educational simulation** for practicing business pitches, implementing the research from "AI AGENTS AND EDUCATION: SIMULATED PRACTICE AT SCALE" by Ethan Mollick et al.

**Current State:** Beautiful UI complete, backend functional, needs final integration and deployment.

---

## 🚀 QUICK START (For New Developers)

### Prerequisites
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- OpenAI API key

### Getting Started in 5 Minutes

```bash
# 1. Clone the repository
git clone https://github.com/[your-username]/PitchQuest
cd PitchQuest

# 2. Backend Setup
python3 -m venv pitchquest_env
source pitchquest_env/bin/activate
pip install -r requirements.txt
export OPENAI_API_KEY="your-key-here"
export DATABASE_URL="postgresql://localhost/pitchquest"
python3 create_tables.py

# 3. Start Backend
uvicorn pitchquest_api.main:app --reload
# Backend runs on http://localhost:8000

# 4. Frontend Setup (new terminal)
cd frontend
npm install
npm run dev
# Frontend runs on http://localhost:3000
```

---

## 🏗️ CURRENT ARCHITECTURE

### System Design
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Next.js UI    │────▶│  FastAPI Backend │────▶│   LangGraph     │
│  (Warm Theme)   │     │  (Orchestrator)  │     │    Agents       │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        │                        │
        │                        ▼                        │
        │                 ┌─────────────┐                │
        └────────────────▶│  PostgreSQL  │◀───────────────┘
                          │   Database   │
                          └─────────────┘
```

### Tech Stack
- **Frontend:** Next.js 15, React 18, TypeScript, Custom CSS (no Tailwind classes used)
- **Backend:** FastAPI, SQLAlchemy, PostgreSQL
- **AI:** OpenAI GPT-4, LangGraph for orchestration
- **Deployment Target:** Vercel (frontend) + Railway (backend)

---

## 🎨 DESIGN SYSTEM (Updated Aug 14)

### Color Palette - Warm & Professional
```css
--primary: #d4886a;      /* Muted Peach */
--primary-dark: #c7785a; /* Peach Dark */
--wood-light: #a08b7c;   /* Light Wood */
--wood: #8b6f5c;         /* Medium Wood */
--wood-dark: #5a4a42;    /* Dark Wood */
--background: #fbf9f7;   /* Soft Ivory */
--sand: #f0e8e2;         /* Sand */
--cream: #f5e6db;        /* Peach Cream */
```

### Typography
- **Font:** Inter (Google Fonts)
- **Weights:** 400 (regular), 500 (medium), 600 (semi-bold), 700 (bold)
- **Letter Spacing:** 0.01em for body, 0.02em for buttons

### Component Architecture
**Simplified to single component** - No component library needed:
- `PitchQuestChat.tsx` - Entire UI in one efficient component
- No Zustand (using useState)
- No shadcn/ui (custom styling)
- No custom hooks (not needed for single component)

---

## 🔧 KNOWN ISSUES & FIXES NEEDED

### 🚨 Critical Issues (Fix Tomorrow)

#### 1. Investor Selection Not Connected
**Problem:** Dropdown exists but doesn't send selection to backend
**Files to modify:**
```python
# pitchquest_api/schemas.py
class OrchestratorRequest(BaseModel):
    session_id: Optional[str] = None
    message: str
    selected_investor: Optional[str] = None  # ADD THIS

# pitchquest_api/services/orchestrator_service.py
def _handle_mentor_to_investor_transition():
    # Parse selected_investor from request
    # Use selection or assign randomly
```

#### 2. Auto-Evaluation Not Triggering
**Problem:** User must manually request evaluation
**Fix location:**
```python
# pitchquest_api/services/orchestrator_service.py
def _handle_investor_phase():
    if pitch_complete and not evaluator_complete:
        # Auto-trigger evaluation
        eval_response = evaluator_service.process_evaluation()
        return combined_response
```

#### 3. Markdown Rendering Incomplete
**Problem:** Headers and lists not parsing correctly
**Fix in frontend:**
```typescript
// Add to formatMessage function
content = content.replace(/### (.*?)$/gm, '<h3>$1</h3>');
content = content.replace(/^- (.*?)$/gm, '• $1');
```

---

## 📁 PROJECT STRUCTURE

```
PitchQuest/
├── agents/                    # Core agent logic
│   ├── mentor_agent.py        # ✅ Working
│   ├── investor_agent.py      # ✅ Working (3 personas)
│   └── evaluator_agent.py     # ✅ Working
│
├── prompts/                   # YAML prompt templates
│   ├── mentor_prompts.yaml
│   ├── investor_prompts.yaml
│   └── evaluator_prompts.yaml
│
├── pitchquest_api/           # FastAPI backend
│   ├── main.py               # App setup, CORS
│   ├── models.py             # SQLAlchemy models
│   ├── schemas.py            # Pydantic schemas
│   ├── routers/              
│   │   └── orchestrator.py   # Main /message endpoint
│   └── services/
│       └── orchestrator_service.py # ⚠️ Needs fixes
│
├── frontend/                 # Next.js app
│   ├── src/
│   │   ├── app/
│   │   │   └── page.tsx     # Main app entry
│   │   ├── components/
│   │   │   └── PitchQuestChat.tsx # ✅ Complete UI
│   │   └── lib/
│   │       └── api.ts       # API client
│   └── package.json
│
├── session_orchestrator.py   # CLI version (working)
├── requirements.txt          # Python dependencies
└── config.py                # API keys
```

---

## 🚀 DEPLOYMENT PLAN (Tomorrow)

### Frontend → Vercel
1. Push to GitHub
2. Import in Vercel
3. Set env var: `NEXT_PUBLIC_API_URL`
4. Deploy (automatic)

### Backend → Railway
1. Push to GitHub
2. New project in Railway
3. Add PostgreSQL
4. Set env vars: `OPENAI_API_KEY`, `DATABASE_URL`
5. Deploy (automatic)

### Environment Variables
```bash
# Frontend (.env.local)
NEXT_PUBLIC_API_URL=https://pitchquest-api.railway.app/api

# Backend (Railway dashboard)
OPENAI_API_KEY=sk-...
DATABASE_URL=postgresql://... (auto-generated)
```

---

## 🧪 TESTING CHECKLIST

### Complete Flow Test
- [ ] Start new session
- [ ] Complete mentor phase (3-4 messages)
- [ ] Select investor from dropdown
- [ ] Complete pitch session
- [ ] Verify auto-evaluation triggers
- [ ] Check markdown formatting
- [ ] Test "New Session" button
- [ ] Test all 3 investors

### API Endpoints
```bash
# Health check
curl http://localhost:8000/api/health

# Send message
curl -X POST http://localhost:8000/api/orchestrator/message \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello", "session_id": null}'
```

---

## 📊 DATABASE SCHEMA

### Session Table (Simplified)
```sql
CREATE TABLE sessions (
    id VARCHAR PRIMARY KEY,
    current_phase VARCHAR DEFAULT 'mentor',
    mentor_complete BOOLEAN DEFAULT FALSE,
    investor_complete BOOLEAN DEFAULT FALSE,
    evaluator_complete BOOLEAN DEFAULT FALSE,
    selected_investor VARCHAR,
    student_name VARCHAR,
    business_idea TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 🎯 KEY DECISIONS & RATIONALE

### Why No Component Libraries?
- **Single component app** doesn't need abstraction
- **Custom design** faster than learning shadcn
- **Reduced complexity** by 60%
- **Faster development** with inline styles

### Why No State Management Library?
- **useState sufficient** for conversation state
- **localStorage** handles persistence
- **No prop drilling** with single component
- **Simpler debugging**

### Why Dropdown vs Cards?
- **Always visible** - no state management
- **Familiar UX** - everyone knows dropdowns
- **Space efficient** - doesn't interrupt chat
- **Simpler code** - just a select element

---

## 🐛 COMMON ISSUES & SOLUTIONS

### Issue: "Failed to send message"
**Solution:** Check backend is running on :8000

### Issue: Markdown not rendering
**Solution:** Check formatMessage function in PitchQuestChat.tsx

### Issue: Investor always Anna Ito
**Solution:** Backend hardcoded, needs tomorrow's fix

### Issue: Must request evaluation manually
**Solution:** Backend issue, needs auto-trigger implementation

---

## 📈 PERFORMANCE METRICS

- **Frontend bundle:** ~200KB (excellent)
- **API response time:** <500ms average
- **Database queries:** 2-3 per message
- **Token usage:** ~500-1000 per conversation

---

## 🔜 FUTURE ENHANCEMENTS (Post-Launch)

### Next Week
- [ ] Docker containerization
- [ ] Comprehensive documentation
- [ ] GitHub Actions CI/CD
- [ ] Error handling improvements

### Future Features
- [ ] User accounts & authentication
- [ ] Conversation export (PDF)
- [ ] Analytics dashboard
- [ ] Multiple language support
- [ ] Custom investor personas
- [ ] Team/classroom features

---

## 💡 DEVELOPMENT TIPS

1. **Keep it simple** - Don't add complexity unless needed
2. **Test locally first** - Use the CLI orchestrator for debugging
3. **Check prompts** - Most behavior issues are in YAML files
4. **Monitor tokens** - GPT-4 costs add up quickly
5. **Use Railway** - Simpler than AWS/Azure for MVPs

---

## 📞 CONTACT & RESOURCES

- **Research Paper:** [Included in project docs]
- **API Documentation:** http://localhost:8000/docs
- **Frontend Dev Server:** http://localhost:3000

---

**Last Updated:** August 14, 2025  
**Status:** Ready for final integration and deployment  
**Estimated Time to Launch:** 3 hours

---

## 🎯 Tomorrow's Developer TODO

```markdown
[ ] Fix investor selection in backend (30 mins)
[ ] Fix auto-evaluation trigger (30 mins)
[ ] Complete markdown rendering (15 mins)
[ ] Test complete flow (30 mins)
[ ] Deploy to Vercel (20 mins)
[ ] Deploy to Railway (25 mins)
[ ] Final production test (15 mins)
[ ] 🎉 SHIP IT!
```