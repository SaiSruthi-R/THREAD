# Memory Mapping - Quick Start Guide

## 🎯 What You're Building
A full-stack AI-powered contextual knowledge system that acts as your organization's digital memory. It ingests data from emails, Slack, GitHub, and documents, then lets you query it with natural language.

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  React + Tailwind | Dashboard | Ask Memory | Graph View     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      API GATEWAY                             │
│  /query | /projects | /decisions | /graph | /ingest         │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    LAMBDA FUNCTIONS                          │
│  RAG Handler | Ingestion | Projects | Decisions | Graph     │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    AI/ML SERVICES                            │
│  Bedrock (Claude + Titan) | Comprehend (NER)                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    STORAGE LAYER                             │
│  OpenSearch (Vectors) | Neptune (Graph) | DynamoDB | S3     │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Setup (5 minutes)

### Prerequisites
```bash
# Check versions
node --version    # Should be 18+
python --version  # Should be 3.11+
aws --version     # AWS CLI configured
```

### Step 1: Clone and Install
```bash
# Install backend dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..
```

### Step 2: Configure AWS
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your AWS credentials
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_REGION=us-east-1
```

### Step 3: Deploy Infrastructure
```bash
cd infrastructure/cdk
pip install -r requirements.txt

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy all stacks
cdk deploy --all

# Note the API endpoint from outputs
```

### Step 4: Seed Sample Data
```bash
# Update scripts/seed_data.py with your region if needed
python scripts/seed_data.py
```

### Step 5: Start Frontend
```bash
cd frontend

# Create .env with API endpoint from CDK output
echo "REACT_APP_API_BASE=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod" > .env

npm start
# Opens http://localhost:3000
```

## 🎮 Demo Scenario

The system comes pre-loaded with sample data:

### Sample Projects
1. **Platform Rebuild** (Active, 65% complete)
2. **Mobile App** (Planning, 20% complete)
3. **Analytics Dashboard** (Completed, 100%)

### Try These Queries
```
"Why was Feature X delayed in March?"
"What decisions were made about the API architecture?"
"Who was involved in the microservices decision?"
"Show me all decisions related to Platform Rebuild"
```

## 📊 Features to Explore

### 1. Dashboard
- View active projects count
- See project timeline (Kickoff → Architecture → API Dev → Audit → Deploy)
- Recent activities feed

### 2. Projects View
- Filter by status (active/planning/completed)
- Sort by name or progress
- View project stats (members, decisions, knowledge items)

### 3. Ask Memory (Main Feature)
- Natural language search
- Filter by: Recent decisions / Project history / Team discussions
- Get answers with:
  - Contextual summary
  - Confidence score (e.g., 85%)
  - Source references (Email, Slack, GitHub, Docs)

### 4. Knowledge Graph
- Interactive node visualization
- Node types: Project, Person, Decision, Artifact, Event
- Click nodes to see connections
- Filter by date range

### 5. Decision Timeline
- Chronological decision history
- Source links for each decision
- People involved
- Related projects

## 🎨 UI Design
- Dark navy background (#0a1628)
- Lime green accents (#84cc16)
- Monospace headers for tech aesthetic
- Data-dense, clean card layouts

## 🔧 Development

### Frontend Development
```bash
cd frontend
npm start  # Runs on http://localhost:3000
```

### Backend Testing
```bash
# Test RAG handler locally
python -c "from backend.lambda.rag_handler import lambda_handler; print(lambda_handler({'body': '{\"query\": \"test\"}'}, {}))"
```

### Infrastructure Updates
```bash
cd infrastructure/cdk
cdk diff    # Preview changes
cdk deploy  # Deploy changes
```

## 💰 Cost Breakdown

### Free Tier Usage
- **Lambda**: 1M requests/month free
- **OpenSearch**: t3.small.search free for 12 months
- **Neptune**: 30-day free trial
- **DynamoDB**: 25GB storage free
- **S3**: 5GB storage free
- **Bedrock**: Pay-per-use (~$0.01-0.05 per query)

### Estimated Monthly Cost (After Free Tier)
- Development: $0-20/month
- Production (low traffic): $50-100/month

## 🐛 Troubleshooting

### CDK Deploy Fails
```bash
# Ensure CDK is bootstrapped
cdk bootstrap aws://ACCOUNT-ID/REGION

# Check AWS credentials
aws sts get-caller-identity
```

### Frontend Can't Connect to API
```bash
# Check API endpoint in frontend/.env
# Verify CORS is enabled in API Gateway
# Check browser console for errors
```

### Lambda Timeout
```bash
# Increase timeout in CDK stack
# Check CloudWatch logs
aws logs tail /aws/lambda/MemoryMappingRAGHandler --follow
```

### OpenSearch Connection Issues
```bash
# Verify VPC security groups
# Check Lambda has VPC access
# Verify OpenSearch domain is active
```

## 📚 Next Steps

1. **Add Real Data Sources**
   - Configure Gmail API integration
   - Set up Slack webhooks
   - Add GitHub webhook handlers

2. **Enhance RAG Pipeline**
   - Fine-tune embedding models
   - Improve chunking strategy
   - Add re-ranking

3. **Expand Knowledge Graph**
   - Add more entity types
   - Create complex relationships
   - Implement graph algorithms

4. **Production Hardening**
   - Add authentication (Cognito)
   - Implement rate limiting
   - Set up monitoring/alerts
   - Add backup strategies

## 🤝 Contributing
This is a hackathon project. Feel free to fork and extend!

## 📄 License
ISC

---

**Built with ❤️ for the Memory Mapping Hackathon**
