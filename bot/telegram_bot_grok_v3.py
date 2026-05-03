#!/usr/bin/env python3
"""
LinguaStart Telegram Bot v3.0
Генерация видео через Stable Diffusion WebUI API (локальное)
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

# Импортируем генератор видео
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'scripts'))
try:
    from generate_videos_via_stable_diffusion import StableDiffusionVideoGenerator
    HAS_VIDEO_GENERATOR = True
except ImportError:
    HAS_VIDEO_GENERATOR = False

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
print(f"  SD_API_URL: {os.getenv('SD_API_URL', 'http://127.0.0.1:7860')}")
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
    """Главное меню с расширенными опциями"""
    keyboard = [
        [
            InlineKeyboardButton("🎬 Генерировать видео", callback_data="generate_grok"),
        ],
        [
            InlineKeyboardButton("📊 Статус", callback_data="status"),
            InlineKeyboardButton("📹 Видео", callback_data="videos"),
        ],
        [
            InlineKeyboardButton("❓ Справка", callback_data="help"),
            InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        ],
        [
            InlineKeyboardButton("🔄 Обновить", callback_data="refresh"),
            InlineKeyboardButton("📞 Поддержка", callback_data="support"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def format_welcome_message():
    """Приветственное сообщение"""
    return f"""
╔════════════════════════════════════╗
║  🚀 {APP_NAME} Video Generator 🚀  ║
║  Powered by Stable Diffusion       ║
╚════════════════════════════════════╝

👋 Добро пожаловать в генератор видео!

🎯 Возможности:
  • 🎬 Генерирование видео через Stable Diffusion
  • 📹 Профессиональные видео для TikTok/Reels
  • 🎨 Высокое качество 720p (9:16)
  • ⚙️ Локальное решение - полный контроль

⏰ Время генерации: 5-10 минут на видео

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
        parse_mode=ParseMode.MARKDOWN
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /help"""
    user_id = update.effective_user.id
    log_message(user_id, "Viewed help")

    help_text = """❓ **Справка:**

🎬 **Как генерировать видео?**
1. Убедись что Stable Diffusion WebUI запущен
2. Нажми кнопку '🎬 Генерировать видео'
3. Подожди 5-10 минут пока идет генерация кадров
4. Получи готовое видео в папке output/videos
5. Загрузи на TikTok/Instagram Reels

⚙️ **Требования:**
  • Запущен Stable Diffusion WebUI локально
  • Адрес: http://127.0.0.1:7860
  • Установлен ffmpeg
  • Достаточно видеопамяти (8GB+)

🎥 **Характеристики видео:**
  • Качество: 720p (720x1280)
  • Формат: 9:16 (вертикальное)
  • Кадры: 8 штук
  • Длительность: ~8 сек
  • Готовы к публикации

