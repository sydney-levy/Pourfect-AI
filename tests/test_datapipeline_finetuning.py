import os
import unittest
from unittest import mock
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src/datapipeline')))

# Importing the functions we want to test and environment variables
from finetuning_data import (
    generate,
    prepare,
    GCP_PROJECT,
    GCP_LOCATION,
    GENERATIVE_MODEL,
    OUTPUT_FOLDER,
)


class TestFinetuningData(unittest.TestCase):

    def test_project_and_location(self):
        # Test that the GCP project and location are set correctly
        self.assertEqual(GCP_PROJECT, "pourfectai-aida")
        self.assertEqual(GCP_LOCATION, "us-central1")

    def test_model_name(self):
        # Test that the generative model name is set correctly
        self.assertEqual(GENERATIVE_MODEL, "gemini-1.5-flash-001")

    def test_generate_function(self):
        # Test the generate function for any exceptions
        try:
            generate()
        except Exception as e:
            self.fail(f"generate() raised an exception unexpectedly: {e}")

    def test_output_folder_creation(self):
        # Test if the OUTPUT_FOLDER is created after running generate()
        generate()
        self.assertTrue(
            os.path.exists(OUTPUT_FOLDER), "Output folder was not created"
        )

if __name__ == "__main__":
    unittest.main()
