#!/usr/bin/env python3
"""
Seed the Memory Mapping system with sample data for demo purposes
"""
import boto3
import json
from datetime import datetime, timedelta
import uuid
import random
import os
from dotenv import load_dotenv
from opensearchpy import OpenSearch, RequestsHttpConnection

load_dotenv()

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
projects_table = dynamodb.Table('memory-projects')
decisions_table = dynamodb.Table('memory-decisions')

def seed_projects():
    """Create sample projects"""
    projects = [
        {
            'projectId': str(uuid.uuid4()),
            'name': 'Platform Rebuild',
            'status': 'active',
            'description': 'Complete rebuild of the core platform architecture',
            'members': ['alice@example.com', 'bob@example.com', 'charlie@example.com'],
            'progress': 65,
            'decisionCount': 8,
            'knowledgeItemCount': 24,
            'timeline': {
                'kickoff': '2024-01-15',
                'architecture_review': '2024-02-01',
                'api_dev': '2024-03-01',
                'audit': '2024-04-15',
                'deploy': '2024-05-01'
            },
            'createdAt': '2024-01-15T00:00:00Z',
            'updatedAt': datetime.now().isoformat()
        },
        {
            'projectId': str(uuid.uuid4()),
            'name': 'Mobile App',
            'status': 'planning',
            'description': 'Native mobile application for iOS and Android',
            'members': ['dave@example.com', 'eve@example.com'],
            'progress': 20,
            'decisionCount': 3,
            'knowledgeItemCount': 12,
            'timeline': {
                'kickoff': '2024-03-01',
                'design': '2024-03-15',
                'development': '2024-04-01',
                'testing': '2024-05-15',
                'launch': '2024-06-01'
            },
            'createdAt': '2024-03-01T00:00:00Z',
            'updatedAt': datetime.now().isoformat()
        },
        {
            'projectId': str(uuid.uuid4()),
            'name': 'Analytics Dashboard',
            'status': 'completed',
            'description': 'Real-time analytics and reporting dashboard',
            'members': ['frank@example.com', 'grace@example.com'],
            'progress': 100,
            'decisionCount': 5,
            'knowledgeItemCount': 18,
            'timeline': {
                'kickoff': '2023-11-01',
                'design': '2023-11-15',
                'development': '2023-12-01',
                'testing': '2024-01-01',
                'launch': '2024-01-15'
            },
            'createdAt': '2023-11-01T00:00:00Z',
            'updatedAt': '2024-01-15T00:00:00Z'
        }
    ]
    
    for project in projects:
        projects_table.put_item(Item=project)
        print(f"Created project: {project['name']}")
    
    return projects

def seed_decisions(projects):
    """Create sample decisions"""
    decisions = [
        {
            'decisionId': str(uuid.uuid4()),
            'projectId': projects[0]['projectId'],
            'projectName': 'Platform Rebuild',
            'title': 'Switch to Microservices Architecture',
            'description': 'After reviewing the monolithic architecture limitations, the team decided to migrate to a microservices-based approach for better scalability.',
            'people': ['alice@example.com', 'bob@example.com'],
            'timestamp': '2024-02-15T10:30:00Z',
            'sources': [
                {'type': 'Email Thread', 'url': 'https://mail.example.com/thread/123'},
                {'type': 'Slack Discussion', 'url': 'https://slack.example.com/archives/456'},
                {'type': 'Architecture Doc', 'url': 'https://docs.example.com/arch-decision'}
            ]
        },
        {
            'decisionId': str(uuid.uuid4()),
            'projectId': projects[0]['projectId'],
            'projectName': 'Platform Rebuild',
            'title': 'API Gateway Implementation',
            'description': 'Decided to use AWS API Gateway for centralized API management and rate limiting.',
            'people': ['charlie@example.com'],
            'timestamp': '2024-03-01T14:20:00Z',
            'sources': [
                {'type': 'GitHub PR', 'url': 'https://github.com/example/repo/pull/789'},
                {'type': 'Tech Spec', 'url': 'https://docs.example.com/api-gateway-spec'}
            ]
        },
        {
            'decisionId': str(uuid.uuid4()),
            'projectId': projects[0]['projectId'],
            'projectName': 'Platform Rebuild',
            'title': 'Feature X Delayed Due to Dependencies',
            'description': 'Feature X implementation was delayed by 2 weeks due to pending third-party API integration. Team decided to mock the API for testing.',
            'people': ['alice@example.com', 'bob@example.com'],
            'timestamp': '2024-03-15T09:00:00Z',
            'sources': [
                {'type': 'Email', 'url': 'https://mail.example.com/thread/456'},
                {'type': 'Slack', 'url': 'https://slack.example.com/archives/789'},
                {'type': 'Jira Ticket', 'url': 'https://jira.example.com/PROJ-123'}
            ]
        },
        {
            'decisionId': str(uuid.uuid4()),
            'projectId': projects[1]['projectId'],
            'projectName': 'Mobile App',
            'title': 'React Native vs Native Development',
            'description': 'After evaluating performance requirements and team expertise, decided to use React Native for cross-platform development.',
            'people': ['dave@example.com', 'eve@example.com'],
            'timestamp': '2024-03-10T11:00:00Z',
            'sources': [
                {'type': 'Meeting Notes', 'url': 'https://docs.example.com/meeting-notes-mobile'},
                {'type': 'Tech Evaluation', 'url': 'https://docs.example.com/tech-eval'}
            ]
        },
        {
            'decisionId': str(uuid.uuid4()),
            'projectId': projects[2]['projectId'],
            'projectName': 'Analytics Dashboard',
            'title': 'Real-time Data Pipeline Architecture',
            'description': 'Implemented Kafka-based streaming pipeline for real-time analytics processing.',
            'people': ['frank@example.com'],
            'timestamp': '2023-12-05T16:30:00Z',
            'sources': [
                {'type': 'Architecture Doc', 'url': 'https://docs.example.com/kafka-pipeline'},
                {'type': 'GitHub Commit', 'url': 'https://github.com/example/repo/commit/abc123'}
            ]
        }
    ]
    
    for decision in decisions:
        decisions_table.put_item(Item=decision)
        print(f"Created decision: {decision['title']}")

