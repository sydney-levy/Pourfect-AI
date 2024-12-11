import os
import unittest
from unittest.mock import patch, MagicMock
from langchain.schema import Document
import tempfile
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/datapipeline')))


# Import the functions to test from preprocess_rag.py
from preprocess_rag import (
    download_files_from_gcp,
    chunk_text_data,
    generate_text_embeddings,
    save_embeddings_to_csv,
    upload_file_to_gcp,
    create_vector_database,
)


class TestPreprocessRagFunctions(unittest.TestCase):

    @patch("preprocess_rag.storage.Client")
    @patch("os.makedirs")
    @patch("os.path.exists", return_value=False)
    def test_download_files_from_gcp(
        self, mock_exists, mock_makedirs, mock_storage_client
    ):
        # Mock the storage client and its methods
        mock_client_instance = mock_storage_client.return_value
        mock_blob = MagicMock()
        mock_blob.name = "test_file.txt"
        mock_blob.download_to_filename = MagicMock()

        mock_client_instance.list_blobs.return_value = [mock_blob]

        # testing files and instances
        download_files_from_gcp(
            "test_bucket", "test_folder_path", "test_local_directory"
        )

        mock_client_instance.list_blobs.assert_called_once_with(
            "test_bucket", prefix="test_folder_path"
        )

        expected_local_file_path = os.path.join(
            "test_local_directory", os.path.basename("test_file.txt")
        )
        mock_blob.download_to_filename.assert_called_once_with(
            expected_local_file_path
        )

    def test_chunk_text_data(self):
        # Test function for chunking text data
        with tempfile.TemporaryDirectory() as temp_dir:
            sample_text = "This is a test sentence. " * 30
            file_path = os.path.join(temp_dir, "sample.txt")

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(sample_text)

            all_splits = chunk_text_data(temp_dir)

            self.assertTrue(len(all_splits) > 0, "No chunks were created.")

            for chunk in all_splits:
                self.assertEqual(chunk.metadata["source"], "sample.txt")

            chunk_size = 500
            chunk_overlap = 50
            for i in range(1, len(all_splits)):
                previous_chunk_end = (
                    all_splits[i - 1].page_content[-chunk_overlap:].strip()
                )
                current_chunk_start = (
                    all_splits[i].page_content[:chunk_overlap].strip()
                )
                self.assertEqual(
                    previous_chunk_end,
                    current_chunk_start,
                    f"Chunk {i} doesn't overlap correctly with previous chunk",
                )

            self.assertEqual(
                previous_chunk_end,
                current_chunk_start,
                f"Chunk {i} does not overlap correctly with previous chunk.",
            )

            for i, chunk in enumerate(all_splits[:-1]):
                self.assertTrue(
                    len(chunk.page_content) <= chunk_size,
                    f"Chunk {i} exceeds the specified chunk size.",
                )

    @patch("preprocess_rag.TextEmbeddingModel")
    def test_generate_text_embeddings(self, mock_embedding_model):
        # Test function for generating text embeddings
        mock_embedding_instance = MagicMock()

        sample_embedding = MagicMock()
        sample_embedding.values = [0.1] * 256

        mock_embedding_instance.get_embeddings.return_value = [
            sample_embedding
        ]
        mock_embedding_model.from_pretrained.return_value = (
            mock_embedding_instance
        )

        chunks = ["sample text"]

        result = generate_text_embeddings(chunks, mock_embedding_instance)

        self.assertTrue(len(result) > 0)
        self.assertIsInstance(result[0], list)
        self.assertEqual(len(result[0]), 256)

    @patch("pandas.DataFrame.to_csv")
    def test_save_embeddings_to_csv(self, mock_to_csv):
        # Test function for saving embeddings to csv
        save_embeddings_to_csv([[0.1, 0.2]], "test_filename.csv")
        mock_to_csv.assert_called_once()

    @patch("preprocess_rag.storage.Client")
    def test_upload_file_to_gcp(self, mock_storage_client):
        # Test function for uploading a file to GCP bucket
        mock_bucket = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value.upload_from_filename = MagicMock()
        upload_file_to_gcp(
            "test_filename.csv", "test_bucket", "test_blob_name"
        )
        mock_storage_client.return_value.bucket.assert_called_once_with(
            "test_bucket"
        )

    @patch("preprocess_rag.chromadb.HttpClient")
    def test_create_vector_database(self, mock_chromadb_client):
        # Test function for creating a vector database on gcp
        mock_client_instance = MagicMock()
        mock_chromadb_client.return_value = mock_client_instance
        mock_collection = MagicMock()
        mock_client_instance.get_or_create_collection.return_value = (
            mock_collection
        )

        all_splits = [
            Document(
                page_content="sample content", metadata={"source": "sample"}
            )
        ]
        all_embeddings = [[0.1, 0.2]]

        create_vector_database(
            all_splits, all_embeddings, collection_name="test-collection"
        )
        mock_client_instance.get_or_create_collection.assert_called_once_with(
            name="test-collection"
        )


if __name__ == "__main__":
    unittest.main()