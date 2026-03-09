# Configuration Guide - Getting Your Environment Variables

This guide explains where to get each configuration value for your `.env` file.

---

## 1. AWS Credentials

### AWS_ACCESS_KEY_ID & AWS_SECRET_ACCESS_KEY

**Option A: Create New IAM User (Recommended for Development)**

1. **Go to AWS Console**
   - Navigate to: https://console.aws.amazon.com/iam/

2. **Create IAM User**
   ```
   IAM → Users → Add users
   ```
   - User name: `memory-mapping-dev`
   - Access type: ✅ Programmatic access
   - Click "Next: Permissions"

3. **Attach Policies**
   - Click "Attach existing policies directly"
   - Select: `AdministratorAccess` (for development)
   - Or create custom policy with these permissions:
     - Lambda full access
     - DynamoDB full access
     - S3 full access
     - OpenSearch full access
     - Neptune full access
     - Bedrock full access
     - Comprehend full access
     - API Gateway full access
     - CloudFormation full access
     - IAM limited access

4. **Get Credentials**
   - Click through to "Create user"
   - **IMPORTANT**: Download the CSV or copy the credentials NOW
   - You'll see:
     ```
     Access key ID: AKIAIOSFODNN7EXAMPLE
     Secret access key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
     ```

5. **Add to .env**
   ```bash
   AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
   AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   ```

**Option B: Use Existing AWS CLI Credentials**

If you already have AWS CLI configured:

```bash
# View your credentials
cat ~/.aws/credentials

# You'll see:
[default]
aws_access_key_id = YOUR_KEY_ID
aws_secret_access_key = YOUR_SECRET_KEY
```

Copy these values to your `.env` file.

**Option C: Use AWS SSO (For Organizations)**

If your organization uses AWS SSO:

```bash
# Configure SSO
aws configure sso

# Get temporary credentials
aws sso login

# View credentials
aws configure export-credentials --profile your-profile
```

---

## 2. AWS Region

### AWS_REGION

**Choose Your Region**

Common options:
- `us-east-1` (N. Virginia) - Default, cheapest, most services
- `us-west-2` (Oregon) - Good for West Coast
- `eu-west-1` (Ireland) - Good for Europe
- `ap-southeast-1` (Singapore) - Good for Asia

**Check Bedrock Availability**

Not all regions support Bedrock. Check here:
https://docs.aws.amazon.com/bedrock/latest/userguide/bedrock-regions.html

Recommended regions with Bedrock:
- `us-east-1` ✅
- `us-west-2` ✅
- `eu-west-1` ✅

**Add to .env**
```bash
AWS_REGION=us-east-1
```

---

## 3. API Gateway Endpoint

### REACT_APP_API_BASE

**You get this AFTER deploying the infrastructure.**

### Step 1: Deploy CDK Stacks

```bash
cd infrastructure/cdk
cdk deploy --all
```

### Step 2: Get API Endpoint from Output

After deployment completes, you'll see output like:

```
✅  MemoryMappingAPIStack

Outputs:
MemoryMappingAPIStack.APIEndpoint = https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
```

### Step 3: Copy the URL

```bash
REACT_APP_API_BASE=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
```

### Alternative: Get from AWS Console

1. Go to API Gateway Console
   - https://console.aws.amazon.com/apigateway/

2. Find "Memory Mapping API"

3. Click on it → Stages → prod

4. Copy the "Invoke URL"
   ```
   https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod
   ```

### Alternative: Get from CLI

```bash
# List all APIs
aws apigateway get-rest-apis

# Get specific API details
aws apigateway get-rest-api --rest-api-id YOUR_API_ID

# Or use CloudFormation
aws cloudformation describe-stacks \
  --stack-name MemoryMappingAPIStack \
  --query 'Stacks[0].Outputs[?OutputKey==`APIEndpoint`].OutputValue' \
  --output text
```

---

## 4. Cognito Configuration

### REACT_APP_USER_POOL_ID & REACT_APP_CLIENT_ID

**You get these AFTER deploying the API stack.**

### Step 1: Get from CDK Output

After deploying `MemoryMappingAPIStack`:

```
Outputs:
MemoryMappingAPIStack.UserPoolId = us-east-1_ABC123XYZ
MemoryMappingAPIStack.ClientId = 1234567890abcdefghijklmnop
```

### Step 2: Add to .env

```bash
REACT_APP_USER_POOL_ID=us-east-1_ABC123XYZ
REACT_APP_CLIENT_ID=1234567890abcdefghijklmnop
```

### Alternative: Get from AWS Console

1. **Go to Cognito Console**
   - https://console.aws.amazon.com/cognito/

2. **Find User Pool**
   - Click "User pools"
   - Find "memory-mapping-users"
   - Click on it

3. **Get User Pool ID**
   - You'll see it at the top: `us-east-1_ABC123XYZ`
   ```bash
   REACT_APP_USER_POOL_ID=us-east-1_ABC123XYZ
   ```

4. **Get Client ID**
   - Click "App integration" tab
   - Scroll to "App clients"
   - Copy the "Client ID": `1234567890abcdefghijklmnop`
   ```bash
   REACT_APP_CLIENT_ID=1234567890abcdefghijklmnop
   ```

### Alternative: Get from CLI

```bash
# List user pools
aws cognito-idp list-user-pools --max-results 10

# Get user pool details
aws cognito-idp describe-user-pool --user-pool-id us-east-1_ABC123XYZ

# List app clients
aws cognito-idp list-user-pool-clients --user-pool-id us-east-1_ABC123XYZ

# Get app client details
aws cognito-idp describe-user-pool-client \
  --user-pool-id us-east-1_ABC123XYZ \
  --client-id YOUR_CLIENT_ID
```

---

## Complete Setup Flow

