# PitchQuest Developer Onboarding Guide

Welcome to the PitchQuest repository! This guide is designed to help **any developer or LLM** quickly understand the repo’s structure, how the system works, and how to continue development without guesswork.

---

## 1. Project Overview
PitchQuest is a **multi-agent educational simulation** for practicing venture capital pitches, based on the Wharton "AI Agents and Education" research.  
The architecture follows the **Mentor → Investor → Evaluator** learning loop, with optional instructor-facing **Progress** and **Class Insights** agents.

---

## 2. Directory Structure & Purpose
```
PitchQuest/
│
├── agents/                     # Core AI agent logic
│   ├── mentor_agent.py         # Mentor Agent (pre-pitch tutoring)
│   ├── investor_agent.py       # Investor personas & pitch simulation
│   ├── evaluator_agent.py      # Post-pitch feedback generation
│   ├── progress_agent.py       # Individual student summaries
│   ├── class_insights_agent.py # Aggregated instructor feedback
│
├── prompts/                    # Prompt templates from research paper
│   ├── mentor_prompt.txt
│   ├── investor_prompts.json
│   ├── evaluator_prompt.txt
│   ├── progress_prompt.txt
│   ├── class_insights_prompt.txt
│
├── pitchquest_api/              # FastAPI backend
│   ├── main.py                  # API routes
│   ├── db.py                    # Postgres connection
│   ├── models.py                # ORM models for sessions, pitches
│   ├── crud.py                  # Database operations
│
├── session_orchestrator.py     # LangGraph multi-agent orchestration
├── config.py                   # API keys, model names
├── create_tables.py            # Initialize database schema
├── requirements.txt
├── README.md                   # Quick start & project plan
├── PROGRESS.md                 # Dev log
├── simple_interactive_workflow.mmd  # Mermaid diagram
├── simple_interactive_workflow.png  # Visualization of flow
├── test_setup.py               # Env & API connectivity check
├── test_postgres.py            # DB connection check
└── LICENSE
```

---

## 3. Key Components

### Agents (Core of Simulation)
- **Mentor Agent**  
  - Guides student before pitching, connects concepts to personal context.
  - Won’t write the pitch; gives hints, asks open-ended questions.
  - Ends after 3 exchanges, transitions to Investor.
  
- **Investor Agent**  
  - Multiple personas (Aria, Anna, Adam) with different styles.
  - Probes for missing pitch elements.
  - Uses hidden internal guidelines for conversation planning, grading, and ending.

- **Evaluator Agent**  
  - Reads transcript of pitch session.
  - Gives specific, actionable feedback and a performance score.

- **Progress Agent** *(Instructor-facing)*  
  - Summarizes strengths and weaknesses per student.

- **Class Insights Agent** *(Instructor-facing)*  
  - Aggregates Progress Agent outputs into class-level trends.

---

## 4. Execution Flow
1. **Survey / Intro Video** (outside current code scope)
2. **Mentor Agent Session** → Guided prep.
3. **Investor Agent Session** → Active pitch practice.
4. **Evaluator Agent Session** → Feedback.
5. *(Optional)* Instructor agents run on transcripts.

---

## 5. Database & Backend
- **Postgres** stores:
  - `students` (profile, survey answers)
  - `sessions` (phase progress)
  - `transcripts` (per agent)
  - `feedback` (agent outputs)
- **FastAPI** provides:
  - Session start/end endpoints
  - Agent interaction routes
  - Data retrieval for UI

---

## 6. Prompt Management
Prompts in `/prompts` are **direct from the paper**—no guessing needed.  
They follow Appendix B from the PitchQuest research.

---

## 7. Current Development Status
From commits & PROGRESS.md:
- ✅ Mentor Agent functional.
- ✅ Initial multi-agent orchestration working.
- ✅ FastAPI backend + Postgres integration scaffolded.
- 🔄 Investor & Evaluator agents partially implemented.
- 🔄 API endpoint wiring for all agents in progress.
- ⏳ Streamlit frontend not yet started.

---

## 8. Next Steps for Development
**Immediate next steps:**
1. Complete **Investor Agent** logic & persona switching.
2. Implement **Evaluator Agent** transcript processing.
3. Finish orchestration hand-offs in `session_orchestrator.py`.
4. Finalize API routes for each agent in `pitchquest_api/main.py`.
5. Integrate database writes for transcripts & feedback.
6. Begin **Streamlit frontend** for interactive sessions.

**Testing focus:**
- Ensure agent hand-offs preserve context.
- Verify Postgres persistence matches session flow.
- Confirm prompt outputs align with pedagogical goals.

---

## 9. Quick Start for a New Developer
```bash
git clone https://github.com/msalmancodes/PitchQuest.git
cd PitchQuest
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# Set your OpenAI API key in config.py
python create_tables.py  # init database
uvicorn pitchquest_api.main:app --reload  # start backend
```
Then:
- Use `session_orchestrator.py` to test end-to-end agent runs.
- Modify prompts in `/prompts` to adjust teaching style.
- View `simple_interactive_workflow.png` for LangGraph visualization.

---

**Source:** Based on repo code structure and Wharton "AI Agents and Education: Simulated Practice at Scale" research.
