import unittest
from unittest.mock import patch, MagicMock
import sys
import os

sys.path.insert(
    0,
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/models")),
)

# Importing the functions to test from train_model.py
from train_model import train, chat


class TestFineTuning(unittest.TestCase):
    @patch("google.auth.default")
    @patch("vertexai.preview.tuning.sft.train")
    @patch("time.sleep", return_value=None)
    # Testing the training of a llm (supervised fine tuning)
    def test_train(self, mock_sleep, mock_train, mock_auth):
        mock_auth.return_value = (MagicMock(), "project-id")
        mock_job = MagicMock()
        mock_job.has_ended = True
        mock_job.tuned_model_name = "mock_model"
        mock_job.tuned_model_endpoint_name = "mock_endpoint"
        mock_job.experiment = "mock_experiment"
        mock_train.return_value = mock_job

        train(wait_for_job=True)
        mock_train.assert_called_once()

    @patch("google.auth.default")
    @patch("train_model.GenerativeModel.generate_content")
    # Testing the chatting functionality
    def test_chat(self, mock_generate_content, mock_auth):
        mock_auth.return_value = (MagicMock(), "project-id")
        mock_response = MagicMock()
        mock_response.text = "Sample Response"
        mock_generate_content.return_value = mock_response

        with patch("builtins.print") as mock_print:
            chat()
            mock_generate_content.assert_called_once()
            mock_print.assert_any_call(
                "Fine-tuned LLM Response:", "Sample Response"
            )


if __name__ == "__main__":
    unittest.main()
