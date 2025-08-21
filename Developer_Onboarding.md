# 🔧 PITCHQUEST DEVELOPER DOCUMENTATION

## 🎯 Project Overview
PitchQuest is a multi-agent educational platform for pitch practice, built with:
- **Backend**: FastAPI on AWS Lambda with API Gateway
- **Frontend**: Next.js deployed on Vercel  
- **Database**: Supabase (PostgreSQL)
- **AI**: OpenAI GPT-5-mini
- **Agents**: LangGraph-based mentor, investor, and evaluator agents

## 📁 Project Structure
```
PitchQuest/
├── pitchquest_api/          # FastAPI backend
│   ├── main.py             # App initialization with CORS
│   ├── lambda_handler.py   # AWS Lambda handler (Mangum)
│   ├── routers/            # API endpoints
│   │   ├── orchestrator.py # Main conversation handler
│   │   ├── mentor.py       # Mentor agent endpoints
│   │   ├── investor.py     # Investor agent endpoints
│   │   └── evaluator.py    # Evaluator agent endpoints
│   └── services/           # Business logic
├── agents/                  # LangGraph agents
│   ├── mentor_agent.py     # Mentor conversation logic
│   ├── investor_agent.py   # Investor conversation logic
│   └── evaluator_agent.py  # Evaluation logic
├── frontend/               # Next.js frontend
│   ├── src/
│   │   ├── app/           # Next.js app directory
│   │   ├── components/    # React components
│   │   └── lib/           # Utilities (api.ts)
│   └── next.config.js     # Next.js configuration
├── deployment/             # Deployment artifacts
│   ├── package/           # Lambda dependencies
│   └── pitchquest_lambda.zip
├── prompts/               # YAML prompt templates
├── config.py              # Configuration (API keys, model)
└── requirements.txt       # Python dependencies
```

## 🚀 Production Architecture

### Backend (AWS Lambda + API Gateway)
- **Lambda Function**: `pitchquest-backend`
- **Runtime**: Python 3.11
- **Memory**: 1024 MB
- **Timeout**: 30 seconds
- **Handler**: `pitchquest_api.lambda_handler.handler`
- **Endpoint**: `https://am0h8n8b8i.execute-api.us-east-1.amazonaws.com/default/`

### Frontend (Vercel)
- **Framework**: Next.js 15.4.6
- **Deployment**: Vercel (auto-deploy from GitHub)
- **Repository**: `github.com/msalmancodes/PitchQuest`
- **Root Directory**: `frontend/`

### Database (Supabase)
- **Provider**: Supabase (PostgreSQL)
- **Connection**: Pooled connection for reliability
- **Tables**: 
  - `sessions`: Student info and phase tracking
  - `messages`: Conversation history
  - `evaluations`: Pitch feedback and scores

### AI Configuration
- **Model**: GPT-5-mini
- **Provider**: OpenAI API
- **Context**: Managed through LangGraph state

## 🔨 Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- AWS CLI configured
- Git

### Local Backend Setup
```bash
# Clone repository
git clone https://github.com/msalmancodes/PitchQuest.git
cd PitchQuest

# Create virtual environment
python -m venv pitchquest_env
source pitchquest_env/bin/activate  # Mac/Linux
# or
pitchquest_env\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="your-supabase-url"
export OPENAI_API_KEY="your-api-key"
export MODEL_NAME="gpt-5-mini"
export CORS_ORIGINS="*"

# Run locally
uvicorn pitchquest_api.main:app --reload --port 8000
```

### Local Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api" > .env.local

# Run development server
npm run dev
```

## 📦 Deployment Commands

### Deploy Backend to Lambda
```bash
# Build Lambda package (Linux compatible)
cd deployment
docker run --rm \
  -v "$PWD":/var/task \
  -w /var/task \
  public.ecr.aws/lambda/python:3.11 \
  bash -c "pip install -r ../requirements.txt -t package/"

# Copy application code
cp -r ../pitchquest_api package/
cp -r ../agents package/
cp -r ../prompts package/
cp ../config.py package/

# Create deployment package
cd package && zip -r ../pitchquest_lambda.zip . -x "*.pyc" "__pycache__/*" && cd ..

# Deploy to Lambda
aws lambda update-function-code \
  --region us-east-1 \
  --function-name pitchquest-backend \
  --zip-file fileb://pitchquest_lambda.zip

# Update environment variables
aws lambda update-function-configuration \
  --function-name pitchquest-backend \
  --region us-east-1 \
  --environment Variables='{
    "DATABASE_URL":"your-database-url",
    "OPENAI_API_KEY":"your-api-key",
    "MODEL_NAME":"gpt-5-mini",
    "CORS_ORIGINS":"*"
  }'