def seed_opensearch():
    """Add sample memory chunks to OpenSearch with embeddings"""
    opensearch_endpoint = os.getenv('OPENSEARCH_ENDPOINT')
    
    # Connect to OpenSearch
    os_client = OpenSearch(
        hosts=[{'host': opensearch_endpoint, 'port': 443}],
        http_auth=('admin', 'Admin123!'),
        use_ssl=True,
        verify_certs=True,
        connection_class=RequestsHttpConnection
    )
    
    # Sample memory chunks with mock embeddings
    chunks = [
        {
            'chunkId': str(uuid.uuid4()),
            'content': 'Feature X was delayed in March due to unexpected dependencies on the authentication service refactor. The team decided to prioritize security updates first.',
            'embedding': [random.random() for _ in range(1536)],
            'source': 'email',
            'sourceRef': 'email-thread-123',
            'projectId': 'platform-rebuild',
            'timestamp': '2024-03-15T10:30:00Z',
            'entities': ['Feature X', 'authentication service', 'security']
        },
        {
            'chunkId': str(uuid.uuid4()),
            'content': 'Team meeting notes: Discussed switching to microservices architecture. Alice proposed using API Gateway for better scalability.',
            'embedding': [random.random() for _ in range(1536)],
            'source': 'slack',
            'sourceRef': 'slack-channel-engineering',
            'projectId': 'platform-rebuild',
            'timestamp': '2024-02-10T14:00:00Z',
            'entities': ['microservices', 'API Gateway', 'Alice']
        },
        {
            'chunkId': str(uuid.uuid4()),
            'content': 'Commit message: Implemented API Gateway integration with Lambda functions. Added rate limiting and authentication middleware.',
            'embedding': [random.random() for _ in range(1536)],
            'source': 'github',
            'sourceRef': 'commit-abc123',
            'projectId': 'platform-rebuild',
            'timestamp': '2024-02-20T09:15:00Z',
            'entities': ['API Gateway', 'Lambda', 'rate limiting']
        },
        {
            'chunkId': str(uuid.uuid4()),
            'content': 'Architecture decision: Chose React Native over native development for mobile app to share code between iOS and Android.',
            'embedding': [random.random() for _ in range(1536)],
            'source': 'document',
            'sourceRef': 'doc-mobile-arch',
            'projectId': 'mobile-app',
            'timestamp': '2024-03-05T11:00:00Z',
            'entities': ['React Native', 'mobile', 'iOS', 'Android']
        },
        {
            'chunkId': str(uuid.uuid4()),
            'content': 'Analytics dashboard now uses real-time data pipeline with Kinesis and Lambda for processing. Dashboard updates every 5 seconds.',
            'embedding': [random.random() for _ in range(1536)],
            'source': 'document',
            'sourceRef': 'doc-analytics-design',
            'projectId': 'analytics-dashboard',
            'timestamp': '2023-12-10T16:30:00Z',
            'entities': ['Kinesis', 'Lambda', 'real-time', 'analytics']
        }
    ]
    
    for chunk in chunks:
        os_client.index(index='memory-chunks', body=chunk, id=chunk['chunkId'])
        print(f"Added memory chunk: {chunk['content'][:50]}...")
    
    print("\n✅ OpenSearch seeded with sample memory chunks!")

if __name__ == '__main__':
    print("Seeding sample data...")
    projects = seed_projects()
    seed_decisions(projects)
    seed_opensearch()
    print("\nSample data seeded successfully!")
    print("\nYou can now query: 'Why was Feature X delayed in March?'")
