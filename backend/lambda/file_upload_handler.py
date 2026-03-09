import json
import boto3
import os
import base64
from datetime import datetime
import uuid

s3_client = boto3.client('s3', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

BUCKET_NAME = os.environ.get('DOCUMENTS_BUCKET', 'memory-mapping-documents')
METADATA_TABLE = os.environ.get('METADATA_TABLE', 'memory-metadata')

metadata_table = dynamodb.Table(METADATA_TABLE)

def lambda_handler(event, context):
    """Handle file uploads to S3"""
    http_method = event.get('httpMethod', 'GET')
    path_params = event.get('pathParameters', {})
    
    try:
        if http_method == 'POST':
            # Upload file
            body = json.loads(event.get('body', '{}'))
            result = upload_file(body)
        elif http_method == 'GET':
            if path_params and 'projectId' in path_params:
                # List files for a project
                result = list_project_files(path_params['projectId'])
            else:
                # List all files
                result = list_all_files()
        elif http_method == 'DELETE':
            # Delete file
            if path_params and 'fileId' in path_params:
                result = delete_file(path_params['fileId'])
            else:
                return error_response(400, 'File ID is required')
        else:
            return error_response(405, 'Method not allowed')
        
        return success_response(result)
    except Exception as e:
        print(f"Error: {str(e)}")
        return error_response(500, str(e))

def upload_file(data):
    """Upload file to S3 and store metadata"""
    file_id = str(uuid.uuid4())
    project_id = data.get('projectId')
    file_name = data.get('fileName')
    file_content = data.get('fileContent')  # Base64 encoded
    file_type = data.get('fileType', 'application/octet-stream')
    description = data.get('description', '')
    
    if not all([project_id, file_name, file_content]):
        raise ValueError('projectId, fileName, and fileContent are required')
    
    # Decode base64 content
    try:
        file_bytes = base64.b64decode(file_content)
    except Exception as e:
        raise ValueError(f'Invalid base64 content: {str(e)}')
    
    # Generate S3 key
    s3_key = f"projects/{project_id}/{file_id}/{file_name}"
    
    # Upload to S3
    s3_client.put_object(
        Bucket=BUCKET_NAME,
        Key=s3_key,
        Body=file_bytes,
        ContentType=file_type,
        Metadata={
            'project-id': project_id,
            'file-id': file_id,
            'original-name': file_name
        }
    )
    
    # Generate presigned URL for download (valid for 1 hour)
    download_url = s3_client.generate_presigned_url(
        'get_object',
        Params={'Bucket': BUCKET_NAME, 'Key': s3_key},
        ExpiresIn=3600
    )
    
    # Store metadata in DynamoDB
    metadata = {
        'entityId': file_id,
        'entityType': 'file',
        'projectId': project_id,
        'fileName': file_name,
        'fileType': file_type,
        'fileSize': len(file_bytes),
        's3Key': s3_key,
        's3Bucket': BUCKET_NAME,
        'description': description,
        'uploadedAt': datetime.utcnow().isoformat(),
        'downloadUrl': download_url
    }
    
    metadata_table.put_item(Item=metadata)
    
    return {
        'fileId': file_id,
        'fileName': file_name,
        'fileSize': len(file_bytes),
        'downloadUrl': download_url,
        'uploadedAt': metadata['uploadedAt']
    }

def list_project_files(project_id):
    """List all files for a specific project"""
    response = metadata_table.scan(
        FilterExpression='projectId = :pid AND entityType = :type',
        ExpressionAttributeValues={
            ':pid': project_id,
            ':type': 'file'
        }
    )
    
    files = response.get('Items', [])
    
    # Generate fresh presigned URLs
    for file in files:
        if 's3Key' in file and 's3Bucket' in file:
            try:
                file['downloadUrl'] = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': file['s3Bucket'], 'Key': file['s3Key']},
                    ExpiresIn=3600
                )
            except Exception as e:
                print(f"Error generating URL for {file.get('fileName')}: {str(e)}")
                file['downloadUrl'] = None
    
    return {'files': files, 'count': len(files)}

def list_all_files():
    """List all files across all projects"""
    response = metadata_table.scan(
        FilterExpression='entityType = :type',
        ExpressionAttributeValues={':type': 'file'}
    )
    
    files = response.get('Items', [])
    
    # Generate fresh presigned URLs
    for file in files:
        if 's3Key' in file and 's3Bucket' in file:
            try:
                file['downloadUrl'] = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': file['s3Bucket'], 'Key': file['s3Key']},
                    ExpiresIn=3600
                )
            except Exception as e:
                print(f"Error generating URL for {file.get('fileName')}: {str(e)}")
                file['downloadUrl'] = None
    
    return {'files': files, 'count': len(files)}

def delete_file(file_id):
    """Delete file from S3 and metadata"""
    # Get file metadata
    response = metadata_table.get_item(Key={'entityId': file_id})
    file_metadata = response.get('Item')
    
    if not file_metadata:
        raise ValueError('File not found')
    
    # Delete from S3
    if 's3Key' in file_metadata and 's3Bucket' in file_metadata:
        s3_client.delete_object(
            Bucket=file_metadata['s3Bucket'],
            Key=file_metadata['s3Key']
        )
    
    # Delete metadata
    metadata_table.delete_item(Key={'entityId': file_id})
    
    return {
        'message': 'File deleted successfully',
        'fileId': file_id,
        'fileName': file_metadata.get('fileName')
    }

def success_response(data):
    """Return success response"""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,DELETE,OPTIONS'
        },
        'body': json.dumps(data)
    }

def error_response(status_code, message):
    """Return error response"""
    return {
        'statusCode': status_code,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
            'Access-Control-Allow-Methods': 'GET,POST,DELETE,OPTIONS'
        },
        'body': json.dumps({'error': message})
    }
