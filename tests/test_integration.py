import unittest
import requests

BASE_URL = "http://34.23.190.158.sslip.io"

class TestAPIWelcomeMessage(unittest.TestCase):
    def test_api_welcome_message(self):
        """
        Test the /api endpoint to ensure it returns the correct welcome message.
        """
        response = requests.get(f"{BASE_URL}/api")
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("message", data)
        self.assertEqual(data["message"], "Welcome to PourfectAI - where every pour is perfectly yours!")

    def test_chat_functionality(self):
        """
        Test the /api/llm-rag/chats endpoint to ensure it responds correctly to a chat message.
        """
        url = f"{BASE_URL}/api/llm-rag/chats"
        headers = {
            "accept": "application/json",
            "Content-Type": "application/json",
            "X-Session-ID": "1"
        }
        payload = {
            "content": "what is the best cocktail?"
        }

        # Send request to api service
        response = requests.post(url, headers=headers, json=payload)

        self.assertEqual(response.status_code, 200, f"Expected status code 200 but got {response.status_code}")
        data = response.json()

        # Extract the response
        assistant_response = next(
            (message["content"] for message in data.get("messages", []) if message["role"] == "assistant"),
            None
        )

        self.assertIsNotNone(assistant_response, "No response from PourfectAI")
        self.assertGreater(len(assistant_response), 0, "PourfectAI's response content is empty")


if __name__ == "__main__":
    unittest.main()
