from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from qdrant_client import QdrantClient
from config import settings
from qdrant_client import QdrantKnowledgeGraph
import openai
import numpy as np

app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize clients
qdrant_kg = QdrantKnowledgeGraph()
openai.api_key = settings.openai_api_key

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
            NodeWithEmbedding(
                id=node.id,
                text=node.text,
                metadata=node.metadata,
                embedding=embedding,
            ).dict()
            for node, embedding in zip(nodes, embeddings)
        ]

        # Upsert to Qdrant
        result = await qdrant_kg.upsert_nodes(nodes_with_embeddings)
        return {"status": "success", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        results = await qdrant_kg.search(
            query_embedding=query_embedding,
            limit=query.limit,
            score_threshold=query.score_threshold,
        )
        return [SearchResult(**result) for result in results]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/nodes")
async def delete_nodes(node_ids: List[str]):
    """Delete nodes by IDs"""
    try:
        await qdrant_kg.delete_nodes(node_ids)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.port)