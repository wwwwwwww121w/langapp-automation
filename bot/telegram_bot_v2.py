#!/usr/bin/env python3
"""
LinguaStart Telegram Video Farm Bot v2.0
Enhanced version with UI, inline buttons, and better interface
"""

import os
import sys
import json
import asyncio
import subprocess
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction, ParseMode

from config import APP_NAME

# Load Telegram config
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))

# Conversation states
AWAITING_COUNT = 1

# Paths
VIDEOS_DIR = Path(__file__).parent / "output" / "videos"
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Job tracking
JOBS = {}


def log_message(user_id: int, message: str):
    """Log bot interactions"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOGS_DIR / "telegram_bot.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] User {user_id}: {message}\n")


def get_main_menu_keyboard():
    """Get main menu keyboard with buttons"""
    keyboard = [
        [
            InlineKeyboardButton("🎬 Генерировать видео", callback_data="generate"),
            InlineKeyboardButton("📊 Статус", callback_data="status"),
        ],
        [
            InlineKeyboardButton("📹 Список видео", callback_data="videos"),
            InlineKeyboardButton("❓ Справка", callback_data="help"),
        ],
        [
            InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
            InlineKeyboardButton("📝 Логи", callback_data="logs"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_generate_count_keyboard():
    """Get keyboard for selecting video count"""
    keyboard = [
        [
            InlineKeyboardButton("1️⃣ 1", callback_data="count_1"),
            InlineKeyboardButton("5️⃣ 5", callback_data="count_5"),
            InlineKeyboardButton("🔟 10", callback_data="count_10"),
        ],
        [
            InlineKeyboardButton("2️⃣0️⃣ 20", callback_data="count_20"),
            InlineKeyboardButton("✏️ Своё число", callback_data="count_custom"),
        ],
        [
            InlineKeyboardButton("❌ Отмена", callback_data="cancel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def format_welcome_message():
    """Format welcome message with emoji and styling"""
    return f"""
╔══════════════════════════════════════╗
║     🚀 {APP_NAME} Video Farm 🚀     ║
║   Закрытая ферма по генерации видео  ║
╚══════════════════════════════════════╝

👋 Добро пожаловать в {APP_NAME} Video Farm!

Это приватный сервис для генерации видео для обучения арабскому языку.

📊 **Возможности:**
  🎬 Генерируйте 1-20 видео по требованию
  📹 Видео доставляются прямо в Телеграм
  🔒 Закрытая система - только вы имеете доступ
  ⚡ Быстрая обработка
  📊 Отслеживание статуса в реальном времени

**Выберите действие из меню ниже 👇**
"""


def format_status_message(user_id: int):
    """Format status message"""
    if user_id not in JOBS:
        return "📭 **Нет активных задач**\n\nНажмите на кнопку \"🎬 Генерировать видео\" для начала"

    job = JOBS[user_id]
    status = job.get("status", "unknown")

    if status == "processing":
        progress = job.get("progress", 0)
        steps = ["Генерация сценариев", "Создание кадров", "Монтаж видео"]
        current_step = steps[progress - 1] if progress > 0 else "Подготовка"
        elapsed = (datetime.now() - job["start_time"]).total_seconds()

        # Progress bar
        filled = "█" * progress + "░" * (3 - progress)
        progress_bar = f"[{filled}] {progress}/3"

        return f"""
⏳ **Обработка видео...**

📊 **Статус:**
  Этап: {current_step}
  Видео: {job.get('count', '?')}
  Время: {elapsed:.0f}сек

  Прогресс: {progress_bar}

Ждите завершения...
"""

    elif status == "completed":
        elapsed = (datetime.now() - job["start_time"]).total_seconds()
        return f"""
✅ **Готово!**

📊 **Статистика:**
  ✓ Видео: {job.get('count', '?')}
  ✓ Время: {elapsed:.0f}сек
  ✓ ID: {job.get('job_id', '?')}

🎉 Видео успешно созданы и отправлены!

Хотите сгенерировать еще? Нажмите на кнопку "🎬 Генерировать видео"
"""

    elif status == "failed":
        return """
❌ **Ошибка при генерации**

Что-то пошло не так. Попробуйте снова или проверьте логи.

