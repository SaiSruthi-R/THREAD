# Memory Mapping - Architecture Deep Dive

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │Dashboard │  │ Projects │  │   Ask    │  │Knowledge │  │Decision││
│  │          │  │   View   │  │  Memory  │  │  Graph   │  │Timeline││
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘  └────────┘│
│                    React 18 + Tailwind CSS + D3.js                   │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓ HTTPS
┌─────────────────────────────────────────────────────────────────────┐
│                        AWS API GATEWAY                               │
│  ┌──────┐  ┌─────────┐  ┌──────────┐  ┌───────┐  ┌────────┐       │
│  │/query│  │/projects│  │/decisions│  │/graph │  │/ingest │       │
│  └──────┘  └─────────┘  └──────────┘  └───────┘  └────────┘       │
│              REST API + CORS + Throttling + Cognito Auth            │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        AWS LAMBDA LAYER                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ RAG Handler  │  │  Ingestion   │  │   Projects   │             │
│  │              │  │   Handler    │  │   Handler    │             │
│  │ • Embedding  │  │ • NER        │  │ • CRUD       │             │
│  │ • Search     │  │ • Chunking   │  │ • Timeline   │             │
│  │ • Generate   │  │ • Embedding  │  │              │             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                      │
│  ┌──────────────┐  ┌──────────────┐                                │
│  │  Decisions   │  │    Graph     │                                │
│  │   Handler    │  │   Handler    │                                │
│  │              │  │              │                                │
│  │ • Query      │  │ • Gremlin    │                                │
│  │ • Filter     │  │ • Traversal  │                                │
│  └──────────────┘  └──────────────┘                                │
│                     Python 3.11 + boto3                             │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        AI/ML SERVICES                                │
│  ┌──────────────────────┐  ┌──────────────────────┐                │
│  │   Amazon Bedrock     │  │ Amazon Comprehend    │                │
│  │                      │  │                      │                │
│  │ • Claude 3.5 Sonnet  │  │ • Entity Extraction  │                │
│  │   (Answer Gen)       │  │ • Key Phrases        │                │
│  │                      │  │ • Sentiment          │                │
│  │ • Titan Embeddings   │  │                      │                │
│  │   (1536-dim vectors) │  │                      │                │
│  └──────────────────────┘  └──────────────────────┘                │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        STORAGE LAYER                                 │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │   OpenSearch     │  │  Amazon Neptune  │  │   DynamoDB       │ │
│  │                  │  │                  │  │                  │ │
│  │ • Vector Index   │  │ • Knowledge      │  │ • Projects       │ │
│  │ • k-NN Search    │  │   Graph          │  │ • Decisions      │ │
│  │ • Full-text      │  │ • Gremlin API    │  │ • Metadata       │ │
│  │                  │  │ • Relationships  │  │                  │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐                        │
│  │   Amazon S3      │  │   Amazon SQS     │                        │
│  │                  │  │                  │                        │
│  │ • Raw Documents  │  │ • Ingestion      │                        │
│  │ • Backups        │  │   Queue          │                        │
│  │ • Archives       │  │ • Graph Updates  │                        │
│  └──────────────────┘  └──────────────────┘                        │
└─────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────┐
│                        DATA SOURCES                                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐           │
│  │  Gmail/  │  │  Slack/  │  │  GitHub  │  │Documents │           │
│  │ Outlook  │  │  Teams   │  │          │  │   (S3)   │           │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘           │
│       API          Webhooks      Webhooks      Upload               │
└─────────────────────────────────────────────────────────────────────┘
```

## Data Flow Diagrams

### 1. Ingestion Pipeline

```
┌─────────────┐
│ Data Source │ (Email, Slack, GitHub, Document)
└──────┬──────┘
       │
       ↓ POST /ingest
┌─────────────────────┐
│ Ingestion Lambda    │
│                     │
│ 1. Validate input   │
│ 2. Extract entities │ ← Amazon Comprehend
│ 3. Chunk text       │
│ 4. Generate vectors │ ← Bedrock Titan
└──────┬──────────────┘
       │
       ├─────────────────────┐
       │                     │
       ↓                     ↓
┌──────────────┐      ┌──────────────┐
│  OpenSearch  │      │  DynamoDB    │
│              │      │              │
│ Store chunks │      │ Store meta   │
│ + embeddings │      │ data         │
└──────────────┘      └──────────────┘
       │
       ↓ Queue message
┌──────────────┐
│     SQS      │
└──────┬───────┘
       │
       ↓ Trigger
