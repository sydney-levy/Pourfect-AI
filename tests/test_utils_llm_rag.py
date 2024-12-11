import pytest
from unittest.mock import patch, MagicMock
import sys
import os

sys.modules["vertexai"] = MagicMock()
sys.modules["vertexai.language_models"] = MagicMock()
sys.modules["vertexai.generative_models"] = MagicMock()
sys.modules["chromadb"] = MagicMock()
sys.modules["chromadb.HttpClient"] = MagicMock()

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/api-service/api/utils")),
)

# Importing functions we want to test
from llm_rag_utils import (
    generate_query_embedding,
    create_chat_session,
    generate_chat_response,
    rebuild_chat_session
)

# Test for generate_query_embedding
def test_generate_query_embedding():
    mock_embedding = [0.1] * 256 

    with patch("llm_rag_utils.embedding_model.get_embeddings") as mock_get_embeddings:
        mock_get_embeddings.return_value = [MagicMock(values=mock_embedding)]

        result = generate_query_embedding("What is a margarita?")
        assert len(result) == 256  
        assert result == mock_embedding 
        mock_get_embeddings.assert_called_once()

# Test for create_chat_session 
def test_create_chat_session():
    mock_chat_session = "dummy_chat_session"

    with patch("llm_rag_utils.generative_model.start_chat") as mock_start_chat:
        mock_start_chat.return_value = mock_chat_session

        result = create_chat_session()
        assert result == mock_chat_session
        mock_start_chat.assert_called_once()

# Test for generate_chat_response -- mocking a felipe's margarita message
def test_generate_chat_response():
    mock_chat_session = MagicMock()
    mock_message = {"content": "How do you make a Felipe's margarita?"}
    mock_chunks = {"documents": ["Orange liqueur, blue agave tequila, simple syrup"]}
    mock_response = MagicMock()
    mock_response.text = "Here is the recipe for a Felipe's margarita..."

    with patch("llm_rag_utils.generate_query_embedding", return_value=[0.1, 0.2, 0.3]):
        with patch("llm_rag_utils.collection.query", return_value=mock_chunks):
            with patch.object(mock_chat_session, "send_message", return_value=mock_response):
                result = generate_chat_response(mock_chat_session, mock_message)
                assert result == "Here is the recipe for a Felipe's margarita..."

# Test for rebuild_chat_session function
def test_rebuild_chat_session():
    mock_chat_history = [
        {"role": "user", "content": "What is a common margarita recipe?"},
        {"role": "assistant", "content": "Common margaritas are made with tequila, lime, and triple sec."}
    ]
    mock_session = MagicMock()

    with patch("llm_rag_utils.create_chat_session", return_value=mock_session):
        with patch("llm_rag_utils.generate_chat_response") as mock_generate_response:
            rebuild_chat_session(mock_chat_history)
            mock_generate_response.assert_called_once_with(mock_session, mock_chat_history[0])