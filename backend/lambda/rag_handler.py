import json
import boto3
import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth

bedrock_runtime = boto3.client('bedrock-runtime', region_name=os.environ.get('AWS_REGION', 'us-east-1'))
neptune_endpoint = os.environ.get('NEPTUNE_ENDPOINT')
opensearch_endpoint = os.environ.get('OPENSEARCH_ENDPOINT')

def lambda_handler(event, context):
    """Main RAG handler for natural language queries"""
    body = json.loads(event.get('body', '{}'))
    query = body.get('query', '')
    
    if not query:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({'error': 'Query is required'})
        }
    
    try:
        # Step 1: Generate query embedding
        query_embedding = generate_embedding(query)
        
        # Step 2: Semantic search in OpenSearch
        semantic_results = search_opensearch(query_embedding)
        
        # Step 3: Get graph context from Neptune
        graph_context = get_graph_context(semantic_results)
        
        # Step 4: Generate answer with Bedrock Claude
        answer = generate_answer(query, semantic_results, graph_context)
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS'
            },
            'body': json.dumps({
                'answer': answer['text'],
                'sources': answer['sources'],
                'confidence': answer['confidence'],
                'graphNodes': graph_context
            })
        }
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
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

def generate_embedding(text):
    """Generate embeddings using Bedrock Titan"""
    response = bedrock_runtime.invoke_model(
        modelId='amazon.titan-embed-text-v1',
        body=json.dumps({'inputText': text})
    )
    result = json.loads(response['body'].read())
    return result['embedding']

def search_opensearch(query_vector):
    """Perform k-NN search in OpenSearch"""
    # Use basic auth with master credentials for fine-grained access control
    os_client = OpenSearch(
        hosts=[{'host': opensearch_endpoint, 'port': 443}],
        http_auth=('admin', 'Admin123!'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection,
        timeout=30  # Increase timeout to 30 seconds
    )
    
    search_body = {
        'size': 5,
        'query': {
            'knn': {
                'embedding': {
                    'vector': query_vector,
                    'k': 5
                }
            }
        }
    }
    
    results = os_client.search(index='memory-chunks', body=search_body)
    return results['hits']['hits']

def get_graph_context(semantic_results):
    """Query Neptune for related entities"""
    # Extract entity IDs from semantic results
    entity_ids = []
    for hit in semantic_results:
        entities = hit['_source'].get('entities', [])
        entity_ids.extend(entities)
    
    # In production, use Gremlin to query Neptune
    # For now, return mock graph context
    return {
        'nodes': entity_ids[:10],
        'relationships': []
    }

def generate_answer(query, semantic_results, graph_context):
    """Generate grounded answer using Bedrock Claude"""
    # Build context from results
    context_parts = []
    sources = []
    
    for idx, hit in enumerate(semantic_results):
        source = hit['_source']
        context_parts.append(f"[{idx+1}] {source['content']}")
        sources.append({
            'id': hit['_id'],
            'type': source['source'],
            'reference': source.get('sourceRef', ''),
            'timestamp': source.get('timestamp', ''),
            'score': hit['_score']
        })
    
    context = '\n\n'.join(context_parts)
    
    # Format prompt for Llama 3 instruction format
    llama_prompt = f"""<|begin_of_text|><|start_header_id|>system<|end_header_id|>

You are a helpful AI assistant that answers questions based on provided context. Always cite your sources using [1], [2], etc.<|eot_id|><|start_header_id|>user<|end_header_id|>

Context:
{context}

Question: {query}

Provide a clear answer with references to the source numbers [1], [2], etc. If the context doesn't contain enough information, say so.<|eot_id|><|start_header_id|>assistant<|end_header_id|>

"""
    
    response = bedrock_runtime.invoke_model(
        modelId='meta.llama3-70b-instruct-v1:0',
        body=json.dumps({
            'prompt': llama_prompt,
            'max_gen_len': 1000,
            'temperature': 0.7,
            'top_p': 0.9
        })
    )
    
    result = json.loads(response['body'].read())
    print(f"Bedrock response: {result}")  # Debug logging
    answer_text = result.get('generation', '')
    
    # Calculate confidence based on semantic scores
    avg_score = sum(hit['_score'] for hit in semantic_results) / len(semantic_results) if semantic_results else 0
    confidence = min(int(avg_score * 100), 95)
    
    return {
        'text': answer_text,
        'sources': sources,
        'confidence': confidence
    }