┌──────────────────┐
│ Graph Updater    │
│                  │
│ Create nodes     │
│ Create edges     │
└────────┬─────────┘
         │
         ↓
┌──────────────┐
│   Neptune    │
│              │
│ Knowledge    │
│ Graph        │
└──────────────┘
```

### 2. RAG Query Pipeline

```
┌─────────────┐
│ User Query  │ "Why was Feature X delayed?"
└──────┬──────┘
       │
       ↓ POST /query
┌─────────────────────┐
│  RAG Lambda         │
│                     │
│ 1. Generate query   │
│    embedding        │ ← Bedrock Titan
└──────┬──────────────┘
       │
       ↓ k-NN search
┌─────────────────────┐
│  OpenSearch         │
│                     │
│ Vector similarity   │
│ Top 5 chunks        │
└──────┬──────────────┘
       │
       ├─────────────────────┐
       │                     │
       ↓                     ↓
┌──────────────┐      ┌──────────────┐
│   Neptune    │      │  DynamoDB    │
│              │      │              │
│ Get related  │      │ Get metadata │
│ entities     │      │              │
└──────┬───────┘      └──────┬───────┘
       │                     │
       └──────────┬──────────┘
                  │
                  ↓ Context
┌─────────────────────────────┐
│  Bedrock Claude             │
│                             │
│ Generate grounded answer    │
│ with source references      │
└──────┬──────────────────────┘
       │
       ↓ Response
┌─────────────────────┐
│  User Interface     │
│                     │
│ • Answer text       │
│ • Sources (links)   │
│ • Confidence score  │
│ • Graph nodes       │
└─────────────────────┘
```

### 3. Knowledge Graph Construction

```
┌─────────────────┐
│ Ingested Data   │
└────────┬────────┘
         │
         ↓ Extract entities
┌─────────────────────────────┐
│ Amazon Comprehend           │
│                             │
│ • PERSON: Alice, Bob        │
│ • TITLE: Platform Rebuild   │
│ • DATE: March 2024          │
│ • ORGANIZATION: Team Alpha  │
└────────┬────────────────────┘
         │
         ↓ Create vertices
