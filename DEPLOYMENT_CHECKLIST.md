# Memory Mapping - Deployment Checklist

## Pre-Deployment Checklist

### ✅ AWS Account Setup
- [ ] AWS account created and verified
- [ ] Billing alerts configured
- [ ] AWS CLI installed and configured
- [ ] IAM user with appropriate permissions created
- [ ] Access keys generated and stored securely
- [ ] Bedrock model access requested and approved
  - [ ] Claude 3.5 Sonnet
  - [ ] Titan Embeddings

### ✅ Development Environment
- [ ] Node.js 18+ installed
- [ ] Python 3.11+ installed
- [ ] AWS CDK installed (`npm install -g aws-cdk`)
- [ ] Git installed and configured
- [ ] Code editor setup (VS Code recommended)

### ✅ Repository Setup
- [ ] Repository cloned
- [ ] `.env` file created from `.env.example`
- [ ] AWS credentials added to `.env`
- [ ] `.gitignore` configured properly

### ✅ Dependencies Installed
- [ ] Backend: `pip install -r requirements.txt`
- [ ] Frontend: `cd frontend && npm install`
- [ ] CDK: `cd infrastructure/cdk && pip install -r requirements.txt`

---

## Deployment Steps

### Step 1: Configure AWS Credentials
```bash
# Option 1: Environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1

# Option 2: AWS CLI configure
aws configure

# Verify credentials
aws sts get-caller-identity
```

**Expected Output:**
```json
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/your-user"
}
```

### Step 2: Bootstrap CDK
```bash
cd infrastructure/cdk

# Bootstrap CDK (first time only)
cdk bootstrap aws://ACCOUNT-ID/REGION

# Example
cdk bootstrap aws://123456789012/us-east-1
```

**Expected Output:**
```
✅ Environment aws://123456789012/us-east-1 bootstrapped
```

### Step 3: Deploy Storage Stack
```bash
# Preview changes
cdk diff MemoryMappingStorageStack

# Deploy
cdk deploy MemoryMappingStorageStack

# Confirm deployment
# Type 'y' when prompted
```

**Expected Resources:**
- DynamoDB tables: memory-metadata, memory-projects, memory-decisions
- Neptune cluster
- OpenSearch domain
- VPC with subnets

**Estimated Time:** 15-20 minutes

### Step 4: Deploy Ingestion Stack
```bash
cdk deploy MemoryMappingIngestionStack
```

**Expected Resources:**
- SQS queue
- S3 bucket
- Ingestion Lambda
- Graph updater Lambda

**Estimated Time:** 5-10 minutes

### Step 5: Deploy AI Stack
```bash
cdk deploy MemoryMappingAIStack
```

**Expected Resources:**
- RAG Lambda with Bedrock permissions
- IAM roles and policies

**Estimated Time:** 3-5 minutes

### Step 6: Deploy API Stack
```bash
cdk deploy MemoryMappingAPIStack
```

**Expected Resources:**
- API Gateway
- Lambda integrations
- Cognito User Pool

**Estimated Time:** 5-10 minutes

### Step 7: Note API Endpoint
```bash
# Get API endpoint from stack outputs
aws cloudformation describe-stacks \
  --stack-name MemoryMappingAPIStack \
  --query 'Stacks[0].Outputs[?OutputKey==`APIEndpoint`].OutputValue' \
  --output text
```

**Save this URL** - you'll need it for the frontend.

### Step 8: Seed Sample Data
```bash
cd ../../scripts

# Update region in seed_data.py if needed
python seed_data.py
```

**Expected Output:**
```
Seeding sample data...
Created project: Platform Rebuild
Created project: Mobile App
Created project: Analytics Dashboard
Created decision: Switch to Microservices Architecture
...
Sample data seeded successfully!
```

### Step 9: Configure Frontend
```bash
cd ../frontend

# Create .env file
echo "REACT_APP_API_BASE=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod" > .env

# Install dependencies (if not done)
npm install
```

### Step 10: Test Frontend Locally
```bash
# Start development server
npm start

# Should open http://localhost:3000
```

**Verify:**
- [ ] Dashboard loads
- [ ] Projects view shows 3 projects
- [ ] Ask Memory interface is accessible
- [ ] No console errors

### Step 11: Build Frontend for Production
```bash
# Build optimized production bundle
npm run build

# Output in frontend/build/
```

### Step 12: Deploy Frontend (Optional)
```bash
# Option 1: S3 + CloudFront
aws s3 sync build/ s3://your-bucket-name
aws cloudfront create-invalidation --distribution-id YOUR_DIST_ID --paths "/*"

# Option 2: Amplify
amplify init
amplify publish

# Option 3: Vercel/Netlify
# Connect GitHub repo and deploy
```

---

## Post-Deployment Verification

### ✅ Backend Health Checks

