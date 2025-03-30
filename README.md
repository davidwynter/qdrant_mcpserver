## A FastAPI client and a MCPServer client for Qdrant access as a service
The file main.py is the entry point and a command line argument selects which server you want to run.


### `main.py`

```python
import argparse
import uvicorn
from fastapi_server import app as fastapi_app
from fastmcp_server import app as fastmcp_app
from config import settings

def run_fastapi():
    """Run the FastAPI server"""
    print(f"Starting FastAPI server on port {settings.port}")
    uvicorn.run(
        fastapi_app,
        host="0.0.0.0",
        port=settings.port,
        log_level="info"
    )

def run_fastmcp():
    """Run the FastMCP server"""
    print(f"Starting FastMCP server on port {settings.mcp_port}")
    fastmcp_app.run(port=settings.mcp_port)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Qdrant MCP Server")
    parser.add_argument(
        "--server-type",
        choices=["fastapi", "fastmcp"],
        default="fastmcp",
        help="Type of server to run (default: fastmcp)"
    )
    args = parser.parse_args()

    if args.server_type == "fastapi":
        run_fastapi()
    else:
        run_fastmcp()
```

# Qdrant MCP Server

A dual-protocol server for Qdrant knowledge graph operations, supporting both FastAPI and FastMCP protocols.

## Project Structure

```markdown
src/qdrant_mcpserver/
├── __init__.py
├── config.py          # Configuration settings
├── qdrant_client.py   # Qdrant operations
├── fastapi_server.py  # FastAPI implementation
├── fastmcp_server.py  # FastMCP implementation
└── main.py            # CLI entry point
```

## File Descriptions

### `config.py`
- Loads environment variables
- Contains settings for:
  - Qdrant connection (URL, API key)
  - OpenAI API key
  - Collection names
  - Server ports
- Uses pydantic for validation

### `qdrant_client.py`
- Implements core Qdrant operations:
  - Collection management
  - Node upsert/delete
  - Vector search
- Handles embedding generation via OpenAI
- Provides service layer for both server types

### `fastapi_server.py`
- FastAPI implementation with:
  - RESTful endpoints
  - CORS middleware
  - OpenAPI documentation
- Endpoints:
  - POST /nodes/upsert
  - POST /nodes/search
  - DELETE /nodes
  - GET /health

### `fastmcp_server.py`
- FastMCP implementation with:
  - MCP protocol compliance
  - Authentication support
  - Standardized response formats
- Same endpoints as FastAPI but with MCP envelope

### `main.py`
- CLI entry point with:
  - Server type selection (--server-type)
  - Unified logging
  - Port configuration
- Runs either FastAPI or FastMCP server

## Installation

1. Install Poetry (if not installed):
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

2. Clone repository:
```bash
git clone https://github.com/your-repo/qdrant-mcpserver.git
cd qdrant-mcpserver
```

3. Install dependencies:
```bash
poetry install
```

4. Configure environment:
```bash
cp .env.example .env
# Edit .env with your actual values
```

## Usage

### Running the Server

```bash
# Run FastMCP server (default)
poetry run python -m qdrant_mcpserver.main

# Run FastAPI server
poetry run python -m qdrant_mcpserver.main --server-type fastapi
```

### Environment Variables


| Variable | Required | Description |
|----------|----------|-------------|
| QDRANT_URL | Yes | Qdrant server URL |
| QDRANT_API_KEY | No | Qdrant API key |
| OPENAI_API_KEY | Yes | OpenAI API key |
| COLLECTION_NAME | No | Default: "knowledge_graph" |
| PORT | No | FastAPI port (default: 8000) |
| MCP_PORT | No | FastMCP port (default: 8080) |
| MCP_SECRET | No | Authentication secret |

### API Endpoints

Both servers provide the same endpoints:

- `POST /nodes/upsert` - Upsert knowledge graph nodes
- `POST /nodes/search` - Semantic search across nodes
- `DELETE /nodes` - Delete nodes by IDs
- `GET /health` - Health check

## Development

### Code Formatting

These commands ensure consistent code style:

```bash
# Formats code according to Black's style guide (PEP 8 compliant)
poetry run black .
```

### Organizes imports properly (groups standard lib, third-party, local)
poetry run isort .Format code:
```bash
poetry run black .
poetry run isort .
```

### Testing

Using pytest for comprehensive test coverage. Test files should mirror the main code structure:

Setup tests
```bash
poetry install --with test
poetry run pytest --cov --cov-report=html
``` 

```bash
# Run all tests
poetry run pytest -v

# Run with coverage report
poetry run pytest --cov=qdrant_mcpserver --cov-report=term-missing
Setup tests (one time):
```

Type checking:
```bash
poetry run mypy .
```

## Deployment

Build production package:
```bash
poetry build
```

Install system-wide:
```bash
pip install dist/*.whl
```

Run as service:
```bash
python -m qdrant_mcpserver.main --server-type fastmcp
```


### Key Features:

1. **Flexible Server Selection**:
   - CLI argument chooses between FastAPI and FastMCP
   - Shared configuration and Qdrant client
   - Consistent endpoints across both

2. **Comprehensive Documentation**:
   - Clear file structure explanation
   - Installation and usage instructions
   - Environment variable reference
   - Development workflow

3. **Production-Ready**:
   - Poetry for dependency management
   - Configuration via environment variables
   - Build and deployment instructions

4. **Maintainable Structure**:
   - Separation of concerns
   - Shared core functionality
   - Clear development practices

The implementation allows you to switch between server protocols while maintaining the same underlying Qdrant operations.