```

### Deploy Frontend to Vercel
```bash
# Commit changes
cd frontend
git add .
git commit -m "Update frontend"
git push origin main

# Vercel auto-deploys from GitHub
# Or manual deploy:
vercel --prod
```

## 🔑 Environment Variables

### Backend (Lambda)
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for GPT-5-mini
- `MODEL_NAME`: AI model to use (default: gpt-5-mini)
- `CORS_ORIGINS`: Allowed origins (use * for all)

### Frontend (Vercel)
- `NEXT_PUBLIC_API_BASE_URL`: Backend API endpoint

## 📝 API Endpoints

### Health Check
```bash
GET /api/health
# Returns: {"status": "healthy", "message": "...", "database": "connected"}
```

### Orchestrator (Main Endpoint)
```bash
POST /api/orchestrator/message
{
  "message": "user message",
  "session_id": "unique-session-id",
  "selected_investor": "optional-investor-name"
}
```

### Session Management
```bash
# Create session
POST /api/sessions

# Get session
GET /api/sessions/{session_id}

# Update session
PUT /api/sessions/{session_id}
```

## 🧪 Testing

### Test Backend Health
```bash
curl https://am0h8n8b8i.execute-api.us-east-1.amazonaws.com/default/api/health
```

### Test Orchestrator
```bash
curl -X POST https://am0h8n8b8i.execute-api.us-east-1.amazonaws.com/default/api/orchestrator/message \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello","session_id":"test-001"}'
```

### Check Lambda Configuration
```bash
aws lambda get-function-configuration \
  --function-name pitchquest-backend \
  --region us-east-1 \
  --query 'Environment.Variables'
```

## 🐛 Common Issues & Solutions

### 1. Lambda Import Errors
**Issue**: Module import errors after deployment
**Solution**: Use Docker to build package with Linux binaries
```bash
docker run --rm -v "$PWD":/var/task -w /var/task \
  public.ecr.aws/lambda/python:3.11 \
  bash -c "pip install -r requirements.txt -t package/"
```

### 2. CORS Errors
**Issue**: Frontend can't connect to backend
**Solution**: Ensure CORS_ORIGINS environment variable is set to "*" or includes your frontend URL

### 3. Database Connection Issues
**Issue**: Can't connect to Supabase
**Solution**: Use pooled connection URL (ends with `.pooler.supabase.com`)

### 4. TypeScript Build Errors
**Issue**: Vercel build fails on TypeScript errors
**Solution**: Add to `next.config.js`:
```javascript
module.exports = {
  eslint: { ignoreDuringBuilds: true },
  typescript: { ignoreBuildErrors: true }
}
```

## 🚧 Production Checklist

### Security
- [ ] Rotate API keys regularly
- [ ] Set specific CORS origins (not *)
- [ ] Implement rate limiting
- [ ] Add authentication/authorization
- [ ] Enable CloudWatch monitoring
- [ ] Set up error alerting

### Performance
- [ ] Implement caching for OpenAI responses
- [ ] Optimize Lambda cold starts
- [ ] Add database connection pooling
- [ ] Enable CDN for frontend assets
- [ ] Implement request batching

### Features to Add
- [ ] More investor personas
- [ ] Session timeout handling
- [ ] Export functionality for feedback
- [ ] Admin dashboard
- [ ] Analytics tracking
- [ ] Multi-language support

## 📊 Monitoring

### CloudWatch Logs
```bash
aws logs tail /aws/lambda/pitchquest-backend --follow
```

### Lambda Metrics
- Monitor in AWS Console → Lambda → pitchquest-backend → Monitoring
- Key metrics: Invocations, Duration, Errors, Throttles

### Database Monitoring
- Supabase Dashboard → Database → Query Performance
- Monitor connection pool usage

## 🔄 Continuous Deployment

### Backend CI/CD (GitHub Actions)
```yaml
name: Deploy Backend
on:
  push:
    branches: [main]
    paths:
      - 'pitchquest_api/**'
      - 'agents/**'
      - 'prompts/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Lambda
        run: |
          # Build and deploy script here
```

### Frontend (Vercel Auto-Deploy)
- Automatically deploys on push to main branch
- Preview deployments for pull requests
- Rollback capability in Vercel dashboard

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [AWS Lambda Python](https://docs.aws.amazon.com/lambda/latest/dg/lambda-python.html)
- [Next.js Documentation](https://nextjs.org/docs)
- [Vercel Deployment](https://vercel.com/docs)
- [Supabase Documentation](https://supabase.com/docs)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)

---

**Last Updated**: August 20, 2025
**Version**: 2.0
**Status**: Production Ready
**Maintainer**: Muhammad Salman