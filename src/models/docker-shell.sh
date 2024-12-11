#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Define some environment variables
export IMAGE_NAME="models"
export BASE_DIR=$(pwd)

docker network inspect llm-rag-network >/dev/null 2>&1 || docker network create llm-rag-network

docker-compose up -d chromadb

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run the container
docker run --rm -it --name $IMAGE_NAME \
  --network llm-rag-network \
  -v $BASE_DIR:/app \
  -v $BASE_DIR/secrets:/secrets \
  -e GOOGLE_APPLICATION_CREDENTIALS="/secrets/pourfectai-aida-6bad61768044.json" \
  $IMAGE_NAME
