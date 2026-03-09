# Testing Guide - Memory Mapping

## Test Strategy

### 1. Unit Tests (Backend)
Test individual Lambda functions in isolation.

### 2. Integration Tests
Test AWS service interactions (OpenSearch, Neptune, Bedrock).

### 3. End-to-End Tests
Test complete user workflows through the UI.

---

## Backend Testing

### Setup Test Environment
```bash
# Install test dependencies
pip install pytest pytest-mock boto3 moto

# Create test directory
mkdir -p backend/tests
```

### Test RAG Handler
```python
# backend/tests/test_rag_handler.py
import json
import pytest
from unittest.mock import Mock, patch
from backend.lambda.rag_handler import lambda_handler, generate_embedding

def test_lambda_handler_missing_query():
    event = {'body': json.dumps({})}
    response = lambda_handler(event, {})
    
    assert response['statusCode'] == 400
    assert 'error' in json.loads(response['body'])

@patch('backend.lambda.rag_handler.bedrock_runtime')
def test_generate_embedding(mock_bedrock):
    mock_bedrock.invoke_model.return_value = {
        'body': Mock(read=lambda: json.dumps({'embedding': [0.1, 0.2, 0.3]}))
    }
    
    result = generate_embedding("test text")
    assert len(result) == 3
    assert result == [0.1, 0.2, 0.3]

# Run tests
# pytest backend/tests/test_rag_handler.py -v
```

### Test Ingestion Handler
```python
# backend/tests/test_ingestion_handler.py
import pytest
from backend.lambda.ingestion_handler import chunk_text, extract_entities

def test_chunk_text():
    text = "word " * 200  # 200 words
    chunks = chunk_text(text, max_length=500)
    
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk) <= 500

def test_chunk_text_short():
    text = "short text"
    chunks = chunk_text(text, max_length=500)
    
    assert len(chunks) == 1
    assert chunks[0] == text

# Run tests
# pytest backend/tests/test_ingestion_handler.py -v
```

---

## Frontend Testing

### Setup Test Environment
```bash
cd frontend
npm install --save-dev @testing-library/react @testing-library/jest-dom
```

### Test Dashboard Component
```javascript
// frontend/src/components/__tests__/Dashboard.test.jsx
import { render, screen, waitFor } from '@testing-library/react';
import Dashboard from '../Dashboard';
import axios from 'axios';

jest.mock('axios');

test('renders dashboard with stats', async () => {
  axios.get.mockResolvedValue({
    data: {
      projects: [{ name: 'Test Project', status: 'active' }],
      decisions: []
    }
  });

  render(<Dashboard />);
  
  await waitFor(() => {
    expect(screen.getByText(/Memory Mapping Dashboard/i)).toBeInTheDocument();
  });
});

// Run tests
// npm test
```

### Test AskMemory Component
```javascript
// frontend/src/components/__tests__/AskMemory.test.jsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import AskMemory from '../AskMemory';
import axios from 'axios';

jest.mock('axios');

test('submits query and displays results', async () => {
  const mockResponse = {
    data: {
      answer: 'Test answer',
      sources: [],
      confidence: 85
    }
  };
  
  axios.post.mockResolvedValue(mockResponse);

  render(<AskMemory />);
  
  const input = screen.getByPlaceholderText(/Why was the API changed/i);
  const button = screen.getByText(/Search/i);
  
  fireEvent.change(input, { target: { value: 'test query' } });
  fireEvent.click(button);
  
  await waitFor(() => {
    expect(screen.getByText('Test answer')).toBeInTheDocument();
    expect(screen.getByText('85%')).toBeInTheDocument();
  });
});
```

---

## Integration Testing

### Test OpenSearch Integration
```python
# backend/tests/test_opensearch_integration.py
import pytest
from opensearchpy import OpenSearch
import os

@pytest.fixture
def opensearch_client():
    # Use local OpenSearch for testing
    return OpenSearch(
        hosts=[{'host': 'localhost', 'port': 9200}],
        use_ssl=False
    )

def test_index_document(opensearch_client):
    doc = {
        'chunkId': 'test-123',
        'content': 'test content',
        'embedding': [0.1] * 1536
    }
    
    response = opensearch_client.index(
        index='memory-chunks-test',
        id='test-123',
        body=doc
    )
    
    assert response['result'] == 'created'

def test_search_documents(opensearch_client):
    query = {
        'query': {
            'match': {
                'content': 'test'
            }
        }
    }
    
    response = opensearch_client.search(
        index='memory-chunks-test',
        body=query
    )
    
    assert response['hits']['total']['value'] > 0
```

### Test DynamoDB Integration
```python
# backend/tests/test_dynamodb_integration.py
import boto3
import pytest
from moto import mock_dynamodb

@mock_dynamodb
def test_create_project():
    dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
    
    # Create test table
    table = dynamodb.create_table(
        TableName='memory-projects-test',
        KeySchema=[{'AttributeName': 'projectId', 'KeyType': 'HASH'}],
        AttributeDefinitions=[{'AttributeName': 'projectId', 'AttributeType': 'S'}],
        BillingMode='PAY_PER_REQUEST'
    )
    
    # Insert item
    table.put_item(Item={
        'projectId': 'test-123',
        'name': 'Test Project',
        'status': 'active'
    })
    
    # Retrieve item
    response = table.get_item(Key={'projectId': 'test-123'})
    assert response['Item']['name'] == 'Test Project'
```

