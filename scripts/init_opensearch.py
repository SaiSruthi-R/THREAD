"""Initialize OpenSearch index with proper mappings"""
import os
from opensearchpy import OpenSearch, RequestsHttpConnection
from dotenv import load_dotenv

load_dotenv()

opensearch_endpoint = os.getenv('OPENSEARCH_ENDPOINT')

# Connect to OpenSearch with basic auth
os_client = OpenSearch(
    hosts=[{'host': opensearch_endpoint, 'port': 443}],
    http_auth=('admin', 'Admin123!'),
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)

# Create index with k-NN mapping for vector search
index_body = {
    "settings": {
        "index": {
            "knn": True,
            "knn.algo_param.ef_search": 100
        }
    },
    "mappings": {
        "properties": {
            "chunkId": {"type": "keyword"},
            "content": {"type": "text"},
            "embedding": {
                "type": "knn_vector",
                "dimension": 1536,
                "method": {
                    "name": "hnsw",
                    "space_type": "l2",
                    "engine": "nmslib"
                }
            },
            "source": {"type": "keyword"},
            "sourceRef": {"type": "keyword"},
            "projectId": {"type": "keyword"},
            "timestamp": {"type": "date"},
            "entities": {"type": "keyword"}
        }
    }
}

try:
    # Check if index exists
    if os_client.indices.exists(index='memory-chunks'):
        print("Index 'memory-chunks' already exists")
    else:
        # Create the index
        response = os_client.indices.create(index='memory-chunks', body=index_body)
        print("✅ Created index 'memory-chunks' successfully!")
        print(f"Response: {response}")
except Exception as e:
    print(f"❌ Error: {e}")
