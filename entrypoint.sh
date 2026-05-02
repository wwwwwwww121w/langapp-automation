#!/bin/bash
set -e

# Debug: Print actual environment variables passed by Railway
echo "DEBUG: Environment variables from Railway:"
echo "DEBUG: TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}"
echo "DEBUG: TELEGRAM_ADMIN_ID=${TELEGRAM_ADMIN_ID}"
echo "DEBUG: XAI_API_KEY=${XAI_API_KEY:0:20}..."

# Run the bot with all inherited environment variables
python bot/telegram_bot_grok_v3.py
