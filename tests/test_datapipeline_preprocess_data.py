import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/datapipeline')))


# Importing the functions we want to test
from preprocess_data import download_data, process_data, upload_data


class TestPreprocessData(unittest.TestCase):
    # mock the storage.client in preprocess_data
    @patch("preprocess_data.storage.Client")
    def test_download_data(self, mock_storage_client):
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        # test names
        gcp_project = "test_project"
        bucket_name = "test_bucket"
        source_blob_name = "test_blob.csv"
        destination_file_name = "test_raw_data.csv"

        # test download_data
        download_data(
            gcp_project, bucket_name, source_blob_name, destination_file_name
        )

        # verify the call was made (assert_called_With)
        mock_storage_client.assert_called_with(project=gcp_project)
        mock_bucket.blob.assert_called_with(source_blob_name)
        mock_blob.download_to_filename.assert_called_with(
            destination_file_name
        )

    def test_process_data(self):
        # arrange the data so that it's similar to what we are working with
        input_data = pd.DataFrame(
            {
                "title": ["Recipe1", "Recipe2", "Recipe1"],
                "raw_ingredients": [
                    "['ingredient1', 'ingredient2']",
                    "['ingredient3']",
                    "['ingredient1', 'ingredient2']",
                ],
                "ingredients": ["Ing1", "Ing2", "Ing1"],
                "recipe": ["Step1", None, "Step1"],
            }
        )
        input_file = "test_raw_data.csv"
        output_file = "test_processed_data.csv"
        input_data.to_csv(input_file, index=False)

        # test process_data
        process_data(input_file, output_file)

        processed_data = pd.read_csv(output_file)
        # Duplicates dropped in dataset
        self.assertEqual(len(processed_data), 1)
        # Drop columns in dataset
        self.assertNotIn("ingredients", processed_data.columns)
        # Remove null recipes
        self.assertFalse(processed_data["recipe"].isnull().any())

        # remove files
        os.remove(input_file)
        os.remove(output_file)

    # mock the storage.client in preprocess_data again
    @patch("preprocess_data.storage.Client")
    def test_upload_data(self, mock_storage_client):
        mock_bucket = MagicMock()
        mock_blob = MagicMock()
        mock_storage_client.return_value.bucket.return_value = mock_bucket
        mock_bucket.blob.return_value = mock_blob

        gcp_project = "test_project"
        bucket_name = "test_bucket"
        destination_blob_name = "test_processed_data.csv"
        source_file_name = "test_processed_data.csv"

        # test upload_data
        upload_data(
            gcp_project, bucket_name, destination_blob_name, source_file_name
        )

        # verify the call was made (assert_called_With)
        mock_storage_client.assert_called_with(project=gcp_project)
        mock_bucket.blob.assert_called_with(destination_blob_name)
        mock_blob.upload_from_filename.assert_called_with(source_file_name)


if __name__ == "__main__":
    unittest.main()
