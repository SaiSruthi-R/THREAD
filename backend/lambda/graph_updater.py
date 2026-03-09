import json
import os
from gremlin_python.driver import client, serializer

neptune_endpoint = os.environ.get('NEPTUNE_ENDPOINT')
neptune_port = os.environ.get('NEPTUNE_PORT', '8182')

def lambda_handler(event, context):
    """Update Neptune knowledge graph with new entities and relationships"""
    
    gremlin_client = get_gremlin_client()
    
    for record in event.get('Records', []):
        body = json.loads(record['body'])
        entities = body.get('entities', [])
        metadata = body.get('metadata', {})
        
        # Create nodes for entities
        for entity in entities:
            create_entity_node(gremlin_client, entity, metadata)
        
        # Create relationships
        create_relationships(gremlin_client, entities, metadata)
    
    return {'statusCode': 200, 'body': json.dumps({'message': 'Graph updated'})}

def get_gremlin_client():
    """Initialize Gremlin client"""
    endpoint = f'wss://{neptune_endpoint}:{neptune_port}/gremlin'
    return client.Client(
        endpoint,
        'g',
        message_serializer=serializer.GraphSONSerializersV2d0()
    )

def create_entity_node(gremlin_client, entity, metadata):
    """Create or update entity node in Neptune"""
    query = f"""
    g.V().has('name', '{entity['text']}').fold()
      .coalesce(
        unfold(),
        addV('{entity['type']}')
          .property('name', '{entity['text']}')
          .property('score', {entity['score']})
      )
    """
    gremlin_client.submit(query).all().result()

def create_relationships(gremlin_client, entities, metadata):
    """Create relationships between entities"""
    project_id = metadata.get('projectId')
    
    if project_id and entities:
        # Link entities to project
        for entity in entities:
            query = f"""
            g.V().has('projectId', '{project_id}').as('project')
              .V().has('name', '{entity['text']}').as('entity')
              .addE('related_to').from('entity').to('project')
            """
            try:
                gremlin_client.submit(query).all().result()
            except Exception as e:
                print(f"Error creating relationship: {e}")
