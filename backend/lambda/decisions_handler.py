import json
import boto3
import os
from datetime import datetime

dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
decisions_table = dynamodb.Table(os.environ.get('DECISIONS_TABLE', 'memory-decisions'))

def lambda_handler(event, context):
    """Handle decision timeline queries"""
    query_params = event.get('queryStringParameters', {}) or {}
    project_id = query_params.get('projectId')
    start_date = query_params.get('startDate')
    end_date = query_params.get('endDate')
    
    try:
        decisions = get_decisions(project_id, start_date, end_date)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({'decisions': decisions})
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

def get_decisions(project_id=None, start_date=None, end_date=None):
    """Query decisions with filters"""
    if project_id:
        response = decisions_table.query(
            IndexName='ProjectIndex',
            KeyConditionExpression='projectId = :pid',
            ExpressionAttributeValues={':pid': project_id}
        )
    else:
        response = decisions_table.scan()
    
    decisions = response.get('Items', [])
    
    # Filter by date range if provided
    if start_date or end_date:
        decisions = [
            d for d in decisions
            if (not start_date or d.get('timestamp', '') >= start_date) and
               (not end_date or d.get('timestamp', '') <= end_date)
        ]
    
    # Sort by timestamp descending
    decisions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    return decisions
