# AgentAcademy 🎓

**Educational Multi-Agent Simulation System for Business Pitch Practice**

> An AI-powered educational platform inspired by the research paper "AI AGENTS AND EDUCATION: SIMULATED PRACTICE AT SCALE" by Ethan Mollick et al., designed to help students practice business pitches through realistic AI-driven simulations.

## 🎯 Project Overview

AgentAcademy provides students with a safe, low-stakes environment to practice entrepreneurial pitching skills through AI agents that serve as mentors, investors, and evaluators. Students engage in guided conversations that simulate real-world pitch scenarios, receiving personalized feedback to improve their presentation and business communication skills.

### 🏗️ Multi-Agent Architecture

- **Mentor Agent**: Pre-pitch tutoring and strategic guidance
- **Investor Agent**: Realistic VC pitch session simulation  
- **Evaluator Agent**: Post-pitch analysis and personalized feedback
- **Session Manager**: Workflow orchestration and progress tracking

## 🚀 Current Status

**Phase 1: Foundation (Week 1)** - 🟡 In Progress

### ✅ Completed
- Basic mentor agent implementation with LangGraph
- 4-question conversation flow (hobby/age/location → business idea → problem/audience → handoff)
- LangGraph streaming for interactive conversations
- State management and conversation flow control
- Graph visualization and debugging capabilities

### 🔄 In Progress  
- Intelligent mentor agent with LLM-powered conversations
- System prompts and conversational AI integration
- Enhanced user experience and natural dialog

### 📋 Upcoming
- Investor agent implementation
- Evaluator agent for feedback generation
- Multi-agent workflow integration

## 🛠️ Technical Stack

- **Framework**: LangGraph (Multi-agent orchestration)
- **LLM**: OpenAI GPT-4
- **Backend**: Python 3.10+
- **State Management**: TypedDict with LangGraph State
- **Development**: Virtual environment with pip

## 📦 Installation & Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/agent-academy.git
cd agent-academy

# Create virtual environment
python -m venv agent_env
source agent_env/bin/activate  # On Mac/Linux

# Install dependencies
pip install langgraph langchain-openai python-dotenv
```

## 🏃‍♂️ Quick Start

```python
# Create config.py with your API key
OPENAI_API_KEY = "your-openai-api-key"
MODEL_NAME = "gpt-4"

# Run the mentor agent
python mentor_agent.py
```

## 📚 Learning Objectives

This project teaches:
- **LangGraph Framework**: Multi-agent system development
- **State Management**: Complex conversation state handling
- **AI Agent Design**: Educational simulation principles
- **Production Development**: Software engineering best practices

## 🎓 Educational Foundation

Based on proven pedagogical research from Wharton's Generative AI Lab, implementing the learning loop:
1. **Direct Instruction** - Foundational knowledge
2. **Guided Practice** - AI mentor conversations  
3. **Active Practice** - Realistic pitch simulations
4. **Feedback** - Personalized improvement guidance
5. **Reflection** - Knowledge consolidation

## 📈 Project Phases

- **Phase 1**: Foundation (Mentor Agent) - Week 1
- **Phase 2**: Multi-Agent Core (All Agents) - Week 2  
- **Phase 3**: Web Interface (FastAPI + Streamlit) - Week 3
- **Phase 4**: Production Polish (Deployment Ready) - Week 4

## 🤝 Contributing

This is a learning project focused on mastering LangGraph and multi-agent systems. See [PROGRESS.md](PROGRESS.md) for detailed development notes and session tracking.

## 📄 License

MIT License - See LICENSE file for details

## 🔗 References

- [AI Agents and Education Research Paper](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4475995)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Educational AI Best Practices](https://www.anthropic.com/research)

---

**Current Version**: v0.1.0-alpha  
**Last Updated**: Julu 2025  
**Development Status**: Active Learning Project