import os
import argparse
import pandas as pd
import json
import glob
from sklearn.model_selection import train_test_split
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel, SafetySetting

# Setup
GCP_PROJECT = "pourfectai-aida"
GCP_LOCATION = "us-central1"
GENERATIVE_MODEL = "gemini-1.5-flash-001"
OUTPUT_FOLDER = "clean_data/V3/finetuned/"
GCS_BUCKET_NAME = "pourfect-ai-bucket"
# Configuration settings for the content generation
generation_config = {
    "max_output_tokens": 8192,  # Maximum number of tokens for output
    "temperature": 1,  # Control randomness in output
    "top_p": 0.95,  # Use nucleus sampling
}

# Safety settings to filter out harmful content
safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_ONLY_HIGH,
    ),
]

# System Prompt
SYSTEM_INSTRUCTION = """Generate a set of 50 question-answer pairs
 about cocktails in English, adopting the tone and perspective of
   an experienced bartender. While answering questions, always
     suggest that these are answers, recommendations, and ideas
     from this bartender. Adhere to the following guidelines:

1. Question Independence:
   - Ensure each question-answer pair is completely
    independent and self-contained
   - Do not reference other questions or answers within the set
   - Each Q&A pair should be understandable without any additional context

2. Technical Information:
   - Incorporate detailed technical information about cocktail-making processes
   - Reference relevant technical terms, equipment, and methodologies
   used in cocktail-making

3. Expert Perspective and Personalization:
   - Embody the voice of a seasoned cocktail expert with deep knowledge
     of international cocktails
   - Address all answers directly from a bartender, using his name and a
     friendly yet respectful tone
   - Infuse responses with passion for cocktail craftsmanship and
     cocktail-making traditions
   - Reference cocktail-making regions, techniques, and historical
     anecdotes where relevant

4. Content Coverage:
   - Traditional and modern cocktail production methods,
     including specific techniques and equipment
   - Diverse cocktail types, their characteristics,
     and regional significance
   - Comparison of cocktails with international varieties,
     including technical differences
   - Cultural importance of cocktails in cuisine and society

5. Tone and Style:
   - Use a passionate, authoritative, yet friendly tone that conveys
     years of expertise
   - Incorporate humorous terms where appropriate, always providing
     English translations or brief explanations
   - Balance technical knowledge with accessible explanations from bartenders
   - Express pride in cocktail-making traditions while acknowledging
     global contributions

6. Complexity and Depth:
   - Provide a mix of basic information and advanced technical insights
   - Include lesser-known facts, expert observations, and scientific data
   - Offer nuanced explanations that reflect deep understanding of
     cocktail science and art

7. Question Types:
   - Include a variety of question types (e.g., "what", "how", "why",
     "can you explain", "what's the difference between")
   - Formulate questions as if someone is passionate about cocktail
   - Ensure questions cover a wide range of topics within the cocktail
     domain, including technical aspects

8. Answer Format:
   - Include vivid imagery and scenarios that bring the bartender's
     expertise to life, such as:
     * "This cocktail is smoother than velvet—get ready for something special!"
     * "Alright, folks! Ready to shake things up? Let’s make some
       magic behind the bar!"
     * "This mix? Easy as pouring water. You’ll be a pro in no time!"
     * "Boom! Now that’s how you stir up some excitement!"
     * "Let’s take this up a notch—time to add some flair to the party!"
     * "This blend is your secret weapon—trust me, you’ll be coming
       back for more!"
   - Give comprehensive answers that showcase expertise while
     maintaining a personal touch
   - Include relevant anecdotes, historical context, or scientific
     explanations where appropriate
   - Ensure answers are informative and engaging, balancing
     technical detail with accessibility

9. Cultural Context:
   - Highlight the role of cocktails in culture and cuisine
   - Discuss regional variations and their historical or geographical reasons

10. Accuracy and Relevance:
    - Ensure all information, especially technical data, is
      factually correct and up-to-date
    - Focus on widely accepted information in the field of cocktail expertise

11. Language:
    - Use English throughout, but feel free to include terms
      (with translations)
      where they add authenticity or specificity
    - Define technical terms when first introduced

Output Format:
Provide the Q&A pairs in JSON format, with each pair as an object containing
 'question' and 'answer' fields, within a JSON array.
Follow these strict guidelines:
1. Use double quotes for JSON keys and string values.
2. For any quotation marks within the text content, use single
 quotes (') instead
 of double quotes. Avoid quotation marks.
3. If a single quote (apostrophe) appears in the text, escape it with
 a backslash (\').
4. Ensure there are no unescaped special characters that could break
 the JSON structure.
5. Avoid any Invalid control characters that JSON decode will not be
 able to decode.

Here's an example of the expected format:
Sample JSON Output:
```json
[
  {
    "question": "What is a cocktail that uses vodka?",
    "answer": "A delicious cocktail that uses vodka is a Moscow Mule!"
  },
  {
    "question": "What is a cocktail for a evening party?",
    "answer": " A fantastic cocktail for an evening party is the Espresso
      Martini—elegant and energizing, it's a great way to keep the
        mood lively."
  }
 ]
```

Note: The sample JSON provided includes only two Q&A pairs for brevity.
 The actual output should contain all 20 pairs as requested."""


