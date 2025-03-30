import pytest
from unittest.mock import MagicMock, patch
from qdrant_client.http import models

def test_ensure_collection(mock_qdrant_client):
    with patch.object(mock_qdrant_client.client, 'get_collection', side_effect=Exception()):
        with patch.object(mock_qdrant_client.client, 'create_collection') as mock_create:
            mock_qdrant_client._ensure_collection()
            mock_create.assert_called_once()

def test_upsert_nodes(mock_qdrant_client):
    test_nodes = [{
        "id": "node1",
        "text": "test",
        "metadata": {},
        "embedding": [0.1]*1536
    }]
    with patch.object(mock_qdrant_client.client, 'upsert') as mock_upsert:
        assert mock_qdrant_client.upsert_nodes(test_nodes)
        mock_upsert.assert_called_once()