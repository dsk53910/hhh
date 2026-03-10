# Testing the Bot

To test the bot locally:

1. Copy `.env.example` to `.env` (or create one):
   ```
   BOT_TOKEN="your_telegram_bot_token"
   ADMIN_ID="your_telegram_id"
   DATABASE_URL="sqlite+aiosqlite:///test.db"
   SECRET_KEY="dummy_secret_for_now"
   ```
2. Run the main file:
   ```
   uv run src/bot/main.py
   ```
