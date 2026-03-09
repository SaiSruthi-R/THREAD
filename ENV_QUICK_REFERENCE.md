# Environment Variables - Quick Reference Card

## 📋 Configuration Values Summary

| Variable | Where to Get | When | Example |
|----------|-------------|------|---------|
| `AWS_ACCESS_KEY_ID` | IAM Console → Users → Create user | **BEFORE** deployment | `AKIAIOSFODNN7EXAMPLE` |
| `AWS_SECRET_ACCESS_KEY` | IAM Console → Users → Create user | **BEFORE** deployment | `wJalrXUtnFEMI/K7MDENG/...` |
| `AWS_REGION` | Choose from AWS regions | **BEFORE** deployment | `us-east-1` |
| `REACT_APP_API_BASE` | CDK output or API Gateway Console | **AFTER** deployment | `https://abc123.execute-api.us-east-1.amazonaws.com/prod` |
| `REACT_APP_USER_POOL_ID` | CDK output or Cognito Console | **AFTER** deployment | `us-east-1_ABC123XYZ` |
| `REACT_APP_CLIENT_ID` | CDK output or Cognito Console | **AFTER** deployment | `1234567890abcdefghijklmnop` |

---

## 🚀 Quick Setup Flow

```
1. Get AWS Credentials (IAM Console)
   ↓
2. Create .env file
   ↓
3. Add AWS credentials to .env
   ↓
4. Deploy infrastructure (cdk deploy --all)
   ↓
5. Copy API endpoint from output
   ↓
6. Copy Cognito IDs from output
   ↓
7. Update .env with new values
   ↓
8. Create frontend/.env
   ↓
9. Start frontend (npm start)
```

---

## 📍 Where to Find Each Value

### 1. AWS Credentials (BEFORE Deployment)

**AWS Console Method:**
```
1. Go to: https://console.aws.amazon.com/iam/
2. Click: Users → Add users
3. Name: memory-mapping-dev
4. Select: Programmatic access
5. Attach: AdministratorAccess policy
6. Copy: Access key ID and Secret access key
```

**AWS CLI Method:**
```bash
cat ~/.aws/credentials
```

---

### 2. AWS Region (BEFORE Deployment)

**Recommended Regions with Bedrock:**
- `us-east-1` (N. Virginia) ✅ Recommended
- `us-west-2` (Oregon) ✅
- `eu-west-1` (Ireland) ✅

**Check Bedrock availability:**
https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-regions.html

---

### 3. API Endpoint (AFTER Deployment)

**From CDK Output:**
```bash
cd infrastructure/cdk
cdk deploy MemoryMappingAPIStack

# Look for:
Outputs:
MemoryMappingAPIStack.APIEndpoint = https://abc123.execute-api.us-east-1.amazonaws.com/prod
```

**From AWS Console:**
```
1. Go to: https://console.aws.amazon.com/apigateway/
2. Find: Memory Mapping API
3. Click: Stages → prod
4. Copy: Invoke URL
```

**From CLI:**
```bash
aws cloudformation describe-stacks \
  --stack-name MemoryMappingAPIStack \
  --query 'Stacks[0].Outputs[?OutputKey==`APIEndpoint`].OutputValue' \
  --output text
```

---

### 4. Cognito User Pool ID (AFTER Deployment)

**From CDK Output:**
```bash
# Look for:
Outputs:
MemoryMappingAPIStack.UserPoolId = us-east-1_ABC123XYZ
```

**From AWS Console:**
```
1. Go to: https://console.aws.amazon.com/cognito/
2. Click: User pools
3. Find: memory-mapping-users
4. Copy: User pool ID (top of page)
```

**From CLI:**
```bash
aws cognito-idp list-user-pools --max-results 10
```

---

### 5. Cognito Client ID (AFTER Deployment)

**From CDK Output:**
```bash
# Look for:
Outputs:
MemoryMappingAPIStack.ClientId = 1234567890abcdefghijklmnop
```

**From AWS Console:**
```
1. Go to: https://console.aws.amazon.com/cognito/
2. Click: User pools → memory-mapping-users
3. Click: App integration tab
4. Scroll to: App clients
5. Copy: Client ID
```

**From CLI:**
```bash
aws cognito-idp list-user-pool-clients \
  --user-pool-id us-east-1_ABC123XYZ
```

---

## 📝 Example .env Files

### Root .env (for backend/CDK)
```bash
# AWS Credentials
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1

# API Configuration (add after deployment)
REACT_APP_API_BASE=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod

# Cognito Configuration (add after deployment)
REACT_APP_USER_POOL_ID=us-east-1_ABC123XYZ
REACT_APP_CLIENT_ID=1234567890abcdefghijklmnop
```

### frontend/.env (for React app)
```bash
REACT_APP_API_BASE=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
REACT_APP_USER_POOL_ID=us-east-1_ABC123XYZ
REACT_APP_CLIENT_ID=1234567890abcdefghijklmnop
```

---

## ✅ Verification Commands

### Test AWS Credentials
```bash
aws sts get-caller-identity
# Should show your account details
```

### Test API Endpoint
```bash
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/projects
# Should return JSON with projects
```

### Test Cognito
```bash
aws cognito-idp describe-user-pool --user-pool-id us-east-1_ABC123XYZ
# Should return user pool details
```

---

## 🔧 Common Issues

### Issue: "Access Denied" creating IAM user
**Solution:** You need admin permissions. Ask your AWS administrator.

### Issue: "Region not supported" for Bedrock
**Solution:** Use `us-east-1`, `us-west-2`, or `eu-west-1`

### Issue: Can't find API endpoint
**Solution:** 
```bash
aws cloudformation describe-stacks \
  --stack-name MemoryMappingAPIStack \
  --query 'Stacks[0].Outputs'
```

### Issue: Cognito User Pool not found
**Solution:** Make sure API stack deployed successfully:
```bash
aws cloudformation describe-stacks \
  --stack-name MemoryMappingAPIStack \
  --query 'Stacks[0].StackStatus'
```

---

## 🔗 Helpful Links

- **IAM Console**: https://console.aws.amazon.com/iam/
- **API Gateway Console**: https://console.aws.amazon.com/apigateway/
- **Cognito Console**: https://console.aws.amazon.com/cognito/
- **Bedrock Console**: https://console.aws.amazon.com/bedrock/
- **CloudFormation Console**: https://console.aws.amazon.com/cloudformation/

---

## 📚 Full Documentation

For detailed instructions, see:
- **CONFIGURATION_GUIDE.md** - Complete configuration guide
- **GETTING_STARTED.md** - Step-by-step setup
- **DEPLOYMENT_CHECKLIST.md** - Deployment steps
- **QUICKSTART.md** - 5-minute quick start

---

## 💡 Pro Tips

1. **Save CDK Outputs**: Copy all outputs to a text file for reference
2. **Use AWS CLI**: Faster than console for getting values
3. **Rotate Keys**: Change access keys every 90 days
4. **Use Secrets Manager**: For production, store secrets in AWS Secrets Manager
5. **Environment-specific**: Use different .env files for dev/staging/prod

---

**Last Updated**: March 2024
