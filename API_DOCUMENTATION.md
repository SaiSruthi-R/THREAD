# Memory Mapping API Documentation

Base URL: `https://your-api-id.execute-api.us-east-1.amazonaws.com/prod`

## Authentication
Currently using AWS IAM authentication. Future versions will use Cognito JWT tokens.

---

## Endpoints

### 1. Query Memory (RAG)

**POST** `/query`

Natural language query interface using RAG (Retrieval Augmented Generation).

**Request Body:**
```json
{
  "query": "Why was Feature X delayed in March?"
}
```

**Response:**
```json
{
  "answer": "Feature X was delayed by 2 weeks in March due to pending third-party API integration. The team decided to mock the API for testing purposes...",
  "sources": [
    {
      "id": "chunk-123",
      "type": "email",
      "reference": "https://mail.example.com/thread/456",
      "timestamp": "2024-03-15T09:00:00Z",
      "score": 0.89
    },
    {
      "id": "chunk-456",
      "type": "slack",
      "reference": "https://slack.example.com/archives/789",
      "timestamp": "2024-03-15T10:30:00Z",
      "score": 0.85
    }
  ],
  "confidence": 87,
  "graphNodes": {
    "nodes": ["entity-1", "entity-2"],
    "relationships": []
  }
}
```

**Process Flow:**
1. Generate query embedding using Bedrock Titan
2. Perform k-NN search in OpenSearch (top 5 results)
3. Query Neptune for related entities
4. Generate grounded answer using Bedrock Claude
5. Return answer with sources and confidence score

---

### 2. Projects

#### List All Projects
**GET** `/projects`

**Response:**
```json
{
  "projects": [
    {
      "projectId": "uuid",
      "name": "Platform Rebuild",
      "status": "active",
      "description": "Complete rebuild of the core platform",
      "members": ["alice@example.com", "bob@example.com"],
      "progress": 65,
      "decisionCount": 8,
      "knowledgeItemCount": 24,
      "timeline": {
        "kickoff": "2024-01-15",
        "architecture_review": "2024-02-01",
        "api_dev": "2024-03-01"
      },
      "createdAt": "2024-01-15T00:00:00Z",
      "updatedAt": "2024-03-20T10:30:00Z"
    }
  ]
}
```

#### Get Project Details
**GET** `/projects/{id}`

**Response:**
```json
{
  "projectId": "uuid",
  "name": "Platform Rebuild",
  "status": "active",
  "description": "Complete rebuild of the core platform",
  "members": ["alice@example.com", "bob@example.com"],
  "progress": 65,
  "decisionCount": 8,
  "knowledgeItemCount": 24,
  "timeline": {...},
  "createdAt": "2024-01-15T00:00:00Z",
  "updatedAt": "2024-03-20T10:30:00Z"
}
```

#### Create Project
**POST** `/projects`

**Request Body:**
```json
{
  "name": "New Project",
  "status": "planning",
  "description": "Project description",
  "members": ["user@example.com"],
  "timeline": {
    "kickoff": "2024-04-01",
    "completion": "2024-06-01"
  }
}
```

**Response:**
```json
{
  "projectId": "new-uuid",
  "name": "New Project",
  "status": "planning",
  ...
}
```

#### Update Project
**PUT** `/projects/{id}`

**Request Body:**
```json
{
  "status": "active",
  "progress": 75,
  "timeline": {...}
}
```

---

### 3. Decisions

#### List Decisions
**GET** `/decisions?projectId={id}&startDate={date}&endDate={date}`

**Query Parameters:**
- `projectId` (optional): Filter by project
- `startDate` (optional): ISO 8601 date
- `endDate` (optional): ISO 8601 date

**Response:**
```json
{
  "decisions": [
    {
      "decisionId": "uuid",
      "projectId": "project-uuid",
      "projectName": "Platform Rebuild",
      "title": "Switch to Microservices Architecture",
      "description": "After reviewing limitations...",
      "people": ["alice@example.com", "bob@example.com"],
      "timestamp": "2024-02-15T10:30:00Z",
      "sources": [
        {
          "type": "Email Thread",
          "url": "https://mail.example.com/thread/123"
        }
      ]
    }
  ]
}
```

---

### 4. Knowledge Graph

**POST** `/graph`

Query the knowledge graph for relationships.

**Request Body:**
```json
{
  "nodeId": "entity-123",
  "queryType": "neighbors"  // or "path", "subgraph"
}
```

