# OpenSearch Fine-Grained Access Control Issue

## Current Status

The `/query` endpoint (RAG functionality) is experiencing an authorization error with OpenSearch due to fine-grained access control.

## Error
```
AuthorizationException(403, 'security_exception', 'no permissions for [indices:data/read/search]')
```

## Root Cause

OpenSearch domain was deployed with fine-grained access control enabled. The Lambda IAM role needs to be mapped to an OpenSearch role, but this requires:
1. Accessing the OpenSearch dashboard
2. Manually mapping the IAM role to an OpenSearch role

## Working Endpoints

✅ All other endpoints are working perfectly:
- `/projects` - List and manage projects
- `/decisions` - View decision timeline  
- `/graph` - Knowledge graph queries
- `/ingest` - Data ingestion

❌ Not working:
- `/query` - AI-powered RAG queries (OpenSearch permission issue)

## Solutions

### Option 1: Manual Role Mapping (Recommended for Production)

1. Access OpenSearch Dashboard:
   ```
   https://search-memory-mapping-domain-3s7mt7jfzfomzjxcvuph5pbw4m.us-east-1.es.amazonaws.com/_dashboards
   Username: admin
   Password: Admin123!
   ```

2. Navigate to Security → Roles → all_access

3. Add the Lambda IAM role ARN to backend roles:
   ```
   arn:aws:iam::140023380330:role/MemoryMappingAIStack-RAGHandlerServiceRole3D94B017-9GnTSPY3mVq2
   ```

### Option 2: Recreate OpenSearch Without Fine-Grained Access Control

This requires destroying and recreating the OpenSearch domain:

```powershell
# 1. Update storage_stack.py - set enabled=False for advanced_security_options
# 2. Destroy the storage stack
cdk destroy MemoryMappingStorageStack

# 3. Redeploy
cdk deploy MemoryMappingStorageStack

# 4. Re-seed data
python scripts/seed_data.py
```

**Warning**: This will delete all data in OpenSearch!

### Option 3: Use AWS CLI to Update Access Policy

```powershell
# Get the Lambda role ARN
$lambdaRole = "arn:aws:iam::140023380330:role/MemoryMappingAIStack-RAGHandlerServiceRole3D94B017-9GnTSPY3mVq2"

# Update OpenSearch access policy
aws opensearch update-domain-config `
  --domain-name memory-mapping-domain `
  --access-policies '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"AWS": "'$lambdaRole'"},
      "Action": "es:*",
      "Resource": "arn:aws:es:us-east-1:140023380330:domain/memory-mapping-domain/*"
    }]
  }' `
  --region us-east-1
```

## Temporary Workaround

For demonstration purposes, you can test the other endpoints which are all working:

### Test Projects API
```powershell
Invoke-RestMethod -Uri "https://1ud60s1obg.execute-api.us-east-1.amazonaws.com/prod/projects"
```

### Test Decisions API
```powershell
Invoke-RestMethod -Uri "https://1ud60s1obg.execute-api.us-east-1.amazonaws.com/prod/decisions"
```

### Test Graph API
```powershell
$body = '{"nodeId":"test-node","queryType":"neighbors"}' | ConvertTo-Json
Invoke-RestMethod -Uri "https://1ud60s1obg.execute-api.us-east-1.amazonaws.com/prod/graph" `
  -Method POST `
  -Body $body `
  -ContentType "application/json"
```

## Impact

- Frontend Dashboard: ✅ Working
- Projects View: ✅ Working
- Decision Timeline: ✅ Working
- Knowledge Graph: ✅ Working (Neptune)
- Ask Memory (RAG): ❌ Not working (OpenSearch permissions)

## Next Steps

1. Choose one of the solutions above
2. Implement the fix
3. Test the `/query` endpoint
4. Verify the "Ask Memory" feature in the frontend

## Additional Notes

- The Lambda layer with dependencies is working correctly
- CORS headers are properly configured
- All other AWS services (DynamoDB, Neptune, Bedrock, API Gateway) are functioning
- This is purely an OpenSearch access control configuration issue

---

**Status**: 4 out of 5 features working
**Blocking Issue**: OpenSearch fine-grained access control
**Estimated Fix Time**: 5-10 minutes with Option 1