Нажмите на кнопку "🎬 Генерировать видео" для повтора
"""

    else:
        return f"📊 **Статус:** {status}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command with main menu"""
    user_id = update.effective_user.id
    log_message(user_id, "Used /start command")

    welcome_msg = format_welcome_message()

    await update.message.reply_text(
        welcome_msg,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_main_menu_keyboard()
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button clicks"""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()

    if query.data == "generate":
        log_message(user_id, "Clicked generate button")

        if user_id in JOBS and JOBS[user_id].get("status") == "processing":
            await query.edit_message_text(
                "⏳ **У вас уже идет процесс генерации!**\n\n"
                "Дождитесь завершения или проверьте статус.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_main_menu_keyboard()
            )
            return

        text = (
            "🎬 **Сколько видео вы хотите сгенерировать?**\n\n"
            "Выберите из предложенных вариантов или введите свое число (1-20):"
        )
        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_generate_count_keyboard()
        )
        context.user_data["generating"] = True
        return AWAITING_COUNT

    elif query.data.startswith("count_"):
        count_str = query.data.replace("count_", "")

        if count_str == "custom":
            await query.edit_message_text(
                "✏️ **Введите число видео (1-20):**",
                parse_mode=ParseMode.MARKDOWN
            )
            context.user_data["generating"] = True
            return AWAITING_COUNT

        count = int(count_str)
        await start_generation(update, context, user_id, count, query)
        return ConversationHandler.END

    elif query.data == "status":
        log_message(user_id, "Clicked status button")
        status_msg = format_status_message(user_id)
        await query.edit_message_text(
            status_msg,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "videos":
        log_message(user_id, "Clicked videos button")
        video_files = sorted(
            VIDEOS_DIR.glob("*.mp4"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        if not video_files:
            text = "📭 **Видео еще не созданы**\n\nНажмите на кнопку \"🎬 Генерировать видео\""
        else:
            text = f"📹 **Доступные видео ({len(video_files)}):**\n\n"
            for i, video_file in enumerate(video_files[:10], 1):
                size_mb = video_file.stat().st_size / (1024 * 1024)
                mod_time = datetime.fromtimestamp(video_file.stat().st_mtime)
                text += f"{i}. `{video_file.name}` ({size_mb:.1f}MB)\n"

            if len(video_files) > 10:
                text += f"\n... и ещё {len(video_files) - 10} видео"

        await query.edit_message_text(
            text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "help":
        log_message(user_id, "Clicked help button")
        help_text = """
❓ **СПРАВКА - Доступные команды:**

🎬 **Генерировать видео**
  Начать процесс создания видео
  Выберите количество: 1-20

📊 **Статус**
  Проверить статус текущей генерации
  Увидеть прогресс и время

📹 **Список видео**
  Посмотреть все созданные видео
  Информация о размере и времени

⚙️ **Настройки**
  Дополнительные параметры

📝 **Логи**
  Просмотр логов ошибок

---

⏱️ **Время генерации:**
  • 1 видео: ~4 минуты
  • 5 видео: ~7 минут
  • 10 видео: ~12 минут
  • 20 видео: ~19 минут

🔐 **Безопасность:**
  ✓ Приватный бот - только вы имеете доступ
  ✓ Видео генерируются локально
  ✓ Никаких данных в облаке
"""
        await query.edit_message_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "settings":
        log_message(user_id, "Clicked settings button")
        settings_text = """
⚙️ **НАСТРОЙКИ**

📊 **Текущие параметры:**
  • Макс видео за раз: 20
  • Формат: MP4 (1080x1920)
  • Язык: Арабский + Английский
  • Качество: Высокое

🔧 **Для изменения настроек:**
  Отредактируйте файл: config.py

📁 **Папки:**
  • Видео: output/videos/
  • Данные: data/
  • Логи: logs/
"""
        await query.edit_message_text(
            settings_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "logs":
        log_message(user_id, "Clicked logs button")
        log_file = LOGS_DIR / "telegram_bot.log"

        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
                recent_logs = "".join(lines[-10:])  # Last 10 lines

            logs_text = f"""
📝 **ПОСЛЕДНИЕ ЛОГИ (10 строк):**

```
{recent_logs}
```
"""
        else:
            logs_text = "📝 **Логи еще не созданы**\n\nЗапустите генерацию видео для создания логов"

        await query.edit_message_text(
            logs_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    elif query.data == "cancel":
        await query.edit_message_text(
            format_welcome_message(),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )
        return ConversationHandler.END


async def start_generation(update, context, user_id: int, count: int, query=None):
    """Start video generation"""
    if count < 1 or count > 20:
        if query:
            await query.edit_message_text(
                "❌ **Пожалуйста, введите число от 1 до 20**",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_generate_count_keyboard()
            )
        return AWAITING_COUNT

    log_message(user_id, f"Started generation of {count} videos")

    job_id = str(int(time.time() * 1000))
    JOBS[user_id] = {
        "status": "processing",
        "count": count,
        "progress": 0,
        "job_id": job_id,
        "start_time": datetime.now(),
    }

    starting_message = f"""
🚀 **Начинаю генерацию {count} видео...**

📊 **Информация:**
  ID задачи: `{job_id}`
  Видео: {count} шт.
  Примерное время: {int(4 + count * 0.5)} минут

⏳ Это может занять некоторое время. Проверяйте статус!
"""

    if query:
        await query.edit_message_text(
            starting_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )
    else:
        await context.bot.send_message(
            chat_id=user_id,
            text=starting_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

    # Run generation asynchronously
    context.application.create_task(
        run_generation_pipeline(context, user_id, count, job_id)
    )

    return ConversationHandler.END


async def run_generation_pipeline(context, user_id: int, count: int, job_id: str):
    """Run the full video generation pipeline"""
    try:
        await context.bot.send_chat_action(chat_id=user_id, action=ChatAction.TYPING)

        # Step 1: Generate scenarios
        await context.bot.send_message(
            chat_id=user_id,
            text="⏳ **Этап 1/3:** Генерация сценариев...",
            parse_mode=ParseMode.MARKDOWN,
        )
        JOBS[user_id]["progress"] = 1

        result = subprocess.run(
            [sys.executable, "scripts/01_generate_scenarios_grok.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            raise Exception(f"Scenario generation failed: {result.stderr}")

        # Step 2: Generate frames
        await context.bot.send_message(
            chat_id=user_id,
            text="⏳ **Этап 2/3:** Создание кадров...",
            parse_mode=ParseMode.MARKDOWN,
        )
        JOBS[user_id]["progress"] = 2

        result = subprocess.run(
            [sys.executable, "scripts/02_generate_frames.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=300,
        )

        if result.returncode != 0:
            raise Exception(f"Frame generation failed: {result.stderr}")

        # Step 3: Assemble videos
        await context.bot.send_message(
            chat_id=user_id,
            text="⏳ **Этап 3/3:** Монтаж видео...",
            parse_mode=ParseMode.MARKDOWN,
        )
        JOBS[user_id]["progress"] = 3

        result = subprocess.run(
            [sys.executable, "scripts/03_assemble_videos.py"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            timeout=600,
        )

        if result.returncode != 0:
            raise Exception(f"Video assembly failed: {result.stderr}")

        # Get generated videos
        video_files = sorted(
            VIDEOS_DIR.glob("*.mp4"),
            key=lambda x: x.stat().st_mtime,
            reverse=True,
        )

        # Send videos to user
        if video_files:
            await context.bot.send_message(
                chat_id=user_id,
                text=f"✅ **Успешно!** Сгенерировано {len(video_files)} видео.\n\n📤 Отправляю файлы на ваш компьютер...",
                parse_mode=ParseMode.MARKDOWN,
            )

            # Send videos with captions
            for i, video_file in enumerate(video_files[:count], 1):
                try:
                    await context.bot.send_chat_action(
                        chat_id=user_id, action=ChatAction.UPLOAD_VIDEO
                    )

                    file_size_mb = video_file.stat().st_size / (1024 * 1024)

                    with open(video_file, "rb") as f:
                        await context.bot.send_video(
                            chat_id=user_id,
                            video=f,
                            caption=f"#{i} {video_file.name} ({file_size_mb:.1f}MB)",
                            write_timeout=300,
                        )

                    await asyncio.sleep(0.5)

                except Exception as e:
                    log_message(user_id, f"Failed to send video {video_file.name}: {e}")
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"⚠️ Ошибка при отправке {video_file.name}",
                    )

            # Final summary
            elapsed = (datetime.now() - JOBS[user_id]["start_time"]).total_seconds()
            summary_text = f"""
🎉 **ВСЕ ГОТОВО!**

📊 **Статистика:**
  ✓ Видео сгенерировано: {len(video_files)}
  ✓ Время выполнения: {elapsed:.0f} сек ({elapsed/60:.1f} мин)
  ✓ ID задачи: `{job_id}`

💾 **Видео сохранены в:** `output/videos/`

Хотите создать еще видео? Нажмите на кнопку "🎬 Генерировать видео"
"""

            await context.bot.send_message(
                chat_id=user_id,
                text=summary_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_main_menu_keyboard()
            )

            JOBS[user_id]["status"] = "completed"
            log_message(user_id, f"Generation completed: {len(video_files)} videos in {elapsed:.0f}s")

        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ **Ошибка:** Видео не были созданы. Проверьте логи.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_main_menu_keyboard()
            )
            JOBS[user_id]["status"] = "failed"

    except Exception as e:
        error_msg = str(e)
        log_message(user_id, f"Generation error: {error_msg}")

        error_text = f"""
❌ **Ошибка при генерации видео:**

```
{error_msg[:200]}
```

Пожалуйста, попробуйте снова или проверьте логи.
"""

        await context.bot.send_message(
            chat_id=user_id,
            text=error_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )
        JOBS[user_id]["status"] = "error"


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages for custom count input"""
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if not context.user_data.get("generating"):
        return

    try:
        count = int(text)
        if count < 1 or count > 20:
            await update.message.reply_text(
                "❌ **Пожалуйста, введите число от 1 до 20**",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_generate_count_keyboard()
            )
            return AWAITING_COUNT

        log_message(user_id, f"Requested generation of {count} videos (custom)")

        job_id = str(int(time.time() * 1000))
        JOBS[user_id] = {
            "status": "processing",
            "count": count,
            "progress": 0,
            "job_id": job_id,
            "start_time": datetime.now(),
        }

        starting_message = f"""
🚀 **Начинаю генерацию {count} видео...**

📊 **Информация:**
  ID: `{job_id}`
  Видео: {count} шт.
  Время: ~{int(4 + count * 0.5)} минут

⏳ Ждите завершения!
"""

        await update.message.reply_text(
            starting_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard()
        )

        context.application.create_task(
            run_generation_pipeline(context, user_id, count, job_id)
        )

        return ConversationHandler.END

    except ValueError:
        await update.message.reply_text(
            "❌ **Введите корректное число (от 1 до 20)**",
            parse_mode=ParseMode.MARKDOWN,
        )
        return AWAITING_COUNT


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors"""
    error_msg = f"Update {update}: {context.error}"
    print(f"Error: {error_msg}")
    log_message(0, f"ERROR: {error_msg}")


def main():
    """Main bot entry point"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен в .env файле")
        print("\n📋 Инструкция:")
        print("1. Создайте бота с @BotFather в Телеграме")
        print("2. Копируйте токен и добавьте в .env файл:")
        print("   TELEGRAM_BOT_TOKEN=your_token_here")
        print("3. Получите ваш ID от @userinfobot")
        print("4. Добавьте в .env файл:")
        print("   TELEGRAM_ADMIN_ID=your_user_id")
        sys.exit(1)

    print(f"🚀 Запуск {APP_NAME} Video Farm Bot v2.0...")
    print(f"📱 Токен: {TELEGRAM_BOT_TOKEN[:20]}...")

    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(button_callback, pattern="^generate$"),
        ],
        states={
            AWAITING_COUNT: [
                CallbackQueryHandler(button_callback, pattern="^count_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message),
            ],
        },
        fallbacks=[
            CallbackQueryHandler(button_callback, pattern="^cancel$"),
        ],
    )

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(conv_handler)
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_error_handler(error_handler)

    print(f"✅ Бот запущен успешно!")
    print(f"📝 Логи: {LOGS_DIR}/telegram_bot.log")
    print(f"\n🤖 Бот готов к использованию!")
    print(f"💬 Откройте Телеграм и отправьте /start вашему боту\n")

    app.run_polling()


if __name__ == "__main__":
    main()
