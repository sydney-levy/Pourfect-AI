import os
import pandas as pd
from google.cloud import storage
import chromadb
from vertexai.language_models import TextEmbeddingInput, TextEmbeddingModel
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

# Vertex AI and GCP Configuration
gcp_project = "pourfectai-aida"
bucket_name = "pourfect-ai-bucket"
folder_path = "raw_data/V1/text_data/"
local_directory = os.path.join(os.getcwd(), "text_data")
EMBEDDING_MODEL = "text-embedding-004"
CHROMADB_HOST = "pourfect-app-vector-db"
CHROMADB_PORT = 8000


def download_files_from_gcp(bucket_name,
                            folder_path, local_directory):
    """
    Download files from GCP bucket to local directory
    """

    # Create the local directory if it doesn't exist
    if not os.path.exists(local_directory):
        os.makedirs(local_directory)
    storage_client = storage.Client(project=gcp_project)
    blobs = storage_client.list_blobs(bucket_name, prefix=folder_path)

    for blob in blobs:
        if not blob.name.endswith("/"):
            local_file_path = os.path.join(local_directory,
                                           os.path.basename(blob.name))
            blob.download_to_filename(local_file_path)
            print(f"Downloaded {blob.name} to {local_file_path}")


def chunk_text_data(local_directory):
    """
    Chunk text data from local directory
    """
    docs = []

    for filename in os.listdir(local_directory):
        file_path = os.path.join(local_directory, filename)

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="ISO-8859-1",
                      errors="ignore") as file:
                content = file.read()

        docs.append(Document(
            page_content=content,
            metadata={"source": filename}
        ))

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500, chunk_overlap=50, add_start_index=True
    )

    all_splits = text_splitter.split_documents(docs)
    return all_splits


def generate_text_embeddings(chunks, embedding_model,
                             dimensionality=256, batch_size=50):
    """
    Generate embeddings for the text chunks
    """
    all_embeddings = []
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        inputs = [TextEmbeddingInput(text, "RETRIEVAL_DOCUMENT")
                  for text in batch]
        embeddings = embedding_model.get_embeddings(
            inputs, output_dimensionality=dimensionality)
        all_embeddings.extend([embedding.values for embedding in embeddings])

    return all_embeddings


def save_embeddings_to_csv(embeddings, filename='vectorized_data.csv'):
    """
    Save the embeddings to a CSV file
    """
    embeddings_df = pd.DataFrame(embeddings)
    embeddings_df.to_csv(filename, index=False)
    print(f"Embeddings saved to {filename}")


def upload_file_to_gcp(filename, bucket_name, destination_blob_name):
    """
    Upload a file to GCP storage
    """
    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(filename)
    print(f"Uploaded {filename} to {destination_blob_name} in {bucket_name}")


def create_vector_database(all_splits,
                           all_embeddings, collection_name="text-collection"):
    """
    Create and populate the vector database with text data and embeddings
    """
    client = chromadb.HttpClient(host=CHROMADB_HOST, port=CHROMADB_PORT)

    try:
        client.delete_collection(name=collection_name)
        print(f"Deleted existing collection '{collection_name}'")
    except Exception:
        print(f"Collection '{collection_name}' did not exist. Creating new.")

    collection = client.get_or_create_collection(name=collection_name)

    ids = [f"doc_{i}" for i in range(len(all_splits))]
    metadatas = [doc.metadata for doc in all_splits]
    documents = [doc.page_content for doc in all_splits]

    collection.add(
        ids=ids,
        documents=documents,
        embeddings=all_embeddings,
        metadatas=metadatas
    )

    print(f"Inserted {len(documents)} documents "
          f"into the collection '{collection_name}'.")
    collection_size = collection.count()
    print(f"The collection '{collection_name}' "
          f"now contains {collection_size} documents.")


if __name__ == '__main__':

    # Download our files from GCP
    download_files_from_gcp(bucket_name, folder_path, local_directory)

    # Chunk text data into smaller pieces
    all_splits = chunk_text_data(local_directory)

    # Initialize VertexAI embedding model
    embedding_model = TextEmbeddingModel.from_pretrained(EMBEDDING_MODEL)

    # Generate embeddings for the chunked data
    all_embeddings = generate_text_embeddings(
        [doc.page_content for doc in all_splits], embedding_model)

    # Save embeddings to CSV and upload to GCP
    save_embeddings_to_csv(all_embeddings)
    upload_file_to_gcp('vectorized_data.csv',
                       bucket_name, "clean_data/V1/vectorized_data.csv")

    # Create the vector database in Chroma DB
    create_vector_database(all_splits, all_embeddings)
