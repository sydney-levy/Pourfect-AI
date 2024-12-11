FROM python:3.12-slim

# Tell pipenv where the shell is. 
# This allows us to use "pipenv shell" as a container entry point.
ENV PYENV_SHELL=/bin/bash
ENV GOOGLE_APPLICATION_CREDENTIALS=secrets/llm-service-account.json

# Ensure we have an up-to-date baseline, install dependencies 
RUN set -ex; \
    apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir pipenv


WORKDIR /app

# Add Pipfile, Pipfile.lock
COPY Pipfile Pipfile.lock /app/

# Use RUN to install necessary packages with pipenv sync
RUN pipenv sync

# Source code
COPY . /app

# Entry point
ENTRYPOINT ["/bin/bash"]

# Get into the pipenv shell
CMD ["-c", "pipenv shell"]
