from fastapi.testclient import TestClient
from qdrant_mcpserver.fastapi_server import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

@patch('qdrant_mcpserver.fastapi_server.openai.Embedding.create')
def test_upsert_nodes(mock_embedding):
    mock_embedding.return_value = {"data": [{"embedding": [0.1]*1536}]}
    test_node = {"id": "test1", "text": "test"}
    
    response = client.post("/nodes/upsert", json=[test_node])
    assert response.status_code == 200
    assert "success" in response.json()