For path queries:
```json
{
  "nodeId": "entity-123",
  "targetId": "entity-456",
  "queryType": "path"
}
```

**Response (neighbors):**
```json
{
  "nodes": [
    {
      "id": "entity-1",
      "label": "Alice",
      "type": "Person",
      "properties": {...}
    }
  ],
  "edges": [
    {
      "id": "edge-1",
      "from": "entity-123",
      "to": "entity-1",
      "label": "made_decision",
      "properties": {...}
    }
  ]
}
```

**Response (path):**
```json
{
  "path": [
    {"type": "vertex", "id": "entity-123", "label": "Project A"},
    {"type": "edge", "label": "has_decision"},
    {"type": "vertex", "id": "entity-456", "label": "Decision X"}
  ]
}
```

---

### 5. Data Ingestion

**POST** `/ingest`

Ingest new data into the system.

**Request Body:**
```json
{
  "sourceType": "email",  // email, slack, github, document
  "content": "Email body or document content...",
  "metadata": {
    "sourceRef": "https://mail.example.com/thread/789",
    "projectId": "project-uuid",
    "author": "alice@example.com",
    "timestamp": "2024-03-20T10:00:00Z"
  }
}
```

**Response:**
```json
{
  "chunkIds": ["chunk-1", "chunk-2"],
  "entities": [
    {
      "text": "Alice",
      "type": "PERSON",
      "score": 0.95
    },
    {
      "text": "Platform Rebuild",
      "type": "TITLE",
      "score": 0.88
    }
  ],
  "timestamp": "2024-03-20T10:05:00Z"
}
```

**Process Flow:**
1. Extract entities using Amazon Comprehend
2. Chunk text into manageable pieces
3. Generate embeddings using Bedrock Titan
4. Store in OpenSearch with vector embeddings
5. Store metadata in DynamoDB
6. Queue graph update for Neptune

---

## Data Models

### MemoryChunk (OpenSearch)
```json
{
  "chunkId": "uuid",
  "content": "text content",
  "embedding": [0.123, 0.456, ...],  // 1536-dim vector
  "source": "email | slack | github | document",
  "sourceRef": "url or identifier",
  "projectId": "uuid",
  "timestamp": "ISO8601",
  "entities": ["entity1", "entity2"]
}
```

### Entity (DynamoDB)
```json
{
  "entityId": "uuid",
  "type": "Person | Project | Decision | Artifact | Event",
  "name": "string",
  "metadata": {},
  "createdAt": "ISO8601",
  "sourceId": "uuid"
}
```

### KnowledgeGraph (Neptune/Gremlin)
```
Vertices:
- Project (projectId, name, status)
- Person (email, name)
- Decision (decisionId, title, description)
- Artifact (artifactId, type, url)
- Event (eventId, timestamp, type)

Edges:
- has_decision (Project -> Decision)
- made (Person -> Decision)
- triggered_by (Decision -> Artifact)
- implemented_in (Decision -> Event)
- related_to (Entity -> Entity)
```

---

## Error Responses

### 400 Bad Request
```json
{
  "error": "Query is required"
}
```

### 500 Internal Server Error
```json
{
  "error": "Error message describing the issue"
}
```

---

## Rate Limits
- Default: 100 requests per minute per IP
- Burst: 200 requests

---

## Example Usage

### cURL
```bash
# Query memory
curl -X POST https://api.example.com/prod/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Why was Feature X delayed?"}'

# List projects
curl https://api.example.com/prod/projects

# Get decisions for a project
curl "https://api.example.com/prod/decisions?projectId=uuid"
```

### JavaScript (Axios)
```javascript
import axios from 'axios';

const API_BASE = 'https://api.example.com/prod';

// Query memory
const response = await axios.post(`${API_BASE}/query`, {
  query: 'Why was Feature X delayed?'
});

console.log(response.data.answer);
console.log(response.data.sources);
```

### Python (Requests)
```python
import requests

API_BASE = 'https://api.example.com/prod'

# Query memory
response = requests.post(f'{API_BASE}/query', json={
    'query': 'Why was Feature X delayed?'
})

data = response.json()
print(data['answer'])
print(data['confidence'])
```

---

## Webhooks (Future)

### Slack Integration
```
POST /webhooks/slack
```

### GitHub Integration
```
POST /webhooks/github
```

### Email Integration
```
POST /webhooks/email
```

---

## SDK Support (Planned)
- JavaScript/TypeScript SDK
- Python SDK
- CLI tool

---

**Last Updated:** March 2024
**API Version:** 1.0.0
