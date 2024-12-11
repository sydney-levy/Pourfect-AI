# MODEL FINETUNING

import argparse
import time
import vertexai
from vertexai.preview.tuning import sft
from vertexai.generative_models import GenerativeModel
# from google.auth import default
# from google.oauth2 import service_account


# Setup
GCP_PROJECT = "pourfectai-aida"
GCP_LOCATION = "us-central1"
OUTPUT_FOLDER = "clean_data/V1/finetuned/"
GCS_BUCKET_NAME = "pourfect-ai-bucket"

TRAIN_DATASET = "gs://pourfect-ai-bucket/clean_data/V1/finetuned/train.jsonl"
VALIDATION_DATASET = (
    "gs://pourfect-ai-bucket/clean_data/V1/finetuned/test.jsonl"
)

GENERATIVE_SOURCE_MODEL = "gemini-1.5-flash-002"

# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 3000,  # Maximum number of tokens for output
    "temperature": 0.75,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}

# # Initialize Vertex AI with credentials
# credentials = service_account.Credentials.from_service_account_file(
#     "/secrets/pourfectai-aida-6bad61768044.json"
# )


vertexai.init(
    project=GCP_PROJECT,
    location=GCP_LOCATION,
)


def train(wait_for_job=False):
    print("train()")

    # Supervised Fine Tuning
    sft_tuning_job = sft.train(
        source_model=GENERATIVE_SOURCE_MODEL,
        train_dataset=TRAIN_DATASET,
        validation_dataset=VALIDATION_DATASET,
        epochs=4,
        adapter_size=4,
        learning_rate_multiplier=1.0,
        tuned_model_display_name="pourfectai-finetuned-v1",
    )
    print("Training job started. Monitoring progress...\n\n")

    # Wait and refresh
    time.sleep(60)
    sft_tuning_job.refresh()

    if wait_for_job:
        print("Check status of tuning job:")
        print(sft_tuning_job)
        while not sft_tuning_job.has_ended:
            time.sleep(60)
            sft_tuning_job.refresh()
            print("Job in progress...")

    print(f"Tuned model name: {sft_tuning_job.tuned_model_name}")
    print(
        f"Tuned model endpoint name: "
        f"{sft_tuning_job.tuned_model_endpoint_name}"
    )
    print(f"Experiment: {sft_tuning_job.experiment}")


def chat():
    print("chat()")
    # Get the model endpoint from Vertex AI:
    # https://console.cloud.google.com/vertex-ai/studio/tuning?project=pourfectai-aida
    MODEL_ENDPOINT = (
        "projects/pourfectai-aida/locations/us-central1/endpoints/"
        "8669025761920811008"  # Finetuned model
    )

    generative_model = GenerativeModel(MODEL_ENDPOINT)

    query = "What is a cocktail whose main ingredient is vanilla vodka?"
    print("query: ", query)
    response = generative_model.generate_content(
        [query],
        generation_config=generation_config,
        stream=False,
    )
    generated_text = response.text
    print("Fine-tuned LLM Response:", generated_text)


def main(args=None):
    print("CLI Arguments:", args)

    if args.train:
        train()

    if args.chat:
        chat()


if __name__ == "__main__":
    # Generate the inputs arguments parser
    parser = argparse.ArgumentParser(description="CLI")

    parser.add_argument(
        "--train",
        action="store_true",
        help="Train model",
    )
    parser.add_argument(
        "--chat",
        action="store_true",
        help="Chat with model",
    )

    args = parser.parse_args()

    main(args)