#### Test API Gateway
```bash
API_ENDPOINT="https://your-api-id.execute-api.us-east-1.amazonaws.com/prod"

# Test projects endpoint
curl $API_ENDPOINT/projects

# Expected: JSON with projects array
```

#### Test Query Endpoint
```bash
curl -X POST $API_ENDPOINT/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Why was Feature X delayed?"}'

# Expected: JSON with answer, sources, confidence
```

#### Test Decisions Endpoint
```bash
curl $API_ENDPOINT/decisions

# Expected: JSON with decisions array
```

### ✅ Frontend Health Checks
- [ ] Navigate to all pages (Dashboard, Projects, Ask Memory, Graph, Timeline)
- [ ] Submit a test query in Ask Memory
- [ ] Filter projects by status
- [ ] Check browser console for errors
- [ ] Verify API calls in Network tab

### ✅ AWS Resource Verification

#### Lambda Functions
```bash
aws lambda list-functions --query 'Functions[?contains(FunctionName, `MemoryMapping`)].FunctionName'
```

**Expected Functions:**
- MemoryMappingRAGHandler
- MemoryMappingIngestionHandler
- MemoryMappingProjectsHandler
- MemoryMappingDecisionsHandler
- MemoryMappingGraphHandler

#### DynamoDB Tables
```bash
aws dynamodb list-tables --query 'TableNames[?contains(@, `memory`)]'
```

**Expected Tables:**
- memory-metadata
- memory-projects
- memory-decisions

#### OpenSearch Domain
```bash
aws opensearch describe-domain --domain-name memory-mapping-domain
```

**Check:** Processing = false, DomainStatus = Active

#### Neptune Cluster
```bash
aws neptune describe-db-clusters --query 'DBClusters[0].Status'
```

**Expected:** "available"

---

## Monitoring Setup

### CloudWatch Dashboards
```bash
# Create custom dashboard
aws cloudwatch put-dashboard --dashboard-name MemoryMapping \
  --dashboard-body file://cloudwatch-dashboard.json
```

### CloudWatch Alarms
```bash
# High error rate alarm
aws cloudwatch put-metric-alarm \
  --alarm-name MemoryMapping-HighErrorRate \
  --alarm-description "Alert when error rate > 5%" \
  --metric-name Errors \
  --namespace AWS/Lambda \
  --statistic Sum \
  --period 300 \
  --threshold 5 \
  --comparison-operator GreaterThanThreshold

# High latency alarm
aws cloudwatch put-metric-alarm \
  --alarm-name MemoryMapping-HighLatency \
  --alarm-description "Alert when latency > 3s" \
  --metric-name Duration \
  --namespace AWS/Lambda \
  --statistic Average \
  --period 300 \
  --threshold 3000 \
  --comparison-operator GreaterThanThreshold
```

### Log Groups
```bash
# View Lambda logs
aws logs tail /aws/lambda/MemoryMappingRAGHandler --follow

# View API Gateway logs
aws logs tail /aws/apigateway/MemoryMappingAPI --follow
```

---

## Troubleshooting Guide

### Issue: CDK Bootstrap Fails
**Error:** `Need to perform AWS calls for account XXX, but no credentials found`

**Solution:**
```bash
# Configure AWS credentials
aws configure

# Or set environment variables
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
export AWS_REGION=us-east-1
```

### Issue: CDK Deploy Fails - Insufficient Permissions
**Error:** `User is not authorized to perform: iam:CreateRole`

**Solution:**
```bash
# Attach AdministratorAccess policy (for development)
aws iam attach-user-policy \
  --user-name your-user \
  --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Or create custom policy with required permissions
```

### Issue: Bedrock Access Denied
**Error:** `AccessDeniedException: Could not access model`

**Solution:**
1. Go to AWS Console → Bedrock → Model access
2. Request access to:
   - Claude 3.5 Sonnet
   - Titan Embeddings
3. Wait for approval (usually instant)
4. Redeploy AI stack

### Issue: OpenSearch Domain Creation Fails
**Error:** `Service linked role does not exist`

**Solution:**
```bash
# Create OpenSearch service-linked role
aws iam create-service-linked-role \
  --aws-service-name es.amazonaws.com
```

### Issue: Neptune Cluster Stuck in Creating
**Symptom:** Cluster status remains "creating" for > 30 minutes

**Solution:**
1. Check VPC subnet configuration
2. Ensure at least 2 subnets in different AZs
3. Verify security group rules
4. Check CloudFormation events for errors

### Issue: Lambda Timeout
**Error:** `Task timed out after 3.00 seconds`

**Solution:**
```python
# In CDK stack, increase timeout
lambda_.Function(
    self, "RAGHandler",
    timeout=Duration.seconds(60),  # Increase from 3 to 60
    memory_size=1024  # Also increase memory
)

# Redeploy
cdk deploy MemoryMappingAIStack
```

