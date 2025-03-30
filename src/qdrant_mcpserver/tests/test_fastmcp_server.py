import pytest
from fastmcp.testing import TestClient as MCPTestClient
from qdrant_mcpserver.fastmcp_server import app

@pytest.fixture
def mcp_client():
    return MCPTestClient(app)

def test_mcp_health(mcp_client):
    response = mcp_client.get("/health")
    assert response.status_code == 200
    assert response.mcp_envelope.version == "1.0"