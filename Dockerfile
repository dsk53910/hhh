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

# DATABASE_URL is loaded from Render environment variables
# For local testing: postgresql+asyncpg://postgres:[PASSWORD]@db.yabuqmchfkzvguyjwago.supabase.co:5432/postgres

# Run the bot with health endpoint on port 8000
CMD python -c "
import os
import asyncio
from aiohttp import web
from src.bot.main import main

async def health(request):
    return web.Response(text='OK')

async def start():
    app = web.Application()
    app.router.add_get('/health', health)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', int(os.getenv('PORT', 8000)))
    await site.start()
    
    # Run bot in background
    bot_task = asyncio.create_task(main())
    
    # Keep running
    await asyncio.Event().wait()

asyncio.run(start())
"