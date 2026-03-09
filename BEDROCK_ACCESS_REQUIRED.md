# ⚠️ AWS Bedrock Access Required

## Current Status

Both the AI Assistant and Ask Memory (RAG) features require AWS Bedrock access, which now needs a use case form submission for Anthropic Claude models.

---

## Error Message

```
Model use case details have not been submitted for this account. 
Fill out the Anthropic use case details form before using the model. 
If you have already filled out the form, try again in 15 minutes.
```

---

## What's Working ✅

| Feature | Status | Description |
|---------|--------|-------------|
| Dashboard | ✅ Working | Project overview and statistics |
| Projects View | ✅ Working | Manage and view projects |
| Decision Timeline | ✅ Working | Track decision history |
| Knowledge Graph | ✅ Working | Visualize relationships (Neptune) |
| Data Ingestion | ✅ Working | Upload and process data |

## What Needs Bedrock Access ⚠️

| Feature | Status | Reason |
|---------|--------|--------|
| Ask Memory (RAG) | ⚠️ Needs Bedrock | Uses Claude 3.5 for AI queries |
| AI Assistant | ⚠️ Needs Bedrock | Uses Claude 3.5 for code generation |

---

## How to Enable Bedrock Access

### Step 1: Submit Use Case Form

1. **Open AWS Bedrock Console**:
   ```
   https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
   ```

2. **Click "Modify model access"**

3. **Select Anthropic Claude models**:
   - ☑ Claude 3.5 Sonnet
   - ☑ Claude 3 Sonnet
   - ☑ Claude 3 Haiku

4. **Fill out the use case form**:
   - **Use Case**: Development and testing of AI-powered knowledge management system
   - **Industry**: Technology / Software Development
   - **Description**: Building a contextual knowledge system with RAG capabilities for project management and code generation

5. **Submit the form**

6. **Wait 15 minutes** for approval (usually instant for development use cases)

### Step 2: Verify Access

After 15 minutes, test the access:

```powershell
# Test AI Assistant
$body = @{
    action = "generate_code"
    language = "python"
    framework = "FastAPI"
    requirements = "Create a hello world endpoint"
    context = "REST API"
} | ConvertTo-Json

Invoke-RestMethod -Uri "https://1ud60s1obg.execute-api.us-east-1.amazonaws.com/prod/ai-assistant" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

---

## Alternative: Use Different Models

If you can't get Anthropic access, you can modify the code to use other Bedrock models:

### Option 1: Amazon Titan

**Pros**: No use case form required, instant access
**Cons**: Less capable than Claude

**Changes needed**:
1. Update `backend/lambda/ai_assistant_handler.py`
2. Change model ID to `amazon.titan-text-premier-v1:0`
3. Adjust prompt format for Titan

### Option 2: Meta Llama

**Pros**: Good performance, no use case form
**Cons**: Different API format

**Changes needed**:
1. Update model ID to `meta.llama3-70b-instruct-v1:0`
2. Adjust prompt format

---

## Current Infrastructure

Everything is deployed and ready:

✅ **Lambda Functions**:
- AIAssistantHandler (deployed)
- RAGHandler (deployed)
- All other handlers (working)

✅ **DynamoDB Tables**:
- Projects table (working)
- Decisions table (working)
- Recommendations table (ready)

✅ **API Endpoints**:
- `/ai-assistant` (ready, needs Bedrock)
- `/query` (ready, needs Bedrock)
- All other endpoints (working)

✅ **Frontend**:
- AI Assistant UI (deployed)
- Ask Memory UI (deployed)
- All other components (working)

✅ **Permissions**:
- IAM roles configured
- Bedrock permissions granted
- Just needs model access approval

---

## Timeline

1. **Submit form**: 2 minutes
2. **Wait for approval**: 15 minutes (usually instant)
3. **Test features**: 5 minutes
4. **Total**: ~20 minutes

---

## What to Do Now

### Immediate Actions:

1. **Submit the Bedrock use case form** (see Step 1 above)
2. **Wait 15 minutes**
3. **Test the AI Assistant** using the command above
4. **Test Ask Memory** from the frontend

### While Waiting:

- Explore the working features (Dashboard, Projects, Decisions, Graph)
- Review the sample data
- Plan what you want to build with the AI Assistant
- Read the documentation (`AI_ASSISTANT_GUIDE.md`)

---

## Support

If you encounter issues after submitting the form:

1. **Check form status**:
   ```
   https://console.aws.amazon.com/bedrock/home?region=us-east-1#/modelaccess
   ```

2. **Verify region**: Make sure you're in `us-east-1`

3. **Check Lambda logs**:
   ```powershell
   aws logs tail /aws/lambda/MemoryMappingAIStack-AIAssistantHandler --follow --region us-east-1
   ```

4. **Try different region**: Some regions have instant access

---

## Summary

**Status**: 5 out of 7 features working (71%)

**Blocking Issue**: AWS Bedrock model access approval

**Solution**: Submit use case form (2 minutes)

**ETA**: 15-20 minutes until full functionality

**All infrastructure is deployed and ready** - just waiting on AWS approval!

---

**Last Updated**: March 8, 2026
**Next Step**: Submit Bedrock use case form
