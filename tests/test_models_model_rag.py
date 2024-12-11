import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/models")),
)

# Importing functions we want to test
from model_rag import (
    generate_query_embedding,
    retrieve_documents_from_db,
    generate_cocktail_response,
)


class TestModelRag(unittest.TestCase):

    @patch("model_rag.TextEmbeddingModel.from_pretrained")
    def test_generate_query_embedding(self, MockTextEmbeddingModel):
        # Mocking the TextEmbeddingModel for embedding generation
        mock_embedding_model = MagicMock()
        MockTextEmbeddingModel.return_value = mock_embedding_model
        mock_embedding_model.get_embeddings.return_value = [
            MagicMock(values=[0.1, 0.2, 0.3, 0.4])
        ]

        query = "What cocktail can I make with vodka and orange juice?"

        # Generate query embedding
        embedding = generate_query_embedding(query, mock_embedding_model)

        # Check that embedding generation is correct
        mock_embedding_model.get_embeddings.assert_called_once()
        # MagicMock embedding vals
        self.assertEqual(embedding, [0.1, 0.2, 0.3, 0.4]) 

    @patch("model_rag.chromadb.HttpClient")
    def test_retrieve_documents_from_db(self, MockHttpClient):
        # Mocking the Chroma DB retrieval
        mock_client = MagicMock()
        MockHttpClient.return_value = mock_client
        mock_collection = MagicMock()
        mock_client.get_collection.return_value = mock_collection
        mock_collection.query.return_value = {
            "documents": ["Mocked text document 1", "Mocked text document 2"]
        }

        query_embedding = [0.1, 0.2, 0.3, 0.4]

        # Retrieve the documents from the DB
        documents = retrieve_documents_from_db(
            mock_client, "text-collection", query_embedding
        )

        # Check the response to make sur e it fits our standards
        mock_collection.query.assert_called_once_with(
            query_embeddings=[query_embedding], n_results=10
        )
        self.assertEqual(documents, "Mocked text document 1")

    @patch("model_rag.GenerativeModel")
    def test_generate_cocktail_response(self, MockGenerativeModel):
        # Mocking GenerativeModel to test response generation
        mock_generative_model = MagicMock()
        MockGenerativeModel.return_value = mock_generative_model
        mock_generative_model.generate_content.return_value = MagicMock(
            text="Mocked cocktail recipe response"
        )

        context = "Mocked text document 1\n\nMocked text document 2"
        query = "What cocktail can I make with vodka and orange juice?"

        # Generate response
        response = generate_cocktail_response(
            context, query, mock_generative_model
        )

        # check that the response was generated
        mock_generative_model.generate_content.assert_called_once()
        self.assertEqual(response, "Mocked cocktail recipe response")


if __name__ == "__main__":
    unittest.main()
