#!/bin/bash
set -e

# Export all environment variables that Railway might have passed
export TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN:- TELEGRAM_BOT_TOKEN}
export TELEGRAM_ADMIN_ID=${TELEGRAM_ADMIN_ID:-0}
export XAI_API_KEY=${XAI_API_KEY:-}
export XAI_VIDEO_MODEL=${XAI_VIDEO_MODEL:-grok-imagine-video}
export XAI_VIDEO_DURATION=${XAI_VIDEO_DURATION:-8}
export XAI_VIDEO_ASPECT_RATIO=${XAI_VIDEO_ASPECT_RATIO:-9:16}
export XAI_VIDEO_RESOLUTION=${XAI_VIDEO_RESOLUTION:-720p}
export FIREWORKS_API_KEY=${FIREWORKS_API_KEY:-}

# Print debug info
echo "DEBUG: Starting Telegram Bot"
echo "DEBUG: TELEGRAM_BOT_TOKEN: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo "DEBUG: TELEGRAM_ADMIN_ID: $TELEGRAM_ADMIN_ID"
echo "DEBUG: XAI_API_KEY: ${XAI_API_KEY:0:20}..."

# Run the bot
python bot/telegram_bot_grok_v3.py
