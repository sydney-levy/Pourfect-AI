# Use the slim variant of Python 3.12 as the base image
FROM python:3.12-slim

# Set the environment variables for pipenv and Google credentials
ENV PYENV_SHELL=/bin/bash
ENV GOOGLE_APPLICATION_CREDENTIALS=secrets/pourfectai-aida-6bad61768044.json

# Install system dependencies required for building and running the application
RUN set -ex; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip and install pipenv for managing dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pipenv

# Set the working directory inside the container
WORKDIR /app

# Copy Pipfile and Pipfile.lock to the container's working directory
COPY Pipfile Pipfile.lock /app/

# Install the Python dependencies using pipenv
RUN pipenv sync

# Copy the rest of the application code into the container
COPY . /app

# Set the entry point to bash, enabling you to run commands inside the container
ENTRYPOINT ["/bin/bash"]

# Default command is to run "pipenv shell" in a non-interactive mode
CMD ["-c", "pipenv shell"]