def generate():
    print("generate()")

    # Make dataset folders
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)

    # Initialize Vertex AI project and location
    vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)

    # Initialize the GenerativeModel with specific system instructions
    model = GenerativeModel(
        GENERATIVE_MODEL, system_instruction=[SYSTEM_INSTRUCTION]
    )

    INPUT_PROMPT = """Generate 50 diverse, informative, and engaging
      question-answer pairs about cocktails following these
        guidelines. Ensure each pair is independent
        and self-contained, embody the passionate and knowledgeable
         tone of a bartenderexpert, incorporate relevant technical
          information, keep all content in English, and address all
            answers directly from the bartender."""
    NUM_ITERATIONS = 5  # INCREASE TO CREATE A LARGE DATASET

    # Loop to generate and save the content
    for i in range(0, NUM_ITERATIONS):
        print(f"Generating batch: {i}")
        try:
            responses = model.generate_content(
                [INPUT_PROMPT],
                generation_config=generation_config,
                safety_settings=safety_settings,
                stream=False,
            )
            generated_text = responses.text

            # Create a unique filename for each iteration
            file_name = f"{OUTPUT_FOLDER}/cocktail_qa_{i}.txt"
            # Save
            with open(file_name, "w") as file:
                file.write(generated_text)
        except Exception as e:
            print(f"Error occurred while generating content: {e}")


def prepare():
    print("prepare()")

    # Get the generated files
    output_files = glob.glob(os.path.join(OUTPUT_FOLDER, "cocktail_qa_*.txt"))
    output_files.sort()

    # Consolidate the data
    output_pairs = []
    errors = []
    for output_file in output_files:
        print("Processing file:", output_file)
        with open(output_file, "r") as read_file:
            text_response = read_file.read()

        text_response = text_response.replace("```json", "").replace("```", "")

        try:
            json_responses = json.loads(text_response)
            output_pairs.extend(json_responses)

        except Exception as e:
            errors.append({"file": output_file, "error": str(e)})

    print("Number of errors:", len(errors))
    print(errors[:5])

    # Save the dataset
    output_pairs_df = pd.DataFrame(output_pairs)
    output_pairs_df.drop_duplicates(subset=["question"], inplace=True)
    output_pairs_df = output_pairs_df.dropna()
    print("Shape:", output_pairs_df.shape)
    print(output_pairs_df.head())
    filename = os.path.join(OUTPUT_FOLDER, "instruct-dataset.csv")
    output_pairs_df.to_csv(filename, index=False)

    # Build training formats
    output_pairs_df["text"] = (
        "human: "
        + output_pairs_df["question"]
        + "\n"
        + "bot: "
        + output_pairs_df["answer"]
    )

    # Gemini Data prep:
    # https://cloud.google.com/vertex-ai/generative-ai/docs/models/gemini-supervised-tuning-prepare
    # {"contents":[{"role":"user","parts":[{"text":"..."}]},{"role":"model","parts":[{"text":"..."}]}]}
    output_pairs_df["contents"] = output_pairs_df.apply(
        lambda row: [
            {"role": "user", "parts": [{"text": row["question"]}]},
            {"role": "model", "parts": [{"text": row["answer"]}]},
        ],
        axis=1,
    )

    # Test train split
    df_train, df_test = train_test_split(
        output_pairs_df, test_size=0.1, random_state=42
    )
    df_train[["text"]].to_csv(
        os.path.join(OUTPUT_FOLDER, "train.csv"), index=False
    )
    df_test[["text"]].to_csv(
        os.path.join(OUTPUT_FOLDER, "test.csv"), index=False
    )

    # Gemini : Max numbers of examples in validation dataset: 256
    df_test = df_test[:256]

    # JSONL
    with open(os.path.join(OUTPUT_FOLDER, "train.jsonl"), "w") as json_file:
        json_file.write(
            df_train[["contents"]].to_json(orient="records", lines=True)
        )
    with open(os.path.join(OUTPUT_FOLDER, "test.jsonl"), "w") as json_file:
        json_file.write(
            df_test[["contents"]].to_json(orient="records", lines=True)
        )


def upload():
    print("upload()")

    storage_client = storage.Client()
    bucket = storage_client.bucket(GCS_BUCKET_NAME)
    timeout = 300

    data_files = glob.glob(os.path.join(OUTPUT_FOLDER, "*.jsonl")) + glob.glob(
        os.path.join(OUTPUT_FOLDER, "*.csv")
    )
    data_files.sort()

    # Upload
    for index, data_file in enumerate(data_files):
        filename = os.path.basename(data_file)
        destination_blob_name = os.path.join(
            "clean_data/V3/finetuned", filename
        )
        blob = bucket.blob(destination_blob_name)
        print("Uploading file:", data_file, destination_blob_name)
        blob.upload_from_filename(data_file, timeout=timeout)


def main(args=None):
    print("CLI Arguments:", args)

    if args.generate:
        generate()

    if args.prepare:
        prepare()

    if args.upload:
        upload()


if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal '--help', it will provide the description
    parser = argparse.ArgumentParser(description="CLI")

    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate data",
    )
    parser.add_argument(
        "--prepare",
        action="store_true",
        help="Prepare data",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload data to bucket",
    )

    args = parser.parse_args()

    main(args)
