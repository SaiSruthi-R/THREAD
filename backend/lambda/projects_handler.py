import json
import boto3
import os
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
projects_table = dynamodb.Table(os.environ.get('PROJECTS_TABLE', 'memory-projects'))

def lambda_handler(event, context):
    """Handle project CRUD operations"""
    http_method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters', {})
    
    try:
        if http_method == 'GET':
            if path_params and 'id' in path_params:
                result = get_project(path_params['id'])
            else:
                result = list_projects()
        elif http_method == 'POST':
            body = json.loads(event.get('body', '{}'))
            result = create_project(body)
        elif http_method == 'PUT':
            body = json.loads(event.get('body', '{}'))
            result = update_project(path_params['id'], body)
        elif http_method == 'DELETE':
            result = delete_project(path_params['id'])
        else:
            return {'statusCode': 405, 'body': json.dumps({'error': 'Method not allowed'})}
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps(result, default=decimal_default)
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({'error': str(e)})
        }

def list_projects():
    """List all projects"""
    response = projects_table.scan()
    return {'projects': response.get('Items', [])}

def get_project(project_id):
    """Get project details"""
    response = projects_table.get_item(Key={'projectId': project_id})
    return response.get('Item', {})

def create_project(data):
    """Create new project"""
    import uuid
    project_id = str(uuid.uuid4())
    
    item = {
        'projectId': project_id,
        'name': data['name'],
        'status': data.get('status', 'planning'),
        'description': data.get('description', ''),
        'members': data.get('members', []),
        'timeline': data.get('timeline', {}),
        'decisionCount': 0,
        'knowledgeItemCount': 0,
        'createdAt': datetime.utcnow().isoformat(),
        'updatedAt': datetime.utcnow().isoformat()
    }
    
    projects_table.put_item(Item=item)
    return item

def update_project(project_id, data):
    """Update project"""
    update_expr = 'SET updatedAt = :updated'
    expr_values = {':updated': datetime.utcnow().isoformat()}
    
    if 'status' in data:
        update_expr += ', #status = :status'
        expr_values[':status'] = data['status']
    
    if 'timeline' in data:
        update_expr += ', timeline = :timeline'
        expr_values[':timeline'] = data['timeline']
    
    response = projects_table.update_item(
        Key={'projectId': project_id},
        UpdateExpression=update_expr,
        ExpressionAttributeValues=expr_values,
        ExpressionAttributeNames={'#status': 'status'} if 'status' in data else {},
        ReturnValues='ALL_NEW'
    )
    
    return response.get('Attributes', {})

def delete_project(project_id):
    """Delete project"""
    projects_table.delete_item(Key={'projectId': project_id})
    return {'message': 'Project deleted successfully', 'projectId': project_id}

def decimal_default(obj):
    """JSON serializer for Decimal"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError
