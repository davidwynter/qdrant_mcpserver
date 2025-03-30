import os
from typing import Optional
from pydantic import BaseSettings

class Settings(BaseSettings):
    qdrant_url: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    qdrant_api_key: Optional[str] = os.getenv("QDRANT_API_KEY")
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    collection_name: str = os.getenv("COLLECTION_NAME", "knowledge_graph")
    model_name: str = os.getenv("MODEL_NAME", "text-embedding-ada-002")
    # For FastAPI
    port: int = int(os.getenv("PORT", 8000))
    # For FastMCP
    mcp_port: int = int(os.getenv("MCP_PORT", 8000))
    mcp_secret: Optional[str] = os.getenv("MCP_SECRET")

    class Config:
        env_file = ".env"

settings = Settings()