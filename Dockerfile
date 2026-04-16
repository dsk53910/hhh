# HHH Bot - Dockerfile for Render.com free tier
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PYTHONPATH=/app

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -u 1000 appuser

# Install uv
RUN pip install --no-cache-dir uv

# Copy project files
COPY . /app/

# Install Python dependencies
RUN uv pip install --system -r /app/pyproject.toml || true

# Create directories for data persistence
RUN mkdir -p /app/data /app/logs && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Default environment variables (Supabase PostgreSQL)
  # DATABASE_URL should be set via Render environment variables
  # Format: postgresql+asyncpg://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres

# Run the bot
CMD ["python", "-m", "src.bot.main"]