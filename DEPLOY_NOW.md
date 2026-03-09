# 🚀 Deploy Memory Mapping - Step by Step

## Current Status
✅ Node.js v25.2.1 installed
✅ Python 3.14.2 installed
✅ NPM 11.6.2 installed
❌ AWS CLI not installed

---

## Step 1: Install AWS CLI (5 minutes)

### For Windows:

**Option A: Using MSI Installer (Recommended)**
1. Download AWS CLI installer:
   - Go to: https://awscli.amazonaws.com/AWSCLIV2.msi
   - Run the downloaded file
   - Follow the installation wizard
   - Click "Next" → "Next" → "Install"

2. Verify installation:
   ```powershell
   # Close and reopen PowerShell, then run:
   aws --version
   ```

**Option B: Using Python pip**
```powershell
pip install awscli
aws --version
```

---

## Step 2: Configure AWS Credentials (5 minutes)

### Get AWS Credentials

1. **Login to AWS Console**
   - Go to: https://console.aws.amazon.com/

2. **Create IAM User**
   - Navigate to: IAM → Users → Add users
   - User name: `memory-mapping-dev`
   - Access type: ✅ Programmatic access
   - Click "Next: Permissions"

3. **Attach Policy**
   - Click "Attach existing policies directly"
   - Search and select: `AdministratorAccess`
   - Click "Next: Tags" → "Next: Review" → "Create user"

4. **Save Credentials**
   - ⚠️ IMPORTANT: Copy these NOW (you won't see them again!)
   - Access key ID: `AKIAIOSFODNN7EXAMPLE`
   - Secret access key: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

### Configure AWS CLI

```powershell
# Run this command
aws configure

# Enter when prompted:
AWS Access Key ID: [paste your access key]
AWS Secret Access Key: [paste your secret key]
Default region name: us-east-1
Default output format: json
```

### Verify Configuration

```powershell
aws sts get-caller-identity
```

Expected output:
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/memory-mapping-dev"
}
```

---

## Step 3: Request Bedrock Access (2 minutes)

1. **Go to Bedrock Console**
   - https://console.aws.amazon.com/bedrock/

2. **Request Model Access**
   - Click "Model access" in left sidebar
   - Click "Manage model access"
   - Select these models:
     - ✅ Claude 3.5 Sonnet
     - ✅ Titan Embeddings G1 - Text
   - Click "Request model access"

3. **Wait for Approval** (usually instant)
   - Status should change to "Access granted"

---

## Step 4: Create Environment File (1 minute)

```powershell
# Create .env file from template
Copy-Item .env.example .env

# Open .env in notepad
notepad .env
```

**Edit .env and add your AWS credentials:**
```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1

# Leave these blank for now (we'll fill them after deployment)
REACT_APP_API_BASE=
REACT_APP_USER_POOL_ID=
REACT_APP_CLIENT_ID=
```

Save and close the file.

---

## Step 5: Install Dependencies (5 minutes)

```powershell
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

## Step 6: Install AWS CDK (2 minutes)

```powershell
# Install CDK globally
npm install -g aws-cdk

# Verify installation
cdk --version
```

---

## Step 7: Bootstrap CDK (3 minutes)

```powershell
cd infrastructure/cdk

# Bootstrap CDK (first time only)
cdk bootstrap

# This creates necessary resources in your AWS account
```

Expected output:
```
✅ Environment aws://123456789012/us-east-1 bootstrapped
```

---

## Step 8: Deploy Infrastructure (20-25 minutes)

```powershell
# Deploy all stacks
cdk deploy --all

# You'll be prompted to approve changes for each stack
# Type 'y' and press Enter for each prompt
```

**What gets deployed:**
1. MemoryMappingStorageStack (15-20 min)
   - DynamoDB tables
   - OpenSearch domain
   - Neptune cluster
   - VPC and networking

2. MemoryMappingIngestionStack (3-5 min)
   - SQS queue
   - S3 bucket
   - Ingestion Lambda

3. MemoryMappingAIStack (2-3 min)
   - RAG Lambda
   - Bedrock permissions

4. MemoryMappingAPIStack (3-5 min)
   - API Gateway
   - Cognito User Pool
   - All Lambda integrations

**⚠️ IMPORTANT: Save the outputs!**

At the end, you'll see:
```
Outputs:
MemoryMappingAPIStack.APIEndpoint = https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
MemoryMappingAPIStack.UserPoolId = us-east-1_ABC123XYZ
MemoryMappingAPIStack.ClientId = 1234567890abcdefghijklmnop
```

