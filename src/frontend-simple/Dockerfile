FROM node:14.9.0-buster-slim

# Update baseline, install dependencies, and set up a non-root user
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends openssl && \
    npm install -g http-server && \
    useradd -ms /bin/bash app -d /home/app -u 2000 && \
    mkdir -p /app && \
    chown app:app /app && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Switch to non-root user
USER app
WORKDIR /app

COPY . /app

# Expose port and define entrypoint
EXPOSE 3000
ENTRYPOINT ["http-server"]
CMD ["-p", "3000"]