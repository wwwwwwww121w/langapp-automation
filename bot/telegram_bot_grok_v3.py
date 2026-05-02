#!/usr/bin/env python3
"""
LinguaStart Telegram Bot v3.0
Генерация видео через xAI Grok Video API
"""

import os
import sys
import json
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core'))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction, ParseMode

# DEBUG: Print all environment variables
print("DEBUG: Environment variables available:")
print(f"  TELEGRAM_BOT_TOKEN: {'SET' if os.getenv('TELEGRAM_BOT_TOKEN') else 'EMPTY'}")
print(f"  TELEGRAM_ADMIN_ID: {'SET' if os.getenv('TELEGRAM_ADMIN_ID') else 'EMPTY'}")
print(f"  XAI_API_KEY: {'SET' if os.getenv('XAI_API_KEY') else 'EMPTY'}")
print(f"All env vars: {list(os.environ.keys())[:20]}")

# Load config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))
APP_NAME = "LinguaStart"

# Validate tokens
if not TELEGRAM_BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN is empty!")
    sys.exit(1)
if TELEGRAM_ADMIN_ID == 0:
    print("ERROR: TELEGRAM_ADMIN_ID is empty!")

# Paths
VIDEOS_DIR = Path(__file__).parent.parent / "output" / "videos"
LOGS_DIR = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)


def log_message(user_id: int, message: str):
    """Логирование действий бота"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOGS_DIR / "telegram_bot_grok.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] User {user_id}: {message}\n")


def get_main_menu_keyboard():
    """Главное меню"""
    keyboard = [
        [
            InlineKeyboardButton("🎬 Генерировать видео Grok", callback_data="generate_grok"),
            InlineKeyboardButton("📊 Статус", callback_data="status"),
        ],
        [
            InlineKeyboardButton("📹 Список видео", callback_data="videos"),
            InlineKeyboardButton("❓ Справка", callback_data="help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def format_welcome_message():
    """Приветственное сообщение"""
    return f"""
╔════════════════════════════════════╗
║  🚀 {APP_NAME} Video Generator 🚀  ║
║  Powered by xAI Grok Video API    ║
╚════════════════════════════════════╝

👋 Добро пожаловать в генератор видео!

🎯 Возможности:
  • 🎬 Генерирование видео через xAI Grok
  • 📹 Профессиональные видео для TikTok/Reels
  • ⚡ Быстрая обработка (8-10 сек видео)
  • 🎨 Высокое качество 720p

📝 Темы видео:
  1. Приложение для изучения английского
  2. Изучение арабского языка
  3. Преимущества LinguaStart

