#!/bin/bash

# exit immediately if a command exits with a non-zero status
set -e

# Set vairables
export BASE_DIR=$(pwd)
export SECRETS_DIR=$(pwd)/../secrets/
export GCP_PROJECT="pourfectai-aida" # CHANGE TO YOUR PROJECT ID
export GOOGLE_APPLICATION_CREDENTIALS="/secrets/pourfectai-aida-6bad61768044.json"
export IMAGE_NAME="pourfect-app-vector-db-cli"

# Create the network if we don't have it yet
docker network inspect pourfect-app-network >/dev/null 2>&1 || docker network create pourfect-app-network

# Build the image based on the Dockerfile
docker build -t $IMAGE_NAME -f Dockerfile .

# Run All Containers
docker-compose run --rm --service-ports $IMAGE_NAME