---

## End-to-End Testing

### Setup Cypress
```bash
cd frontend
npm install --save-dev cypress
npx cypress open
```

### E2E Test: Complete User Flow
```javascript
// frontend/cypress/e2e/user_flow.cy.js
describe('Memory Mapping User Flow', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000');
  });

  it('navigates through all views', () => {
    // Dashboard
    cy.contains('Memory Mapping Dashboard').should('be.visible');
    cy.contains('Active Projects').should('be.visible');
    
    // Projects
    cy.contains('Projects').click();
    cy.url().should('include', '/projects');
    cy.contains('Platform Rebuild').should('be.visible');
    
    // Ask Memory
    cy.contains('Ask Memory').click();
    cy.url().should('include', '/ask');
    cy.get('input[placeholder*="Why was"]').should('be.visible');
    
    // Knowledge Graph
    cy.contains('Knowledge Graph').click();
    cy.url().should('include', '/graph');
    
    // Decision Timeline
    cy.contains('Decision Timeline').click();
    cy.url().should('include', '/timeline');
  });

  it('performs a search query', () => {
    cy.contains('Ask Memory').click();
    
    cy.get('input[placeholder*="Why was"]')
      .type('Why was Feature X delayed?');
    
    cy.contains('Search').click();
    
    cy.contains('Answer', { timeout: 10000 }).should('be.visible');
    cy.contains('Confidence').should('be.visible');
    cy.contains('Source References').should('be.visible');
  });

  it('filters projects', () => {
    cy.contains('Projects').click();
    
    cy.contains('Active').click();
    cy.contains('Platform Rebuild').should('be.visible');
    
    cy.contains('Completed').click();
    cy.contains('Analytics Dashboard').should('be.visible');
  });
});
```

---

## Load Testing

### Setup Artillery
```bash
npm install -g artillery
```

### Load Test Configuration
```yaml
# load-test.yml
config:
  target: 'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod'
  phases:
    - duration: 60
      arrivalRate: 10
      name: "Warm up"
    - duration: 120
      arrivalRate: 50
      name: "Sustained load"
  
scenarios:
  - name: "Query Memory"
    flow:
      - post:
          url: "/query"
          json:
            query: "Why was Feature X delayed?"
      
  - name: "List Projects"
    flow:
      - get:
          url: "/projects"
      
  - name: "Get Decisions"
    flow:
      - get:
          url: "/decisions"
```

### Run Load Test
```bash
artillery run load-test.yml
```

---

## Manual Testing Checklist

### Backend APIs
- [ ] POST /query with valid query returns answer
- [ ] POST /query with empty query returns 400
- [ ] GET /projects returns list of projects
- [ ] POST /projects creates new project
- [ ] GET /decisions with filters works
- [ ] POST /ingest processes data correctly
- [ ] POST /graph returns graph data

### Frontend
- [ ] Dashboard loads with correct stats
- [ ] Project timeline displays correctly
- [ ] Projects view filters work
- [ ] Ask Memory search returns results
- [ ] Source references are clickable
- [ ] Knowledge graph renders
- [ ] Decision timeline shows chronological order
- [ ] Navigation between views works

### Integration
- [ ] Query returns sources from OpenSearch
- [ ] Graph data comes from Neptune
- [ ] Ingestion creates embeddings
- [ ] Entities are extracted correctly
- [ ] Confidence scores are reasonable

---

## Performance Benchmarks

### Target Metrics
- Query response time: < 3 seconds
- Page load time: < 2 seconds
- API response time: < 1 second
- Embedding generation: < 500ms
- Graph query: < 1 second

### Monitoring
```bash
# CloudWatch Logs
aws logs tail /aws/lambda/MemoryMappingRAGHandler --follow

# API Gateway metrics
aws cloudwatch get-metric-statistics \
  --namespace AWS/ApiGateway \
  --metric-name Latency \
  --dimensions Name=ApiName,Value=MemoryMappingAPI \
  --start-time 2024-03-20T00:00:00Z \
  --end-time 2024-03-20T23:59:59Z \
  --period 3600 \
  --statistics Average
```

---

## CI/CD Testing Pipeline

### GitHub Actions Workflow
```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-mock
      - run: pytest backend/tests/ -v

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-node@v2
        with:
          node-version: '18'
      - run: cd frontend && npm install
      - run: cd frontend && npm test
```

---

## Test Data

### Sample Query Inputs
```
"Why was Feature X delayed in March?"
"What decisions were made about the API?"
"Who was involved in the microservices decision?"
"Show me all GitHub commits related to Platform Rebuild"
"What was discussed in the architecture review?"
```

### Expected Outputs
Each query should return:
- Relevant answer text
- 3-5 source references
- Confidence score 70-95%
- Related graph nodes

---

**Run All Tests:**
```bash
# Backend
pytest backend/tests/ -v --cov

# Frontend
cd frontend && npm test -- --coverage

# E2E
cd frontend && npx cypress run

# Load
artillery run load-test.yml
```
