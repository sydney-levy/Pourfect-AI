import requests

# Integration tests-- run locally right now

BASE_URL = "http://localhost:9000/llm-rag/chats"
HEADERS = {
    "X-Session-ID": "215",
    "Content-Type": "application/json"
}
# Testing if pourfect AI can give a correct mojito recipe
USER_QUERY = {"content": "give me a mojito recipe"}
EXPECTED_KEYWORDS = ["rum", "mint", "lime"]

# Check to see if the api is accessible
def test_api_endpoint_accessible():
    """
    Test if the API endpoint is accessible.
    """
    response = requests.get(BASE_URL, headers=HEADERS)
    assert response.status_code == 200, f"API endpoint is not accessible: {response.status_code}"
    print("API endpoint is accessible.")

# POST request is used for sending data to a server -- testing if that works
def test_post_request_success():
    """
    Test if the POST request to the API is successful.
    """
    response = requests.post(BASE_URL, json=USER_QUERY, headers=HEADERS)
    assert response.status_code == 200, f"POST request failed: {response.status_code}"
    print("POST request is successful.")

# Ensuring Pourfect AI's response is good
def test_response_structure():
    """
    Test if the API response structure is valid.
    """
    response = requests.post(BASE_URL, json=USER_QUERY, headers=HEADERS)
    response_data = response.json()
    
    # Validate messages  exists
    assert "messages" in response_data, "Missing 'messages' in API response"
    assert isinstance(response_data["messages"], list), "'messages' should be a list"
    assert len(response_data["messages"]) > 0, "'messages' list is empty"
    print("API response structure is valid.")

# Validating that messages response exists
def test_assistant_message_exists():
    """
    Test if the assistant's reply exists in the API response.
    """
    response = requests.post(BASE_URL, json=USER_QUERY, headers=HEADERS)
    response_data = response.json()
    
    assistant_message = next(
        (msg["content"] for msg in response_data["messages"] if msg["role"] == "assistant"),
        None
    )
    assert assistant_message is not None, "No assistant message found in 'messages'"
    print("Assistant's message exists in the response.")

# Making sure it can produce a mojito recipe
def test_assistant_message_content():
    """
    Test if the assistant's message contains expected keywords.
    """
    response = requests.post(BASE_URL, json=USER_QUERY, headers=HEADERS)
    response_data = response.json()
    
    assistant_message = next(
        (msg["content"] for msg in response_data["messages"] if msg["role"] == "assistant"),
        None
    )
    response_text = assistant_message.lower()
    assert any(keyword in response_text for keyword in EXPECTED_KEYWORDS), \
        f"Response does not contain expected keywords: {response_text}"
    print("Assistant's message contains expected keywords.")

# Run all the tests
if __name__ == "__main__":
    test_api_endpoint_accessible()
    test_post_request_success()
    test_response_structure()
    test_assistant_message_exists()
    test_assistant_message_content()
