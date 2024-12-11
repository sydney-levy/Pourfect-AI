from typing import Dict, List
from fastapi import HTTPException
import traceback
import chromadb
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from vertexai.generative_models import GenerativeModel, ChatSession

# Setup
GCP_PROJECT = "pourfectai-aida"
GCP_LOCATION = "us-central1"
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 256
# GENERATIVE_MODEL = "gemini-1.5-flash-002"
GENERATIVE_MODEL = (
    "projects/pourfectai-aida/locations/us-central1/endpoints/"
    "8669025761920811008"
)
CHROMADB_HOST = "pourfect-app-vector-db"
CHROMADB_PORT = 8000

# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 8192,
    "temperature": 0.25,
    "top_p": 0.95,
}

# Initialize the GenerativeModel with specific system instructions
SYSTEM_INSTRUCTION = (
    "You are a fun, charming, and witty AI assistant specialized in bartender"
    "& cocktail knowledge. Your responses are based solely on the information"
    " provided in the text chunks given to you."
    "Your responses are based solely on the information provided in the text "
    "chunks given to you. Do not use any external knowledge or make "
    "assumptions beyond what is explicitly stated in these chunks.\n\n"
    "When answering a query:\n"
    "1. Carefully read all the text chunks provided.\n"
    "2. Identify the most relevant information from these chunks "
    "to address the user's question.\n"
    "3. Formulate your response using the information found in the "
    "given chunks.\n4. Always maintain a professional and knowledgeable tone, "
    "befitting a cocktail expert.\n"
    "5. If there are contradictions in the provided chunks, mention this "
    "in your response and explain the different viewpoints presented.\n"
    "6. If the user asks you to create a cocktail using available "
    "ingredients, you don't have to use all of them.\n\n"
    "Remember:\n"
    "- You are an expert in cocktails, and you're allowed to make up new "
    "recipes if there isn't one in the provided context that matches exactly."
    "\n- If asked about topics unrelated to cocktails, politely redirect the "
    "conversation back to cocktail-related subjects.\n"
    "- Be concise in your responses while ensuring you cover all relevant "
    "information from the chunks.\n\n"
    "Your goal is to provide accurate, helpful information about cocktails "
    "based solely on the content of the text chunks you receive with each "
    "query."
)

generative_model = GenerativeModel(
    GENERATIVE_MODEL, system_instruction=[SYSTEM_INSTRUCTION]
)
# https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/text-embeddings-api#python
embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

# Initialize chat sessions
chat_sessions: Dict[str, ChatSession] = {}

# Connect to chroma DB
client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
method = "recursive-split"
collection_name = "text-collection"
# Get the collection
collection = client.get_collection(name=collection_name)


def generate_query_embedding(query):
    query_embedding_inputs = [
        TextEmbeddingInput(task_type="RETRIEVAL_DOCUMENT", text=query)
    ]
    kwargs = (
        dict(output_dimensionality=EMBEDDING_DIMENSION)
        if EMBEDDING_DIMENSION
        else {}
    )
    embeddings = embedding_model.get_embeddings(
        query_embedding_inputs, **kwargs
    )
    return embeddings[0].values


def create_chat_session() -> ChatSession:
    """Create a new chat session with the model"""
    return generative_model.start_chat()


def generate_chat_response(chat_session: ChatSession, message: Dict) -> str:
    """
    Generate a response using the chat session to maintain history.
    Handles text inputs.

    Args:
        chat_session: The Vertex AI chat session
        message: Dict containing 'content' (text)

    Returns:
        str: The model's response
    """
    try:
        # Initialize parts list for the message
        message_parts = []

        # Add text content if present
        if message.get("content"):
            # Create embeddings for the message content
            query_embedding = generate_query_embedding(message["content"])
            # Retrieve chunks based on embedding value
            results = collection.query(
                query_embeddings=[query_embedding], n_results=10
            )

            INPUT_PROMPT = f"""
            Here are some text chunks that may contain relevant information:

            {results["documents"]}

            Based on the above information, along with any information you may
            previously know about cocktails, please answer the following query.
            If the provided text does not have an exact recipe for what the
            user queries, do not mention that. Instead, create an
            appetizing recipe on your own.
            DO NOT mention anything about the text chunks.


            {message["content"]}
            """

            message_parts.append(INPUT_PROMPT)

        if not message_parts:
            raise ValueError("Message must contain either text content")

        # Send message with all parts to the model
        response = chat_session.send_message(
            message_parts, generation_config=generation_config
        )

        return response.text

    except Exception as e:
        print(f"Error generating response: {str(e)}")
        traceback.print_exc()
        raise HTTPException(
            status_code=500, detail=f"Failed to generate response: {str(e)}"
        )


def rebuild_chat_session(chat_history: List[Dict]) -> ChatSession:
    """Rebuild a chat session with complete context"""
    new_session = create_chat_session()

    for message in chat_history:
        if message["role"] == "user":
            generate_chat_response(new_session, message)

    return new_session
