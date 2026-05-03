#!/bin/bash
set -e

echo "=============================="
echo "LinguaStart Bot v3.0 - Railway"
echo "=============================="
echo "TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo "TELEGRAM_ADMIN_ID:  ${TELEGRAM_ADMIN_ID}"
echo "PORT:               ${PORT}"
echo "=============================="

python bot/telegram_bot_grok_v3.py