### Step-by-Step Process

```bash
# 1. Create AWS IAM User (if needed)
# → Get AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY

# 2. Choose your region
# → Set AWS_REGION=us-east-1

# 3. Create .env file
cp .env.example .env

# 4. Add AWS credentials to .env
nano .env  # or use your editor
# Add:
# AWS_ACCESS_KEY_ID=your_key
# AWS_SECRET_ACCESS_KEY=your_secret
# AWS_REGION=us-east-1

# 5. Deploy infrastructure
cd infrastructure/cdk
cdk bootstrap
cdk deploy --all

# 6. Copy outputs to .env
# → Get REACT_APP_API_BASE from output
# → Get REACT_APP_USER_POOL_ID from output
# → Get REACT_APP_CLIENT_ID from output

# 7. Update frontend .env
cd ../../frontend
echo "REACT_APP_API_BASE=https://your-api-id.execute-api.us-east-1.amazonaws.com/prod" > .env
echo "REACT_APP_USER_POOL_ID=us-east-1_ABC123XYZ" >> .env
echo "REACT_APP_CLIENT_ID=1234567890abcdefghijklmnop" >> .env

# 8. Start frontend
npm start
```

---

## Example Complete .env File

### Root .env (for backend/CDK)
```bash
# AWS Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
```

### frontend/.env (for React app)
```bash
# API Configuration
REACT_APP_API_BASE=https://abc123xyz.execute-api.us-east-1.amazonaws.com/prod

# Cognito Configuration
REACT_APP_USER_POOL_ID=us-east-1_ABC123XYZ
REACT_APP_CLIENT_ID=1234567890abcdefghijklmnop
```

---

## Verification

### Test AWS Credentials

```bash
# Test AWS CLI access
aws sts get-caller-identity

# Expected output:
{
    "UserId": "AIDAXXXXXXXXXXXXXXXXX",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/memory-mapping-dev"
}
```

### Test API Endpoint

```bash
# Test API is accessible
curl https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/projects

# Expected: JSON response with projects
```

### Test Cognito

```bash
# Describe user pool
aws cognito-idp describe-user-pool \
  --user-pool-id us-east-1_ABC123XYZ

# Expected: JSON with user pool details
```

---

## Troubleshooting

### Issue: "Access Denied" when creating IAM user

**Solution**: You need admin permissions in AWS to create IAM users.
- Ask your AWS administrator to create a user for you
- Or use AWS SSO if your organization has it

### Issue: "Region not supported" for Bedrock

**Solution**: Change to a supported region
```bash
AWS_REGION=us-east-1  # or us-west-2, eu-west-1
```

### Issue: Can't find API endpoint after deployment

**Solution**: Check CloudFormation outputs
```bash
aws cloudformation describe-stacks \
  --stack-name MemoryMappingAPIStack \
  --query 'Stacks[0].Outputs'
```

### Issue: Cognito User Pool not found

**Solution**: Make sure API stack deployed successfully
```bash
aws cloudformation describe-stacks \
  --stack-name MemoryMappingAPIStack \
  --query 'Stacks[0].StackStatus'

# Should show: CREATE_COMPLETE or UPDATE_COMPLETE
```

---

## Security Best Practices

### 1. Never Commit .env Files
```bash
# Already in .gitignore
.env
.env.local
frontend/.env
```

### 2. Rotate Access Keys Regularly
```bash
# Create new key
aws iam create-access-key --user-name memory-mapping-dev

# Update .env with new key

# Delete old key
aws iam delete-access-key \
  --user-name memory-mapping-dev \
  --access-key-id OLD_KEY_ID
```

### 3. Use Least Privilege
Instead of `AdministratorAccess`, create custom policy:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:*",
        "dynamodb:*",
        "s3:*",
        "es:*",
        "neptune-db:*",
        "bedrock:*",
        "comprehend:*",
        "apigateway:*",
        "cognito-idp:*",
        "cloudformation:*",
        "iam:PassRole"
      ],
      "Resource": "*"
    }
  ]
}
```

### 4. Use AWS Secrets Manager (Production)
```bash
# Store secrets in AWS Secrets Manager
aws secretsmanager create-secret \
  --name memory-mapping/api-keys \
  --secret-string '{"api_key":"your_key"}'

# Retrieve in Lambda
import boto3
secrets = boto3.client('secretsmanager')
secret = secrets.get_secret_value(SecretId='memory-mapping/api-keys')
```

---

## Quick Reference

| Variable | Where to Get | When Available |
|----------|-------------|----------------|
| `AWS_ACCESS_KEY_ID` | IAM Console → Users → Create user | Before deployment |
| `AWS_SECRET_ACCESS_KEY` | IAM Console → Users → Create user | Before deployment |
| `AWS_REGION` | Choose from AWS regions | Before deployment |
| `REACT_APP_API_BASE` | CDK output or API Gateway Console | After API stack deployed |
| `REACT_APP_USER_POOL_ID` | CDK output or Cognito Console | After API stack deployed |
| `REACT_APP_CLIENT_ID` | CDK output or Cognito Console | After API stack deployed |

---

## Need Help?

### AWS Documentation
- IAM Users: https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users.html
- Regions: https://aws.amazon.com/about-aws/global-infrastructure/regions_az/
- API Gateway: https://docs.aws.amazon.com/apigateway/
- Cognito: https://docs.aws.amazon.com/cognito/

### Common Commands
```bash
# Check AWS CLI version
aws --version

# Configure AWS CLI
aws configure

# List all CloudFormation stacks
aws cloudformation list-stacks

# Get all outputs from a stack
aws cloudformation describe-stacks \
  --stack-name MemoryMappingAPIStack \
  --query 'Stacks[0].Outputs'
```

---

**Last Updated**: March 2024
