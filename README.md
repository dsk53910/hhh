# HHH Bot - HH.ru Job Monitoring & Telegram Bot

An automated job monitoring system for hh.ru (HeadHunter Russia) with intelligent response capabilities and a Telegram bot for management and notifications.

## Features

- 🔍 **Automated job monitoring** from hh.ru with configurable search criteria
- 🤖 **Telegram bot** for management and notifications
- 📊 **Auto-apply capabilities** with approval workflow
- 📈 **Analytics and job market insights**
- ⚙️ **YAML-based configuration** for search criteria and responses
- 🎯 **AI-powered personalized response generation**

## Quick Start

```bash
# Install dependencies
uv sync

# Activate virtual environment
source .venv/bin/activate

# Copy environment configuration
cp .env.example .env

# Edit .env with your tokens and settings

# Run database migrations
alembic upgrade head

# Start the bot
python src/bot/main.py
```

## Configuration

All configuration is managed through:
- `.env` - Environment variables and secrets
- `config/config.yaml` - Main application settings
- `config/search_criteria.yaml` - Job search filters
- `config/responses.yaml` - Response templates

## Development

```bash
# Install development dependencies
uv sync --group dev

# Run tests
pytest

# Code formatting
black src/
ruff check src/

# Type checking
mypy src/
```

## Project Structure

```
src/
├── bot/           # Telegram bot handlers and logic
├── core/          # Database, configuration, scheduling
├── services/      # Business logic (hh.ru, responses, analytics)
├── models/        # SQLAlchemy data models
└── utils/         # Helper functions and logging
```

## License

MIT License