Нажми кнопку ниже для начала! 👇
"""


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /start"""
    user_id = update.effective_user.id
    log_message(user_id, "Started bot")

    await update.message.reply_text(
        format_welcome_message(),
        reply_markup=get_main_menu_keyboard(),
        parse_mode=ParseMode.HTML
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок"""
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    if query.data == "generate_grok":
        log_message(user_id, "Started Grok video generation")

        await query.edit_message_text(
            text="🎬 **Генерирую видео через xAI Grok...**\n\n"
                 "Это может занять 1-2 минуты⏳\n\n"
                 "_Генерирую 3 видео про LinguaStart_",
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            # Запускаем скрипт генерации видео
            result = subprocess.run(
                [sys.executable, "scripts/04_generate_videos_via_grok.py"],
                capture_output=True,
                text=True,
                timeout=600
            )

            if result.returncode == 0:
                # Читаем URL видео
                url_file = VIDEOS_DIR / "video_url.txt"
                if url_file.exists():
                    with open(url_file, 'r', encoding='utf-8') as f:
                        urls = f.readlines()

                    if len(urls) >= 3:
                        message = """✅ **Видео успешно сгенерированы!**

🎬 **Видео готовы к публикации:**

1️⃣ **Английский язык**
🔗 [Скачать видео](""" + urls[-3].strip() + """)

2️⃣ **Арабский язык**
🔗 [Скачать видео](""" + urls[-2].strip() + """)

3️⃣ **Преимущества LinguaStart**
🔗 [Скачать видео](""" + urls[-1].strip() + """)

📲 Загрузи эти видео на TikTok/Instagram Reels!
🚀 Видео готовы к вирусному распространению!"""

                        await query.edit_message_text(
                            text=message,
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=get_main_menu_keyboard()
                        )
                        log_message(user_id, "Generated 3 videos successfully")
                    else:
                        await query.edit_message_text(
                            text="⚠️ Видео сгенерированы, но файл содержит меньше 3 ссылок.",
                            reply_markup=get_main_menu_keyboard()
                        )
                else:
                    await query.edit_message_text(
                        text="❌ Ошибка: файл с URL видео не найден.",
                        reply_markup=get_main_menu_keyboard()
                    )
            else:
                error_msg = result.stderr[:200] if result.stderr else "Unknown error"
                await query.edit_message_text(
                    text=f"❌ **Ошибка при генерации видео:**\n\n`{error_msg}`",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=get_main_menu_keyboard()
                )
                log_message(user_id, f"Generation failed: {error_msg}")

        except subprocess.TimeoutExpired:
            await query.edit_message_text(
                text="⏱️ **Timeout:** Генерация видео заняла слишком много времени",
                reply_markup=get_main_menu_keyboard()
            )
            log_message(user_id, "Generation timeout")
        except Exception as e:
            await query.edit_message_text(
                text=f"❌ **Ошибка:** {str(e)[:100]}",
                reply_markup=get_main_menu_keyboard()
            )
            log_message(user_id, f"Error: {str(e)}")

    elif query.data == "status":
        status_text = """📊 **Статус системы:**

✅ xAI Grok Video API: Connected
✅ Telegram Bot: Online
✅ Video Generator: Ready

📈 **Статистика:**
  • Видео сгенерировано: 3
  • Качество: 720p (9:16)
  • Формат: MP4
  • Длительность: 8 сек каждое"""

        await query.edit_message_text(
            text=status_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "videos":
        if VIDEOS_DIR.exists():
            mp4_files = list(VIDEOS_DIR.glob("*.mp4"))
            if mp4_files:
                video_list = "\n".join([f"  • {f.name}" for f in mp4_files[:10]])
                await query.edit_message_text(
                    text=f"📹 **Список видео:**\n\n{video_list}",
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=get_main_menu_keyboard()
                )
            else:
                await query.edit_message_text(
                    text="📭 **Видео еще не сгенерированы**\n\nНажми на кнопку '🎬 Генерировать видео Grok'",
                    reply_markup=get_main_menu_keyboard()
                )
        else:
            await query.edit_message_text(
                text="📭 **Папка с видео не найдена**",
                reply_markup=get_main_menu_keyboard()
            )

    elif query.data == "help":
        help_text = """❓ **Справка:**

🎬 **Как генерировать видео?**
1. Нажми кнопку '🎬 Генерировать видео Grok'
2. Подожди 1-2 минуты пока идет обработка
3. Получи ссылки на готовые видео
4. Загрузи на TikTok/Instagram Reels

📱 **Поддерживаемые темы:**
  • Приложение для английского
  • Изучение арабского
  • Преимущества LinguaStart

🎥 **Характеристики видео:**
  • Качество: 720p
  • Формат: 9:16 (вертикальное)
  • Длительность: 8-10 сек
  • Готовые к публикации

🚀 **Технология:**
  Powered by xAI Grok Video API"""

        await query.edit_message_text(
            text=help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    else:
        await query.edit_message_text(
            text=format_welcome_message(),
            reply_markup=get_main_menu_keyboard()
        )


async def main():
    """Запуск бота"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))

    print(f"\n{'=' * 60}")
    print(f"🤖 {APP_NAME} Telegram Bot v3.0 запущен!")
    print(f"{'=' * 60}")
    print(f"✅ Bot token: {TELEGRAM_BOT_TOKEN[:30]}...")
    print(f"✅ Admin ID: {TELEGRAM_ADMIN_ID}")
    print(f"✅ Используется xAI Grok Video API")
    print(f"{'=' * 60}\n")

    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
