FROM python:3.12-slim-bookworm

# The installer requires curl (and certificates) to download the release archive
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh

# Ensure the installed binary is on the `PATH`
ENV PATH="/root/.local/bin/:$PATH"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    build-essential \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN uv venv .venv /app/.venv

ENV PATH="/app/.venv/bin:$PATH"

COPY requirements.txt .

RUN uv pip install -r requirements.txt

COPY . .

RUN mkdir -p /app/media/metadata \
    /app/media/dash_output \
    /app/media/temp_uploads


# Create a non-root user
RUN useradd -m streambuddy && \
    chown -R streambuddy:streambuddy /app

USER streambuddy