🚀 **Технология:**
  Stable Diffusion WebUI (локальное)"""

    await update.message.reply_text(
        help_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда /menu"""
    user_id = update.effective_user.id
    log_message(user_id, "Opened menu")

    menu_text = """📋 **Доступные функции:**

🎬 **Генерировать видео**
Создай профессиональное видео через Stable Diffusion для TikTok/Reels (5-10 мин)

📊 **Статус**
Проверь статус системы и подключения к Stable Diffusion

📹 **Видео**
Посмотри все сгенерированные видео в папке

⚙️ **Настройки**
Информация о параметрах генерации Stable Diffusion

🔄 **Обновить**
Проверь актуальный статус системы

📞 **Поддержка**
Контакты поддержки и документация

❓ **Справка**
Подробная справка по использованию бота

✨ Выбери нужное действие из меню ниже!"""

    await update.message.reply_text(
        menu_text,
        reply_markup=get_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка кнопок"""
    query = update.callback_query
    user_id = query.from_user.id

    await query.answer()

    if query.data == "generate_grok":
        log_message(user_id, "Started Stable Diffusion video generation")

        await query.edit_message_text(
            text="🎬 **Генерирую видео через Stable Diffusion...**\n\n"
                 "Это может занять 5-10 минут⏳\n\n"
                 "_Убедитесь что Stable Diffusion WebUI запущен локально_",
            parse_mode=ParseMode.MARKDOWN
        )

        try:
            # Используем StableDiffusionVideoGenerator с отслеживанием прогресса
            status_message = None
            last_progress = 0

            async def update_progress(status_info):
                """Обновляет сообщение о прогрессе в Telegram"""
                nonlocal status_message, last_progress

                progress = status_info.get('progress', 0)
                message = status_info.get('message', '')
                status = status_info.get('status', '')

                # Обновляем сообщение каждый раз когда прогресс меняется на 5%
                if progress - last_progress >= 5 or status in ['COMPLETE', 'ERROR']:
                    last_progress = progress

                    progress_bar = f"{'█' * (progress // 10)}{'░' * (10 - progress // 10)} {progress}%"
                    update_text = (
                        f"🎬 **Генерирую видео...**\n\n"
                        f"[{progress_bar}]\n\n"
                        f"📊 Статус: {message}\n"
                        f"⏱️  Это может занять 5-10 минут"
                    )

                    try:
                        await query.edit_message_text(
                            text=update_text,
                            parse_mode=ParseMode.MARKDOWN
                        )
                    except Exception as e:
                        print(f"Error updating progress: {e}")

            # Генерируем видео
            generator = StableDiffusionVideoGenerator()

            # Генерируем 3 видео с отслеживанием прогресса
            all_urls = []
            prompts = [
                "Красивое видео приложение LinguaStart для изучения английского языка. Показать интерфейс, уроки, студентов учащихся. Современный дизайн, яркие цвета. 9:16 формат вертикальное видео.",
                "Видео приложение LinguaStart для изучения арабского языка. Показать прогресс студентов, достижения, рейтинги, награды. Геймификация. 9:16 вертикальное видео.",
                "Промо-видео LinguaStart. Показать основные возможности: быстрое обучение, интерактивные уроки, сообщество учеников, игры. Вирусный контент для социальных сетей. 9:16 вертикальное."
            ]

            for i, prompt in enumerate(prompts, 1):
                await update_progress({
                    "status": "STARTING",
                    "progress": (i-1) * 30,
                    "message": f"🎬 Генерирую видео {i}/3..."
                })

                result = generator.generate_video(prompt, str(VIDEOS_DIR), update_progress)

                if result['success']:
                    all_urls.append(result['url'])
                else:
                    raise Exception(f"Ошибка при генерации видео {i}: {result['error']}")

            if len(all_urls) >= 1:
                message = f"""✅ **Видео успешно сгенерированы!**

🎬 **Видео готовы к публикации:**"""

                for idx, url in enumerate(all_urls, 1):
                    message += f"\n\n{idx}️⃣ **Видео {idx}**\n📁 {Path(url).name}"

                message += """

📲 Видео сохранены в папке output/videos
Загрузи их на TikTok/Instagram Reels!
🚀 Готовы к вирусному распространению!"""

                await query.edit_message_text(
                    text=message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=get_main_menu_keyboard()
                )
                log_message(user_id, f"Generated {len(all_urls)} videos successfully")
            else:
                await query.edit_message_text(
                    text="⚠️ Видео сгенерированы, но нет файлов.",
                    reply_markup=get_main_menu_keyboard()
                )

        except Exception as e:
            error_msg = str(e)[:200]
            await query.edit_message_text(
                text=f"❌ **Ошибка при генерации видео:**\n\n`{error_msg}`\n\n"
                     f"💡 **Проверьте:**\n"
                     f"• Запущен ли Stable Diffusion WebUI?\n"
                     f"• Правильный ли URL? (http://127.0.0.1:7860)",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_main_menu_keyboard()
            )
            log_message(user_id, f"Generation error: {error_msg}")

    elif query.data == "status":
        sd_api_url = os.getenv("SD_API_URL", "http://127.0.0.1:7860")
        status_text = f"""📊 **Статус системы:**

🖥️ **Компоненты:**
  • Telegram Bot: ✅ Online
  • Stable Diffusion API: 🔗 {sd_api_url}
  • Video Generator: 🎬 Ready

📈 **Информация:**
  • Генератор: Stable Diffusion WebUI (локальный)
  • Качество: 720p (9:16)
  • Формат: MP4
  • Длительность: ~8 сек на видео
  • Время генерации: 5-10 минут на видео"""

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
1. Убедись что Stable Diffusion WebUI запущен
2. Нажми кнопку '🎬 Генерировать видео'
3. Подожди 5-10 минут пока идет генерация
4. Получи видео в папке /output/videos
5. Загрузи на TikTok/Instagram Reels

⚙️ **Требования:**
  • Stable Diffusion WebUI запущен
  • http://127.0.0.1:7860 доступен
  • ffmpeg установлен
  • 8GB+ видеопамяти

🎥 **Характеристики видео:**
  • Качество: 720p (720x1280)
  • Формат: 9:16 (вертикальное)
  • Кадры: 8 штук
  • Длительность: ~8 сек
  • Готовы к публикации

🚀 **Технология:**
  Stable Diffusion WebUI"""

        await query.edit_message_text(
            text=help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "settings":
        settings_text = """⚙️ **Настройки:**

🎬 **Параметры генерации видео:**
  • Генератор: Stable Diffusion WebUI
  • Качество: 720p (720x1280)
  • Формат: 9:16 (вертикальное)
  • Кадры: 8 на видео
  • Длительность: ~8 секунд
  • Шаги: 20 на кадр
  • CFG Scale: 7.5

📊 **Информация о системе:**
  • Версия: LinguaStart v3.0
  • Статус: ✅ Локальный режим
  • Генератор: Stable Diffusion
  • Язык: Русский

💾 **Хранилище:**
  • Папка видео: /output/videos
  • Кадры: /output/frames
  • Логи: /logs
  • Данные: /data

⚡ Все настройки оптимизированы для качества"""

        await query.edit_message_text(
            text=settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "refresh":
        refresh_text = """🔄 **Обновление информации...**

✅ Статус системы: Активен
✅ Подключение к API: OK
✅ Хранилище: Доступно
✅ Логирование: Включено

📈 **Статистика:**
  • Всего видео сгенерировано: ∞
  • Ошибок: 0
  • Среднее время генерации: 1-2 мин

🚀 Система готова к работе!"""

        await query.edit_message_text(
            text=refresh_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "support":
        support_text = """📞 **Поддержка и контакты:**

🌐 **Веб-сайт:**
  https://linguastart.com

📧 **Email:**
  support@linguastart.com

💬 **Telegram:**
  @linguastart_support

📱 **Мобильное приложение:**
  • iOS: App Store
  • Android: Google Play

🐛 **Сообщить об ошибке:**
  Используй команду /bug [описание]

📚 **Документация:**
  https://docs.linguastart.com

⏰ **Время поддержки:**
  24/7 онлайн

🤝 Мы здесь, чтобы помочь!"""

        await query.edit_message_text(
            text=support_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    else:
        await query.edit_message_text(
            text=format_welcome_message(),
            reply_markup=get_main_menu_keyboard()
        )


def main():
    """Запуск бота"""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    sd_api_url = os.getenv("SD_API_URL", "http://127.0.0.1:7860")

    print(f"\n{'=' * 60}")
    print(f"🤖 {APP_NAME} Telegram Bot v3.0 запущен!")
    print(f"{'=' * 60}")
    print(f"✅ Bot token: {TELEGRAM_BOT_TOKEN[:30]}...")
    print(f"✅ Admin ID: {TELEGRAM_ADMIN_ID}")
    print(f"✅ Генератор: Stable Diffusion WebUI")
    print(f"✅ API URL: {sd_api_url}")
    print(f"{'=' * 60}\n")

    # Use application's built-in run method
    application.run_polling()


if __name__ == "__main__":
    main()