**Copy these values!** You'll need them in the next step.

---

## Step 9: Update Configuration (2 minutes)

```powershell
# Go back to root directory
cd ../..

# Open .env file
notepad .env
```

**Add the values from CDK output:**
```bash
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1

# Add these from CDK output:
REACT_APP_API_BASE=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
REACT_APP_USER_POOL_ID=us-east-1_ABC123XYZ
REACT_APP_CLIENT_ID=1234567890abcdefghijklmnop
```

Save and close.

**Create frontend .env:**
```powershell
cd frontend

# Create frontend .env file
@"
REACT_APP_API_BASE=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
REACT_APP_USER_POOL_ID=us-east-1_ABC123XYZ
REACT_APP_CLIENT_ID=1234567890abcdefghijklmnop
"@ | Out-File -FilePath .env -Encoding utf8

cd ..
```

---

## Step 10: Seed Sample Data (1 minute)

```powershell
# Load sample projects and decisions
python scripts/seed_data.py
```

Expected output:
```
Seeding sample data...
Created project: Platform Rebuild
Created project: Mobile App
Created project: Analytics Dashboard
Created decision: Switch to Microservices Architecture
Created decision: API Gateway Implementation
Created decision: Feature X Delayed Due to Dependencies
Created decision: React Native vs Native Development
Created decision: Real-time Data Pipeline Architecture

Sample data seeded successfully!

You can now query: 'Why was Feature X delayed in March?'
```

---

## Step 11: Start the Application (1 minute)

```powershell
cd frontend
npm start
```

**Your browser will automatically open to:** http://localhost:3000

---

## Step 12: Test the Application (5 minutes)

### Test 1: Dashboard
- You should see 3 active projects
- Timeline with 5 steps
- Recent activities

### Test 2: Projects View
- Click "Projects" in sidebar
- Should see 3 project cards
- Try filtering by "Active"

### Test 3: Ask Memory (Main Feature!)
- Click "Ask Memory" in sidebar
- Type: `Why was Feature X delayed in March?`
- Click "Search"
- Should get an answer with sources and confidence score

### Test 4: Knowledge Graph
- Click "Knowledge Graph" in sidebar
- Should see interactive node visualization

### Test 5: Decision Timeline
- Click "Decision Timeline" in sidebar
- Should see 5 decisions chronologically

---

## 🎉 Success!

If all tests pass, your Memory Mapping system is fully deployed and running!

---

## Troubleshooting

### Issue: AWS CLI not found after installation
**Solution:** Close and reopen PowerShell/Terminal

### Issue: CDK bootstrap fails
**Solution:** 
```powershell
# Make sure AWS credentials are configured
aws sts get-caller-identity

# If fails, run:
aws configure
```

### Issue: Bedrock access denied
**Solution:** 
1. Go to https://console.aws.amazon.com/bedrock/
2. Click "Model access"
3. Request access for Claude and Titan models
4. Wait for approval (usually instant)

### Issue: CDK deploy fails with "Stack already exists"
**Solution:**
```powershell
# Update existing stack
cdk deploy --all --require-approval never
```

### Issue: Frontend shows "Network Error"
**Solution:**
1. Check frontend/.env has correct API endpoint
2. Test API directly:
```powershell
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/projects
```

### Issue: No data showing in UI
**Solution:**
```powershell
# Re-run seed script
python scripts/seed_data.py
```

---

## Next Steps

1. **Try different queries:**
   - "What decisions were made about the API?"
   - "Who was involved in the microservices decision?"
   - "Show me all decisions related to Platform Rebuild"

2. **Explore the knowledge graph:**
   - Click on nodes to see connections
   - Filter by date range

3. **Add real data:**
   - Configure email integration
   - Set up Slack webhooks
   - Add GitHub webhooks

---

## Cost Monitoring

Check your AWS costs:
```powershell
aws ce get-cost-and-usage `
  --time-period Start=2024-03-01,End=2024-03-31 `
  --granularity MONTHLY `
  --metrics BlendedCost
```

Expected cost for testing: $0-20/month (mostly Bedrock usage)

---

## Cleanup (When Done Testing)

To delete all resources and stop charges:
```powershell
cd infrastructure/cdk

# Destroy all stacks
cdk destroy --all

# Type 'y' to confirm each deletion
```

---

**Need Help?** Check these guides:
- CONFIGURATION_GUIDE.md - Configuration details
- DEPLOYMENT_CHECKLIST.md - Detailed deployment steps
- TROUBLESHOOTING section above

**Last Updated:** March 2024
