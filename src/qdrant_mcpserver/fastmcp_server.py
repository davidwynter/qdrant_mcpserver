from fastmcp import FastMCP
from pydantic import BaseModel
from typing import List, Optional
from config import settings
from qdrant_service import QdrantKnowledgeGraph
import openai
import numpy as np

class Node(BaseModel):
    id: str
    text: str
    metadata: Optional[dict] = None

class NodeWithEmbedding(Node):
    embedding: List[float]

class SearchQuery(BaseModel):
    text: str
    limit: Optional[int] = 10
    score_threshold: Optional[float] = None

class SearchResult(BaseModel):
    id: str
    score: float
    text: str
    metadata: dict

# Initialize services
qdrant_kg = QdrantKnowledgeGraph()
openai.api_key = settings.openai_api_key

# Create MCP server
app = FastMCP(
    name="Qdrant Knowledge Graph MCPServer",
    version="1.0.0",
    secret=settings.mcp_secret,
)

@app.post("/nodes/upsert")
async def upsert_nodes(nodes: List[Node]):
    """Upsert nodes with embeddings"""
    try:
        # Get embeddings from OpenAI
        texts = [node.text for node in nodes]
        response = openai.Embedding.create(
            input=texts,
            model=settings.model_name,
        )
        embeddings = [item["embedding"] for item in response["data"]]

        # Create nodes with embeddings
        nodes_with_embeddings = [
            {
                "id": node.id,
                "text": node.text,
                "metadata": node.metadata or {},
                "embedding": embedding,
            }
            for node, embedding in zip(nodes, embeddings)
        ]

        # Upsert to Qdrant
        success = qdrant_kg.upsert_nodes(nodes_with_embeddings)
        return {"success": success}
    except Exception as e:
        return {"error": str(e)}, 500

@app.post("/nodes/search")
async def search_nodes(query: SearchQuery):
    """Search for similar nodes"""
    try:
        # Get query embedding
        response = openai.Embedding.create(
            input=[query.text],
            model=settings.model_name,
        )
        query_embedding = response["data"][0]["embedding"]

        # Search Qdrant
        results = qdrant_kg.search(
            query_embedding=query_embedding,
            limit=query.limit,
            score_threshold=query.score_threshold,
        )
        return {"results": results}
    except Exception as e:
        return {"error": str(e)}, 500

@app.delete("/nodes")
async def delete_nodes(node_ids: List[str]):
    """Delete nodes by IDs"""
    try:
        success = qdrant_kg.delete_nodes(node_ids)
        return {"success": success}
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == "__main__":
    app.run(port=settings.mcp_port)