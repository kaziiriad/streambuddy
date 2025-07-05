# 1. Builder Stage: To install dependencies
FROM python:3.12-slim-bookworm as builder

# Install curl and other system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:${PATH}"

WORKDIR /app

# Create a virtual environment
RUN uv venv /opt/venv

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt .

# Install dependencies into the virtual environment
RUN . /opt/venv/bin/activate && uv pip install -r requirements.txt --no-cache

# 2. Runtime Stage: The final, lean image
FROM python:3.12-slim-bookworm as runtime

WORKDIR /app

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copy the virtual environment from the builder stage
COPY --from=builder /opt/venv /opt/venv

# Set the PATH to use the virtual environment
ENV PATH="/opt/venv/bin:${PATH}"

# Copy the rest of the application code
COPY . .

# Expose the port and set the entrypoint
EXPOSE 8000
ENTRYPOINT ["/app/docker-entrypoint.sh"]