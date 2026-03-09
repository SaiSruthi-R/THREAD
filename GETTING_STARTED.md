# Getting Started - Memory Mapping

## 🚀 Quick Setup (15 minutes)

Follow these steps to get Memory Mapping running on your machine.

---

## Prerequisites Checklist

Before you begin, make sure you have:

- [ ] AWS Account (create at https://aws.amazon.com)
- [ ] Node.js 18+ installed (`node --version`)
- [ ] Python 3.11+ installed (`python --version`)
- [ ] AWS CLI installed (`aws --version`)
- [ ] Git installed (`git --version`)

---

## Step 1: Get AWS Credentials (5 minutes)

### Option A: Create New IAM User

1. **Login to AWS Console**
   - Go to: https://console.aws.amazon.com/iam/

2. **Create User**
   ```
   IAM → Users → Add users
   Name: memory-mapping-dev
   Access type: ✅ Programmatic access
   ```

3. **Attach Policy**
   ```
   Attach existing policies directly
   Select: AdministratorAccess
   ```

4. **Save Credentials**
   ```
   Download CSV or copy:
   Access key ID: AKIAIOSFODNN7EXAMPLE
   Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   ```

### Option B: Use Existing Credentials

```bash
# If you already have AWS CLI configured
cat ~/.aws/credentials

# Copy the access_key_id and secret_access_key
```

---

## Step 2: Clone and Setup (2 minutes)

```bash
# Clone repository
git clone https://github.com/yourusername/memory-mapping.git
cd memory-mapping

# Create .env file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your favorite editor
```

**Add to .env:**
```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```

**Verify AWS access:**
```bash
aws sts get-caller-identity
# Should show your account details
```

---

## Step 3: Install Dependencies (3 minutes)

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
cd ..

# Install CDK dependencies
cd infrastructure/cdk
pip install -r requirements.txt
cd ../..
```

---

## Step 4: Request Bedrock Access (1 minute)

1. **Go to Bedrock Console**
   - https://console.aws.amazon.com/bedrock/

2. **Request Model Access**
   ```
   Model access → Manage model access
   Select:
   ✅ Claude 3.5 Sonnet
   ✅ Titan Embeddings G1 - Text
   
   Click: Request model access
   ```

3. **Wait for Approval** (usually instant)

---

## Step 5: Deploy Infrastructure (15-20 minutes)

```bash
cd infrastructure/cdk

# Bootstrap CDK (first time only)
cdk bootstrap

# Deploy all stacks
cdk deploy --all

# Type 'y' when prompted for each stack
```

**What gets deployed:**
- ✅ DynamoDB tables (3)
- ✅ OpenSearch domain
- ✅ Neptune cluster
- ✅ Lambda functions (6)
- ✅ API Gateway
- ✅ Cognito User Pool
- ✅ S3 bucket
- ✅ SQS queue

**Save the outputs!** You'll see:
```
Outputs:
MemoryMappingAPIStack.APIEndpoint = https://abc123.execute-api.us-east-1.amazonaws.com/prod
MemoryMappingAPIStack.UserPoolId = us-east-1_ABC123
MemoryMappingAPIStack.ClientId = 1234567890abcdef
```

---

## Step 6: Update Configuration (1 minute)

### Update root .env
```bash
# Add these to your root .env file
echo "REACT_APP_API_BASE=https://abc123.execute-api.us-east-1.amazonaws.com/prod" >> .env
echo "REACT_APP_USER_POOL_ID=us-east-1_ABC123" >> .env
echo "REACT_APP_CLIENT_ID=1234567890abcdef" >> .env
```

### Create frontend .env
```bash
cd frontend

# Create frontend-specific .env
cat > .env << EOF
REACT_APP_API_BASE=https://abc123.execute-api.us-east-1.amazonaws.com/prod
REACT_APP_USER_POOL_ID=us-east-1_ABC123
REACT_APP_CLIENT_ID=1234567890abcdef
EOF

cd ..
```

---

## Step 7: Seed Sample Data (1 minute)

```bash
# Load sample projects and decisions
python scripts/seed_data.py
```

**Expected output:**
```
Seeding sample data...
Created project: Platform Rebuild
Created project: Mobile App
Created project: Analytics Dashboard
Created decision: Switch to Microservices Architecture
...
Sample data seeded successfully!
```

---

## Step 8: Start Frontend (1 minute)

```bash
cd frontend
npm start
```

**Browser opens automatically at:** http://localhost:3000

---

## Step 9: Test the System (2 minutes)

### Test 1: View Dashboard
- Navigate to http://localhost:3000
- You should see 3 projects
- Timeline should show 5 steps

### Test 2: View Projects
- Click "Projects" in sidebar
- Should see 3 project cards
- Try filtering by "Active"

### Test 3: Ask Memory
- Click "Ask Memory" in sidebar
- Type: "Why was Feature X delayed in March?"
- Click "Search"
- Should get answer with sources and confidence score

### Test 4: View Graph
- Click "Knowledge Graph" in sidebar
- Should see interactive node visualization

### Test 5: View Timeline
- Click "Decision Timeline" in sidebar
- Should see 5 decisions chronologically

---

## Troubleshooting

### Issue: AWS credentials not working
```bash
# Test credentials
aws sts get-caller-identity

# If fails, reconfigure
aws configure
```

### Issue: CDK bootstrap fails
```bash
# Make sure you have admin permissions
# Or ask your AWS admin to bootstrap for you
cdk bootstrap aws://ACCOUNT-ID/us-east-1
```

### Issue: Bedrock access denied
```bash
# Go to Bedrock console and request access
# https://console.aws.amazon.com/bedrock/
# Model access → Request access for Claude and Titan
```

### Issue: Frontend can't connect to API
```bash
# Verify API endpoint
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/projects

# Check frontend/.env has correct API_BASE
cat frontend/.env
```

### Issue: No data showing
```bash
# Re-run seed script
python scripts/seed_data.py

# Check DynamoDB tables
aws dynamodb scan --table-name memory-projects --limit 5
```

---

## What's Next?

### Explore the System
- Try different queries in Ask Memory
- Explore the knowledge graph
- Filter projects by status
- View decision timeline

### Add Real Data
- Configure email integration
- Set up Slack webhooks
- Add GitHub webhooks
- Upload documents to S3

### Customize
- Modify UI colors in `frontend/tailwind.config.js`
- Add new Lambda functions
- Extend the knowledge graph
- Add more entity types

---

## Quick Commands Reference

```bash
# Start frontend
cd frontend && npm start

# View Lambda logs
aws logs tail /aws/lambda/MemoryMappingRAGHandler --follow

# Test API
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/projects

# Redeploy infrastructure
cd infrastructure/cdk && cdk deploy --all

# Seed data
python scripts/seed_data.py

# Run tests
cd frontend && npm test
```

---

## Architecture Overview

```
┌─────────────┐
│   Browser   │ http://localhost:3000
└──────┬──────┘
       │
       ↓ HTTPS
┌─────────────┐
│ API Gateway │ /query, /projects, /decisions, /graph
└──────┬──────┘
       │
       ↓
┌─────────────┐
│   Lambda    │ RAG, Ingestion, Projects, Decisions, Graph
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Bedrock    │ Claude 3.5 + Titan Embeddings
│ Comprehend  │ Entity Extraction
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ OpenSearch  │ Vector search
│  Neptune    │ Knowledge graph
│  DynamoDB   │ Metadata
│     S3      │ Documents
└─────────────┘
```

---

## Cost Estimate

### Free Tier (First 12 months)
- Lambda: Free (1M requests/month)
- OpenSearch: Free
- DynamoDB: Free (25GB)
- S3: Free (5GB)

### Pay-Per-Use
- Bedrock: ~$0.01-0.05 per query
- Neptune: ~$0.10/hour (30-day trial)

**Total for testing: $0-20/month**

---

## Support

### Documentation
- **Quick Start**: QUICKSTART.md
- **Configuration**: CONFIGURATION_GUIDE.md
- **API Reference**: API_DOCUMENTATION.md
- **Architecture**: ARCHITECTURE.md
- **Testing**: TESTING.md
- **Deployment**: DEPLOYMENT_CHECKLIST.md

### Get Help
- Check CONFIGURATION_GUIDE.md for detailed setup
- Review DEPLOYMENT_CHECKLIST.md for troubleshooting
- Check AWS CloudWatch logs for errors

---

## Success Checklist

- [ ] AWS credentials configured
- [ ] Dependencies installed
- [ ] Bedrock access approved
- [ ] Infrastructure deployed
- [ ] API endpoint obtained
- [ ] Configuration updated
- [ ] Sample data seeded
- [ ] Frontend running
- [ ] Test query successful
- [ ] All views accessible

---

**Congratulations! You're ready to use Memory Mapping! 🎉**

Try asking: "Why was Feature X delayed in March?"

---

**Last Updated**: March 2024
