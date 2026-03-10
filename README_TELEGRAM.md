# How to Create a Telegram Bot and Get Your IDs

To run this application, you need a Telegram Bot Token and your own Telegram User ID (so the bot knows you are the admin and can send you messages).

## 1. Getting a Bot Token
1. Open Telegram on your phone or computer.
2. Search for the user **@BotFather** (this is the official Telegram bot creator).
3. Send the command `/newbot`.
4. BotFather will ask for a **Name** for your bot (e.g., "My Job Scanner").
5. BotFather will then ask for a **Username** for your bot. It must end in `bot` (e.g., `my_hhh_scanner_bot`).
6. Once created, BotFather will give you a **Token**. It looks something like this:
   `1234567890:AAH_aBcDeFgHiJkLmNoPqRsTuVwXyZ`
7. **Keep this token secret.**

## 2. Getting Your Admin ID
Your Telegram ID is a unique number assigned to your account.

1. In Telegram, search for the user **@userinfobot** or **@RawDataBot**.
2. Send the command `/start` to it.
3. The bot will reply with your account information.
4. Look for the `Id` line (it will be a number like `123456789` or `987654321`).
5. This is your **ADMIN_ID**.

## 3. Configuring the Bot
Create a file named `.env` in the root of your project folder (next to `pyproject.toml`) and add the following lines:

```env
BOT_TOKEN="your_token_from_botfather"
ADMIN_ID="your_id_from_userinfobot"
DATABASE_URL="sqlite+aiosqlite:///test.db"
SECRET_KEY="super_secret_key_123"
```

You can now start the bot using:
```bash
uv run python src/bot/main.py
```
