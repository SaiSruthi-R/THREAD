import json
import boto3
import os
from datetime import datetime

bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

projects_table = dynamodb.Table(os.environ.get('PROJECTS_TABLE', 'memory-projects'))

def lambda_handler(event, context):
    """AI Assistant for project upscaling and code generation"""
    body = json.loads(event.get('body', '{}'))
    action = body.get('action')  # 'upscale', 'generate_code', 'architecture', 'review'
    
    try:
        if action == 'upscale':
            result = upscale_project(body)
        elif action == 'generate_code':
            result = generate_code(body)
        elif action == 'architecture':
            result = suggest_architecture(body)
        elif action == 'review':
            result = review_code(body)
        else:
            return error_response(400, 'Invalid action. Use: upscale, generate_code, architecture, or review')
        
        return success_response(result)
    except Exception as e:
        return error_response(500, str(e))

def upscale_project(data):
    """Generate project upscaling recommendations"""
    project_id = data.get('projectId')
    current_scope = data.get('currentScope', '')
    goals = data.get('goals', [])
    
    # Get project details
    project = None
    if project_id:
        response = projects_table.get_item(Key={'projectId': project_id})
        project = response.get('Item', {})
    
    prompt = f"""You are an expert software architect and project manager. Analyze this project and provide detailed upscaling recommendations.

Current Project: {project.get('name', 'New Project') if project else 'New Project'}
Current Scope: {current_scope}
Goals: {', '.join(goals)}

Provide a comprehensive upscaling plan with:
1. Feature Expansion Ideas (5-7 new features)
2. Technical Improvements (architecture, performance, security)
3. Scalability Recommendations
4. Technology Stack Enhancements
5. Timeline Estimation (phases and milestones)
6. Resource Requirements (team size, skills needed)
7. Risk Assessment and Mitigation

Format as structured JSON with clear sections."""

    response = invoke_claude(prompt, max_tokens=3000)
    
    # Store recommendation
    recommendation_id = store_recommendation(project_id, 'upscale', response)
    
    return {
        'recommendationId': recommendation_id,
        'projectId': project_id,
        'type': 'upscale',
        'recommendations': response,
        'timestamp': datetime.utcnow().isoformat()
    }

def generate_code(data):
    """Generate code based on requirements"""
    language = data.get('language', 'python')
    framework = data.get('framework', '')
    requirements = data.get('requirements', '')
    context = data.get('context', '')
    
    prompt = f"""You are an expert software developer. Generate production-ready code based on these requirements.

Language: {language}
Framework: {framework}
Context: {context}

Requirements:
{requirements}

Generate:
1. Complete, working code with proper structure
2. Error handling and validation
3. Comments explaining key logic
4. Unit test examples
5. Usage documentation

Follow best practices for {language} and {framework}. Make the code modular, maintainable, and scalable."""

    code = invoke_claude(prompt, max_tokens=4000)
    
    return {
        'language': language,
        'framework': framework,
        'code': code,
        'timestamp': datetime.utcnow().isoformat()
    }

def suggest_architecture(data):
    """Suggest system architecture"""
    project_type = data.get('projectType', '')
    requirements = data.get('requirements', [])
    scale = data.get('scale', 'medium')  # small, medium, large, enterprise
    constraints = data.get('constraints', [])
    
    prompt = f"""You are a senior solutions architect. Design a comprehensive system architecture.

Project Type: {project_type}
Scale: {scale}
Requirements: {', '.join(requirements)}
Constraints: {', '.join(constraints)}

Provide:
1. High-Level Architecture Diagram (describe in text)
2. Technology Stack Recommendations
   - Frontend technologies
   - Backend technologies
   - Database choices
   - Infrastructure (cloud services)
   - DevOps tools
3. Component Breakdown
   - Microservices/modules
   - APIs and interfaces
   - Data flow
4. Scalability Strategy
5. Security Considerations
6. Cost Estimation
7. Deployment Strategy
8. Monitoring and Observability

Format as detailed, structured response with clear sections."""

    architecture = invoke_claude(prompt, max_tokens=3500)
    
    return {
        'projectType': project_type,
        'scale': scale,
        'architecture': architecture,
        'timestamp': datetime.utcnow().isoformat()
    }

def review_code(data):
    """Review code and provide feedback"""
    code = data.get('code', '')
    language = data.get('language', 'python')
    focus_areas = data.get('focusAreas', ['quality', 'security', 'performance'])
    
    prompt = f"""You are a senior code reviewer. Analyze this {language} code and provide detailed feedback.

Focus Areas: {', '.join(focus_areas)}

Code:
```{language}
{code}
```

Provide:
1. Code Quality Assessment (1-10 score)
2. Issues Found
   - Critical issues (security, bugs)
   - Major issues (performance, maintainability)
   - Minor issues (style, conventions)
3. Specific Recommendations
   - What to fix immediately
   - What to improve
   - Best practices to follow
4. Refactored Code Examples (for major issues)
5. Security Vulnerabilities (if any)
6. Performance Optimization Suggestions
7. Testing Recommendations

Be specific with line numbers and examples."""

    review = invoke_claude(prompt, max_tokens=3000)
    
    return {
        'language': language,
        'focusAreas': focus_areas,
        'review': review,
        'timestamp': datetime.utcnow().isoformat()
    }

def invoke_claude(prompt, max_tokens=2000):
    """Invoke Meta Llama 3 via Bedrock with proper instruction format"""
    # Format prompt for Llama 3 instruction format
    llama_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful AI assistant specialized in software development, architecture, and project management.<|eot_id|><|start_header_id|>user<|end_header_id|>

{prompt}<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    
    response = bedrock_runtime.invoke_model(
        modelId='meta.llama3-70b-instruct-v1:0',
        body=json.dumps({
            'prompt': llama_prompt,
            'max_gen_len': max_tokens,
            'temperature': 0.7,
            'top_p': 0.9
        })
    )
    
    result = json.loads(response['body'].read())
    return result.get('generation', '')

def store_recommendation(project_id, rec_type, content):
    """Store AI recommendation in DynamoDB"""
    import uuid
    
    recommendations_table = dynamodb.Table(os.environ.get('RECOMMENDATIONS_TABLE', 'ai-recommendations'))
    
    recommendation_id = str(uuid.uuid4())
    
    try:
        recommendations_table.put_item(
            Item={
                'recommendationId': recommendation_id,
                'projectId': project_id or 'general',
                'type': rec_type,
                'content': content,
                'createdAt': datetime.utcnow().isoformat()
            }
        )
    except Exception as e:
        print(f"Error storing recommendation: {e}")
    
    return recommendation_id

def success_response(data):
    """Return success response with CORS headers"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps(data)
    }

def error_response(status_code, message):
    """Return error response with CORS headers"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
        },
        'body': json.dumps({'error': message})
    }
