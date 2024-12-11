import pandas as pd
import ast
from google.cloud import storage


def download_data(gcp_project, bucket_name,
                  source_blob_name, destination_file_name):
    """
    Download tabular data from our GCP bucket
    """
    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)
    print(f'Downloaded raw data to {destination_file_name}')


def process_data(input_file, output_file):
    """
    Process the data by dropping duplicates, na values, unnecessary columns
    """
    df = pd.read_csv(input_file)
    df = df.drop_duplicates(subset='title')
    df['raw_ingredients'] = df['raw_ingredients'].apply(ast.literal_eval)
    df.drop(columns=['ingredients'], inplace=True)
    df.dropna(subset=['recipe'], inplace=True)
    df.to_csv(output_file, index=False)
    print(f'Processed data saved to {output_file}')


def upload_data(gcp_project, bucket_name,
                destination_blob_name, source_file_name):
    """
    Upload data to GCP bucket
    """
    storage_client = storage.Client(project=gcp_project)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f'Uploaded {source_file_name} to'
          f'{destination_blob_name} in {bucket_name}')


if __name__ == '__main__':
    gcp_project = "pourfectai-aida"
    bucket_name = "pourfect-ai-bucket"
    raw_data_blob = 'raw_data/V1/raw_data.csv'
    raw_data_file = 'raw_data.csv'
    processed_data_blob = 'clean_data/V1/processed_data.csv'
    processed_data_file = 'processed_data.csv'

    download_data(gcp_project, bucket_name,
                  raw_data_blob, raw_data_file)
    process_data(raw_data_file, processed_data_file)
    upload_data(gcp_project, bucket_name,
                processed_data_blob, processed_data_file)