┌─────────────────────────────┐
│ Neptune Graph               │
│                             │
│ V(Alice) [Person]           │
│ V(Platform Rebuild) [Proj]  │
│ V(API Refactor) [Decision]  │
│ V(Email #123) [Artifact]    │
│ V(Commit abc) [Event]       │
└────────┬────────────────────┘
         │
         ↓ Create edges
┌─────────────────────────────┐
│ Relationships               │
│                             │
│ Alice --[made]--> Decision  │
│ Project --[has]--> Decision │
│ Decision --[from]--> Email  │
│ Decision --[impl]--> Commit │
└─────────────────────────────┘
```

## Component Interactions

### Frontend → Backend

```javascript
// User submits query
const response = await axios.post('/query', {
  query: 'Why was Feature X delayed?'
});

// Backend processes
1. Generate embedding: [0.123, 0.456, ...]
2. Search OpenSearch: 5 relevant chunks
3. Query Neptune: related entities
4. Generate answer: Claude 3.5
5. Return response: {answer, sources, confidence}

// Frontend displays
- Answer text with references [1], [2]
- Source cards (clickable links)
- Confidence badge (87%)
- Graph visualization option
```

### Lambda → AWS Services

```python
# RAG Handler interactions
bedrock_runtime.invoke_model(
    modelId='amazon.titan-embed-text-v1',
    body={'inputText': query}
)
↓
opensearch_client.search(
    index='memory-chunks',
    body={'knn': {'embedding': {'vector': query_vector, 'k': 5}}}
)
↓
gremlin_client.submit(
    "g.V('entity-id').bothE().otherV().limit(50)"
)
↓
bedrock_runtime.invoke_model(
    modelId='anthropic.claude-3-5-sonnet',
    body={'messages': [{'role': 'user', 'content': prompt}]}
)
```

## Security Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Security Layers                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. Network Layer                                            │
│     ┌──────────────────────────────────────┐               │
│     │ VPC (10.0.0.0/16)                    │               │
│     │  ├─ Public Subnet (NAT Gateway)      │               │
│     │  ├─ Private Subnet (Lambda)          │               │
│     │  └─ Private Subnet (OpenSearch)      │               │
│     └──────────────────────────────────────┘               │
│                                                              │
│  2. Authentication Layer                                     │
│     ┌──────────────────────────────────────┐               │
│     │ Amazon Cognito                       │               │
│     │  ├─ User Pools                       │               │
│     │  ├─ JWT Tokens                       │               │
│     │  └─ MFA (optional)                   │               │
│     └──────────────────────────────────────┘               │
│                                                              │
│  3. Authorization Layer                                      │
│     ┌──────────────────────────────────────┐               │
│     │ AWS IAM                              │               │
│     │  ├─ Lambda Execution Roles           │               │
│     │  ├─ Service-to-Service Auth          │               │
│     │  └─ Resource Policies                │               │
│     └──────────────────────────────────────┘               │
│                                                              │
│  4. Data Layer                                               │
│     ┌──────────────────────────────────────┐               │
│     │ Encryption                           │               │
│     │  ├─ At Rest (KMS)                    │               │
│     │  ├─ In Transit (TLS 1.2+)            │               │
│     │  └─ Field-level (sensitive data)     │               │
│     └──────────────────────────────────────┘               │
│                                                              │
│  5. Application Layer                                        │
│     ┌──────────────────────────────────────┐               │
│     │ API Gateway                          │               │
│     │  ├─ Rate Limiting (100 req/min)      │               │
│     │  ├─ Request Validation               │               │
│     │  └─ WAF Rules                        │               │
│     └──────────────────────────────────────┘               │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Scalability Patterns

### Horizontal Scaling

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Distribution                         │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  API Gateway                                                 │
│       │                                                      │
│       ├──────┬──────┬──────┬──────┐                        │
│       ↓      ↓      ↓      ↓      ↓                        │
│   Lambda Lambda Lambda Lambda Lambda                        │
│   (Auto-scaling: 0 → 1000 concurrent)                       │
│       │      │      │      │      │                        │
│       └──────┴──────┴──────┴──────┘                        │
│              │                                               │
│              ↓                                               │
│       ┌─────────────┐                                       │
│       │ OpenSearch  │                                       │
│       │ Data Nodes  │                                       │
│       │  ├─ Node 1  │                                       │
│       │  ├─ Node 2  │                                       │
│       │  └─ Node 3  │                                       │
│       └─────────────┘                                       │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Caching Strategy

```
User Query
    ↓
┌─────────────┐
│ CloudFront  │ (Static assets)
└──────┬──────┘
       ↓
┌─────────────┐
│ API Gateway │ (Response caching: 5 min)
└──────┬──────┘
       ↓
┌─────────────┐
│   Lambda    │
└──────┬──────┘
       ↓
┌─────────────┐
│ ElastiCache │ (Query results: 1 hour)
│   (Redis)   │
└──────┬──────┘
       ↓
┌─────────────┐
│ OpenSearch  │ (Vector cache)
└─────────────┘
```

## Monitoring & Observability

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring Stack                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  CloudWatch Logs                                             │
│  ├─ Lambda execution logs                                    │
│  ├─ API Gateway access logs                                  │
│  └─ Application logs                                         │
│                                                              │
│  CloudWatch Metrics                                          │
│  ├─ Lambda duration, errors, throttles                       │
│  ├─ API Gateway latency, 4xx, 5xx                           │
│  ├─ OpenSearch cluster health                                │
│  └─ DynamoDB read/write capacity                             │
│                                                              │
│  CloudWatch Alarms                                           │
│  ├─ High error rate (> 5%)                                   │
│  ├─ High latency (> 3s)                                      │
│  ├─ Lambda throttling                                        │
│  └─ OpenSearch disk space (> 80%)                            │
│                                                              │
│  X-Ray Tracing                                               │
│  ├─ End-to-end request tracing                               │
│  ├─ Service map visualization                                │
│  └─ Performance bottleneck identification                    │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

## Disaster Recovery

```
┌─────────────────────────────────────────────────────────────┐
│                    Backup Strategy                           │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  DynamoDB                                                    │
│  ├─ Point-in-time recovery (35 days)                         │
│  ├─ On-demand backups                                        │
│  └─ Cross-region replication                                 │
│                                                              │
│  OpenSearch                                                  │
│  ├─ Automated snapshots (daily)                              │
│  ├─ Manual snapshots (before changes)                        │
│  └─ S3 snapshot repository                                   │
│                                                              │
│  Neptune                                                     │
│  ├─ Automated backups (7 days)                               │
│  ├─ Manual snapshots                                         │
│  └─ Read replicas (HA)                                       │
│                                                              │
│  S3                                                          │
│  ├─ Versioning enabled                                       │
│  ├─ Cross-region replication                                 │
│  └─ Lifecycle policies                                       │
│                                                              │
│  Recovery Time Objective (RTO): < 1 hour                     │
│  Recovery Point Objective (RPO): < 5 minutes                 │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

**Architecture Version**: 1.0.0
**Last Updated**: March 2024
