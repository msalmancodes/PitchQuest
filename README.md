# 🚀 PitchQuest

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-15.4-black.svg)](https://nextjs.org/)
[![AWS Lambda](https://img.shields.io/badge/AWS-Lambda-orange.svg)](https://aws.amazon.com/lambda/)
[![GPT-5](https://img.shields.io/badge/OpenAI-GPT--5--mini-purple.svg)](https://openai.com/)
[![Vercel](https://img.shields.io/badge/Vercel-Deployed-black.svg)](https://vercel.com/)

**AI-powered pitch training platform with multi-agent mentoring, practice, and feedback system.**

## 📖 About

PitchQuest is an educational simulation platform that helps students practice business pitches through conversational AI agents. Based on research from ["AI Agents and Education: Simulated Practice at Scale"](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4802463) by Mollick et al., it provides personalized mentoring, realistic investor interactions, and comprehensive feedback. The system uses three specialized AI agents orchestrated through LangGraph to create a complete learning experience.

## ✨ Features

- 🤖 **Three Specialized AI Agents** - Mentor, Investor, and Evaluator agents for complete training
- 💬 **Interactive Chat Interface** - Clean, responsive web UI for natural conversations  
- 📊 **Session Persistence** - Save progress and continue across sessions
- 🔄 **Structured Learning Flow** - Guided journey from preparation to practice to feedback
- ☁️ **Production Deployed** - Serverless backend on AWS Lambda, frontend on Vercel
- 🎓 **Research-Based Design** - Pedagogically grounded in educational best practices

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Next.js 15.4, React, TypeScript | Modern web interface |
| **Backend** | FastAPI, AWS Lambda, API Gateway | Serverless API |
| **Database** | Supabase (PostgreSQL) | Session & message storage |
| **AI/ML** | OpenAI GPT-5-mini, LangGraph | Agent orchestration |
| **Deployment** | Vercel (Frontend), AWS (Backend) | Cloud hosting |

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key
- Supabase account (or local PostgreSQL)

### Local Development

```bash
# 1. Clone repository
git clone https://github.com/msalmancodes/PitchQuest.git
cd PitchQuest

# 2. Backend setup
python -m venv pitchquest_env
source pitchquest_env/bin/activate  # Windows: pitchquest_env\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # Add your API keys
uvicorn pitchquest_api.main:app --reload

# 3. Frontend setup (new terminal)
cd frontend
npm install
npm run dev

# 4. Open http://localhost:3000
```

## 📁 Project Structure

```
PitchQuest/
├── 📄 README.md                    # You are here
├── 📄 Developer_Onboarding.md      # Complete setup guide
├── 📄 PROGRESS.md                  # Development timeline
├── 📄 requirements.txt             # Python dependencies
├── 📄 config.py                    # Configuration settings
├── 📂 pitchquest_api/             
│   ├── main.py                    # FastAPI application
│   ├── lambda_handler.py          # AWS Lambda handler
│   └── routers/                   # API endpoints
├── 📂 agents/                     
│   ├── mentor_agent.py            # Mentoring logic
│   ├── investor_agent.py          # Pitch session logic
│   └── evaluator_agent.py         # Feedback generation
├── 📂 prompts/                    
│   └── *.yaml                     # Agent prompt templates
├── 📂 frontend/                   
│   ├── src/                       # React components
│   └── package.json               # Node dependencies
└── 📂 deployment/                 
    └── build.sh                   # Lambda build script
```

### 📚 Key Documentation

- **[Developer Onboarding](./Developer_Onboarding.md)** - Detailed setup, deployment, and API documentation
- **[Progress & Roadmap](./PROGRESS.md)** - Development history and future plans
- **[API Documentation](./pitchquest_api)** - Endpoint specifications
- **[Agent Architecture](./agents/README.md)** - Multi-agent system design

## 🤝 Contributors

### Development Team
- **[Muhammad Salman](https://github.com/msalmancodes)** - Project Lead & Developer

### AI Assistants
- **[Claude](https://claude.ai)** (Anthropic) - Architecture design, code review, documentation
- **[ChatGPT](https://chat.openai.com)** (OpenAI) - Initial development, debugging support

### Research Foundation
- **[Mollick et al.](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4802463)** - "AI Agents and Education" research paper

## 🔗 Live Demo
- **Web Page**: (https://pitch-quest-sj48.vercel.app/)
- **API Endpoint**: `https://am0h8n8b8i.execute-api.us-east-1.amazonaws.com/default/api/health`
- **Frontend**: [Contact for access]

## 📝 License

MIT License - see [LICENSE](./LICENSE) file for details

## 🙏 Acknowledgments

- **Research**: Based on "AI Agents and Education: Simulated Practice at Scale" by Ethan & Lilach Mollick et al.
- **Technologies**: OpenAI, AWS, Vercel, Supabase, FastAPI, Next.js, LangGraph
- **Support**: Wharton School's Generative AI Lab for the foundational research

---

*Building the future of education through AI-powered practice* 🎓