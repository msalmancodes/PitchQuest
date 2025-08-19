# 🔧 PITCHQUEST DEVELOPER DOCUMENTATION

## 📁 Project Structure
```
PitchQuest/
├── pitchquest_api/          # FastAPI backend
│   ├── main.py             # App initialization
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
├── frontend/               # React frontend
├── deployment/             # Deployment artifacts
│   ├── package/           # Lambda dependencies
│   └── pitchquest_lambda.zip
└── requirements.txt        # Python dependencies
```

## 🚀 Deployment Architecture

### Backend (AWS Lambda + API Gateway)
- **Lambda Function**: pitchquest-backend
- **Runtime**: Python 3.11
- **Memory**: 1024 MB
- **Timeout**: 30 seconds
- **Package Size**: 32 MB
- **Handler**: pitchquest_api.lambda_handler.handler

### Database (Supabase)
- **Provider**: Supabase (PostgreSQL)
- **Connection**: Pooled connection for reliability
- **Tables**: sessions, messages, evaluations

### API Gateway
- **Type**: REST API
- **Routing**: {proxy+} catch-all pattern
- **Endpoint**: https://am0h8n8b8i.execute-api.us-east-1.amazonaws.com/default/

## 🔨 Build & Deployment Commands

### Build Lambda Package (Linux Compatible)
```bash
docker run --rm \
  -v "$PWD":/var/task \
  -w /var/task \
  public.ecr.aws/lambda/python:3.11 \
  bash -c "pip install --upgrade pip && \
           pip install -r requirements.txt -t deployment/package/ && \
           find deployment/package -type f -name '*.pyc' -delete && \
           find deployment/package -type d -name '__pycache__' -delete"

cd deployment
cp -r ../pitchquest_api package/
cp -r ../agents package/
cp -r ../prompts package/
cd package && zip -r ../pitchquest_lambda.zip . -x "*.pyc" "__pycache__/*" && cd ..
```

### Deploy to Lambda
```bash
aws lambda update-function-code \
  --region us-east-1 \
  --function-name pitchquest-backend \
  --zip-file fileb://deployment/pitchquest_lambda.zip
```

### Update Environment Variables
```bash
# Create env_vars.json with your credentials
aws lambda update-function-configuration \
  --function-name pitchquest-backend \
  --region us-east-1 \
  --environment file://env_vars.json
```

## 🔑 Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `OPENAI_API_KEY`: OpenAI API key for GPT-4
- `CORS_ORIGINS`: Allowed origins for CORS

## 📝 API Endpoints

### Health Check
```
GET /api/health
```

### Orchestrator (Main Endpoint)
```
POST /api/orchestrator/message
{
  "message": "user message",
  "session_id": "unique-session-id",
  "current_agent": "mentor|investor|evaluator",
  "conversation_history": []
}
```

## 🧪 Testing

### Test Backend Locally
```bash
uvicorn pitchquest_api.main:app --reload --port 8000
```

### Test Lambda Deployment
```bash
curl -X POST https://am0h8n8b8i.execute-api.us-east-1.amazonaws.com/default/api/orchestrator/message \
  -H "Content-Type: application/json" \
  -d '{"message":"Test","session_id":"test-001","current_agent":"mentor","conversation_history":[]}'
```

## 🐛 Common Issues & Solutions

1. **Lambda Import Errors**: Use Docker to build with Linux binaries
2. **Database Connection**: Use Supabase pooled connection, not direct
3. **API Gateway Routing**: Ensure {proxy+} is configured
4. **CORS Issues**: Set CORS_ORIGINS environment variable

## 🚧 TODO for Production

### Security
- [ ] Rotate OpenAI API key (currently exposed)
- [ ] Set specific CORS origins (not *)
- [ ] Add rate limiting
- [ ] Implement authentication

### Performance
- [ ] Add caching for OpenAI responses
- [ ] Optimize Lambda cold starts
- [ ] Add CloudWatch monitoring

### Features
- [ ] Add more investor personas
- [ ] Implement session timeout
- [ ] Add export functionality for feedback
- [ ] Create admin dashboard

---

**Last Updated**: August 19, 2025
**Status**: Backend deployed, frontend pending
**Maintainer**: Salman Bey