import json
import boto3
import os
from gremlin_python.driver import client, serializer

neptune_endpoint = os.environ.get('NEPTUNE_ENDPOINT')
neptune_port = os.environ.get('NEPTUNE_PORT', '8182')

def lambda_handler(event, context):
    """Handle knowledge graph queries"""
    body = json.loads(event.get('body', '{}'))
    node_id = body.get('nodeId')
    query_type = body.get('queryType', 'neighbors')  # neighbors, path, subgraph
    
    try:
        gremlin_client = get_gremlin_client()
        
        if query_type == 'neighbors':
            result = get_neighbors(gremlin_client, node_id)
        elif query_type == 'path':
            target_id = body.get('targetId')
            result = find_path(gremlin_client, node_id, target_id)
        else:
            result = get_subgraph(gremlin_client, node_id)
        
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

def get_gremlin_client():
    """Initialize Gremlin client for Neptune"""
    endpoint = f'wss://{neptune_endpoint}:{neptune_port}/gremlin'
    return client.Client(
        endpoint,
        'g',
        message_serializer=serializer.GraphSONSerializersV2d0()
    )

def get_neighbors(gremlin_client, node_id):
    """Get all connected nodes"""
    query = f"""
    g.V('{node_id}')
      .bothE()
      .project('edge', 'node')
      .by(valueMap(true))
      .by(otherV().valueMap(true))
      .limit(50)
    """
    results = gremlin_client.submit(query).all().result()
    
    nodes = []
    edges = []
    for result in results:
        edges.append(result['edge'])
        nodes.append(result['node'])
    
    return {'nodes': nodes, 'edges': edges}

def find_path(gremlin_client, source_id, target_id):
    """Find shortest path between two nodes"""
    query = f"""
    g.V('{source_id}')
      .repeat(bothE().otherV().simplePath())
      .until(hasId('{target_id}'))
      .path()
      .limit(1)
    """
    results = gremlin_client.submit(query).all().result()
    return {'path': results[0] if results else []}

def get_subgraph(gremlin_client, node_id, depth=2):
    """Get subgraph around a node"""
    query = f"""
    g.V('{node_id}')
      .repeat(bothE().otherV().simplePath())
      .times({depth})
      .path()
      .limit(100)
    """
    results = gremlin_client.submit(query).all().result()
    return {'subgraph': results}
