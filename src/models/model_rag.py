import os
import chromadb
import time

# Vertex AI
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from vertexai.generative_models import GenerativeModel, Content, Part

# Connect to chroma DB
GCP_PROJECT = "pourfectai-aida"
BUCKET_NAME = "pourfect-ai-bucket"
FOLDER_PATH = "raw_data/V1/text_data/"
LOCAL_DIRECTORY = os.path.join(os.getcwd(), "text_data")
EMBEDDING_MODEL = "text-embedding-004"
EMBEDDING_DIMENSION = 256
CHROMADB_HOST = "llm-rag-chromadb"
CHROMADB_PORT = 8000
# Model that we perform RAG with
MODEL_ENDPOINT = (
    "projects/pourfectai-aida/locations/us-central1/endpoints/"
    "8669025761920811008"
)  # Finetuned model
COLLECTION_NAME = "text-collection"  # Vector DB

SYSTEM_INSTRUCTION_2 = """
    You are an AI assistant specialized in bartender and cocktail knowledge.
    Your responses are based solely on the information provided in the text
     chunks given to you.
    Do not use any external knowledge or make assumptions beyond what is
      explicitly stated in these chunks.

    When answering a query:
    1. Carefully read all the text chunks provided.
    2. Identify the most relevant information from these chunks
      to address the user's question.
    3. Formulate your response using the information found in the given chunks.
    4. Always maintain a professional and knowledgeable tone, befitting
     x a cocktail expert.
    5. If there are contradictions in the provided chunks, mention this in your
      response and explain the different viewpoints presented.

    Remember:
    - You are an expert in cocktails, and you're allowed to make
      up new recipes if there isn't one in the provided
        context that matches exactly
    - If asked about topics unrelated to cocktails,
      politely redirect the conversation
      back to cocktail-related subjects.
    - Be concise in your responses while ensuring you
      cover all relevant information
      from the chunks.
    - If the text provided to you does not give you any
      information about a specific cocktail recipe, you
        can make one up, as long as it is still appetizing!
    """


def initialize_chroma_client():
    """
    Initialize the Chroma DB client
    """
    client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)
    return client


def load_embedding_model():
    """
    Load embedding model (we already fine-tuned this)
    """
    embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)
    return embedding_model


def generate_query_embedding(query, embedding_model):
    """
    Function to convert user question to vectorized embedding
    """
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


def retrieve_documents_from_db(
    client, collection_name, query_embedding, n_results=10
):
    """
    Get top n_result relevant documents from Vector DB
    """
    collection = client.get_collection(name=collection_name)
    results = collection.query(
        query_embeddings=[query_embedding], n_results=n_results
    )
    return results["documents"][0]


def generate_cocktail_response(context, query, generative_model):
    """
    Generate response with model
    """

    user_prompt_text = f"""
    Here are some text chunks that may contain relevant information about
      cocktails/mocktails and their recipes:

    {context}

    Based on the above information, along with any information you may
      previously know about cocktails, please answer the following query.
        If the provided text does not have an exact recipe for what the
          user queries, do not mention that. Instead, create an
            appetizing recipe on your own.

    {query}
    """

    user_prompt_content = Content(
        role="user", parts=[Part.from_text(user_prompt_text)]
    )

    generation_config = {
        "max_output_tokens": 8192,
        "temperature": 0.25,
        "top_p": 0.95,
    }

    response = generative_model.generate_content(
        user_prompt_content, generation_config=generation_config
    )
    return response.text


def process_query(query):
    """
    Process entire workflow
    """
    start_time = time.time()

    # Initialize necessary components
    client = initialize_chroma_client()
    embedding_model = load_embedding_model()

    # Generate query embedding
    query_embedding = generate_query_embedding(query, embedding_model)

    # Retrieve top 10 relevant documents from Chroma DB
    retrieved_docs = retrieve_documents_from_db(
        client, COLLECTION_NAME, query_embedding
    )

    # Put the top 10 documents into a single context
    context = "\n\n".join(retrieved_docs)

    # Initialize the generative model that we already finetuned on
    generative_model = GenerativeModel(
        MODEL_ENDPOINT, system_instruction=[SYSTEM_INSTRUCTION_2]
    )

    # Generate the response based on context and query
    response = generate_cocktail_response(context, query, generative_model)

    # Track the time it takes to generate a response
    end_time = time.time()
    duration = end_time - start_time

    print(f"Query: {query}\n")
    print(f"Pourfect AI: {response}")
    print(f"Time taken: {duration:.2f} seconds")


if __name__ == "__main__":
    query = (
        "Hello Pourfect AI! I have the following ingredients on hand: coffee, "
        "vodka, rum, triple sec, limes, and orange juice. Can I make a tasty "
        "cocktail with any of these?"
    )
    process_query(query)
