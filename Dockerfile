# Use official Python image based on Debian
FROM python:3.11-slim-bullseye

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100

# Set working directory
WORKDIR /app

# Install system dependencies (required for some Python packages like psycopg2)
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv (Fast Python package installer)
RUN pip install uv

# Copy only the requirements first to cache the layer
COPY pyproject.toml .

# Install dependencies using uv directly into the system python
RUN uv pip install --system -r pyproject.toml

# Copy the rest of the application
COPY . .

# Ensure the database migrations directory exists
RUN mkdir -p /app/migrations

# Make start script executable
RUN chmod +x /app/hhh.sh

# Command to run the application directly
CMD ["python", "-m", "src.bot.main"]
