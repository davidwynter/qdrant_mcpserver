from qdrant_client import QdrantClient
from qdrant_client.http import models
from config import settings
import numpy as np
from typing import List, Dict, Any, Optional

class QdrantKnowledgeGraph:
    def __init__(self):
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
        )
        self.collection_name = settings.collection_name
        self._ensure_collection()

    def _ensure_collection(self):
        """Create collection if it doesn't exist"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            print(f"Collection {self.collection_name} already exists")
        except Exception:
            print(f"Creating new collection: {self.collection_name}")
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,  # OpenAI embedding size
                    distance=models.Distance.COSINE,
                ),
                optimizers_config=models.OptimizersConfigDiff(
                    indexing_threshold=0,
                ),
            )

    async def upsert_nodes(self, nodes: List[Dict[str, Any]]):
        """Upsert knowledge graph nodes"""
        points = []
        for node in nodes:
            points.append(
                models.PointStruct(
                    id=node["id"],
                    vector=node["embedding"],
                    payload={
                        "text": node["text"],
                        "metadata": node.get("metadata", {}),
                    },
                )
            )
        
        operation_info = self.client.upsert(
            collection_name=self.collection_name,
            points=points,
            wait=True,
        )
        return operation_info

    async def search(
        self,
        query_embedding: List[float],
        limit: int = 10,
        score_threshold: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar nodes"""
        search_result = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding,
            limit=limit,
            score_threshold=score_threshold,
        )

        return [
            {
                "id": hit.id,
                "score": hit.score,
                "text": hit.payload["text"],
                "metadata": hit.payload.get("metadata", {}),
            }
            for hit in search_result
        ]

    async def delete_nodes(self, node_ids: List[str]) -> bool:
        """Delete nodes by their IDs"""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=models.PointIdsList(
                points=node_ids,
            ),
        )
        return True