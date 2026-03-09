import json
import boto3
import os
from datetime import datetime
import uuid

comprehend = boto3.client('comprehend', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
dynamodb = boto3.resource('dynamodb', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
s3 = boto3.client('s3', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
sqs = boto3.client('sqs', region_name=os.environ.get('AWS_REGION', 'us-east-1'))

metadata_table = dynamodb.Table(os.environ.get('METADATA_TABLE', 'memory-metadata'))
opensearch_endpoint = os.environ.get('OPENSEARCH_ENDPOINT')

def lambda_handler(event, context):
    """Ingest data from multiple sources: email, slack, github, documents"""
    
    # Handle SQS batch
    if 'Records' in event:
        for record in event['Records']:
            process_record(record)
        return {'statusCode': 200, 'body': json.dumps({'processed': len(event['Records'])})}
    
    # Handle direct API call
    body = json.loads(event.get('body', '{}'))
    source_type = body.get('sourceType')  # email, slack, github, document
    content = body.get('content')
    metadata = body.get('metadata', {})
    
    try:
        result = ingest_content(source_type, content, metadata)
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps(result)
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

def process_record(record):
    """Process individual SQS record"""
    body = json.loads(record['body'])
    ingest_content(body['sourceType'], body['content'], body.get('metadata', {}))

def ingest_content(source_type, content, metadata):
    """Main ingestion pipeline"""
    chunk_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    # Step 1: Extract entities using Comprehend
    entities = extract_entities(content)
    
    # Step 2: Chunk text if needed
    chunks = chunk_text(content, max_length=500)
    
    # Step 3: Generate embeddings and store in OpenSearch
    chunk_ids = []
    for chunk in chunks:
        embedding = generate_embedding(chunk)
        chunk_id = store_in_opensearch(chunk, embedding, source_type, metadata, entities, timestamp)
        chunk_ids.append(chunk_id)
    
    # Step 4: Store metadata in DynamoDB
    store_metadata(chunk_ids, source_type, metadata, entities, timestamp)
    
    # Step 5: Update knowledge graph in Neptune (async via SQS)
    queue_graph_update(entities, metadata, timestamp)
    
    return {
        'chunkIds': chunk_ids,
        'entities': entities,
        'timestamp': timestamp
    }

def extract_entities(text):
    """Extract named entities using Amazon Comprehend"""
    try:
        response = comprehend.detect_entities(Text=text[:5000], LanguageCode='en')
        entities = []
        for entity in response['Entities']:
            if entity['Score'] > 0.7:  # Confidence threshold
                entities.append({
                    'text': entity['Text'],
                    'type': entity['Type'],
                    'score': entity['Score']
                })
        return entities
    except Exception as e:
        print(f"Entity extraction error: {e}")
        return []

def chunk_text(text, max_length=500):
    """Split text into chunks"""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0
    
    for word in words:
        if current_length + len(word) > max_length and current_chunk:
            chunks.append(' '.join(current_chunk))
            current_chunk = [word]
            current_length = len(word)
        else:
            current_chunk.append(word)
            current_length += len(word) + 1
    
    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks if chunks else [text]

def generate_embedding(text):
    """Generate embeddings using Bedrock Titan"""
    response = bedrock_runtime.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({'inputText': text})
    )
    result = json.loads(response['body'].read())
    return result['embedding']

def store_in_opensearch(content, embedding, source_type, metadata, entities, timestamp):
    """Store chunk in OpenSearch with vector embedding"""
    from opensearchpy import OpenSearch, RequestsHttpConnection
    from requests_aws4auth import AWS4Auth
    
    credentials = boto3.Session().get_credentials()
    awsauth = AWS4Auth(
        credentials.access_key,
        credentials.secret_key,
        os.environ.get('AWS_REGION', 'us-east-1'),
        'es',
        session_token=credentials.token
    )
    
    os_client = OpenSearch(
        hosts=[{'host': opensearch_endpoint, 'port': 443}],
        http_auth=awsauth,
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    chunk_id = str(uuid.uuid4())
    document = {
        'chunkId': chunk_id,
        'content': content,
        'embedding': embedding,
        'source': source_type,
        'sourceRef': metadata.get('sourceRef', ''),
        'projectId': metadata.get('projectId', ''),
        'timestamp': timestamp,
        'entities': [e['text'] for e in entities]
    }
    
    os_client.index(index='memory-chunks', id=chunk_id, body=document)
    return chunk_id

def store_metadata(chunk_ids, source_type, metadata, entities, timestamp):
    """Store metadata in DynamoDB"""
    item = {
        'entityId': str(uuid.uuid4()),
        'type': 'Artifact',
        'source': source_type,
        'chunkIds': chunk_ids,
        'metadata': metadata,
        'entities': entities,
        'createdAt': timestamp
    }
    metadata_table.put_item(Item=item)

def queue_graph_update(entities, metadata, timestamp):
    """Queue graph update for Neptune"""
    queue_url = os.environ.get('GRAPH_UPDATE_QUEUE')
    if queue_url:
        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps({
                'entities': entities,
                'metadata': metadata,
                'timestamp': timestamp
            })
        )