### Issue: Frontend Can't Connect to API
**Error:** `Network Error` or `CORS Error`

**Solution:**
1. Verify API endpoint in frontend/.env
2. Check API Gateway CORS configuration
3. Verify API is deployed (not just created)
4. Check browser console for exact error

```bash
# Test API directly
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/projects
```

### Issue: Query Returns Empty Results
**Symptom:** Query succeeds but returns no sources

**Solution:**
1. Verify data was seeded
```bash
python scripts/seed_data.py
```

2. Check OpenSearch index
```bash
# Get OpenSearch endpoint
aws opensearch describe-domain \
  --domain-name memory-mapping-domain \
  --query 'DomainStatus.Endpoint'

# Check index (requires VPN/bastion if in VPC)
curl https://opensearch-endpoint/_cat/indices
```

3. Check Lambda logs
```bash
aws logs tail /aws/lambda/MemoryMappingRAGHandler --follow
```

### Issue: High Costs
**Symptom:** AWS bill higher than expected

**Solution:**
1. Check Bedrock usage
```bash
aws ce get-cost-and-usage \
  --time-period Start=2024-03-01,End=2024-03-31 \
  --granularity MONTHLY \
  --metrics BlendedCost \
  --group-by Type=SERVICE
```

2. Reduce OpenSearch instance size
```python
# In storage_stack.py
capacity=opensearch.CapacityConfig(
    data_node_instance_type="t3.small.search",  # Use smallest
    data_nodes=1  # Use single node for dev
)
```

3. Enable DynamoDB on-demand billing
4. Set S3 lifecycle policies
5. Delete unused resources

---

## Rollback Procedure

### Rollback Single Stack
```bash
# List stack versions
aws cloudformation list-stack-resources \
  --stack-name MemoryMappingAPIStack

# Rollback to previous version
cdk deploy MemoryMappingAPIStack --rollback
```

### Complete Teardown
```bash
# Destroy all stacks (in reverse order)
cdk destroy MemoryMappingAPIStack
cdk destroy MemoryMappingAIStack
cdk destroy MemoryMappingIngestionStack
cdk destroy MemoryMappingStorageStack

# Confirm each deletion
```

**Warning:** This will delete all data!

---

## Performance Optimization

### After Deployment

#### 1. Enable API Gateway Caching
```bash
aws apigateway update-stage \
  --rest-api-id your-api-id \
  --stage-name prod \
  --patch-operations \
    op=replace,path=/cacheClusterEnabled,value=true \
    op=replace,path=/cacheClusterSize,value=0.5
```

#### 2. Configure Lambda Reserved Concurrency
```bash
aws lambda put-function-concurrency \
  --function-name MemoryMappingRAGHandler \
  --reserved-concurrent-executions 10
```

#### 3. Enable X-Ray Tracing
```bash
aws lambda update-function-configuration \
  --function-name MemoryMappingRAGHandler \
  --tracing-config Mode=Active
```

#### 4. Optimize OpenSearch
- Enable slow log analysis
- Configure index refresh interval
- Set up index lifecycle management

---

## Security Hardening

### Post-Deployment Security

#### 1. Enable CloudTrail
```bash
aws cloudtrail create-trail \
  --name memory-mapping-trail \
  --s3-bucket-name your-cloudtrail-bucket
```

#### 2. Enable GuardDuty
```bash
aws guardduty create-detector --enable
```

#### 3. Configure WAF Rules
```bash
# Create WAF web ACL
aws wafv2 create-web-acl \
  --name memory-mapping-waf \
  --scope REGIONAL \
  --default-action Allow={} \
  --rules file://waf-rules.json
```

#### 4. Rotate Access Keys
```bash
# Create new access key
aws iam create-access-key --user-name your-user

# Update .env with new keys

# Delete old access key
aws iam delete-access-key \
  --user-name your-user \
  --access-key-id OLD_KEY_ID
```

---

## Maintenance Schedule

### Daily
- [ ] Check CloudWatch alarms
- [ ] Review error logs
- [ ] Monitor costs

### Weekly
- [ ] Review performance metrics
- [ ] Check for AWS service updates
- [ ] Backup critical data

### Monthly
- [ ] Update dependencies
- [ ] Review security groups
- [ ] Optimize costs
- [ ] Test disaster recovery

---

## Success Criteria

### ✅ Deployment Successful When:
- [ ] All CDK stacks deployed without errors
- [ ] All Lambda functions are active
- [ ] API Gateway returns 200 for health checks
- [ ] Frontend loads without errors
- [ ] Sample queries return results
- [ ] CloudWatch logs show no errors
- [ ] All AWS resources are in "available" state
- [ ] Costs are within expected range

---

**Deployment Version**: 1.0.0
**Last Updated**: March 2024
