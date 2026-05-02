#!/usr/bin/env python3
"""
LinguaStart Telegram Bot - Video Farm
Generates videos on request and sends results via Telegram
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

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)
from telegram.constants import ChatAction, ParseMode

from config import (
    FIREWORKS_API_KEY,
    FIREWORKS_BASE_URL,
    FIREWORKS_MODEL_QUALITY,
    DATA_DIR,
    APP_NAME,
)

# Load Telegram config from environment
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_ID = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))

# Conversation states
AWAITING_COUNT = 1

# Paths
VIDEOS_DIR = Path(__file__).parent / "output" / "videos"
LOGS_DIR = Path(__file__).parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# Job tracking
JOBS = {}  # {user_id: {status, count, progress, job_id}}


def log_message(user_id: int, message: str):
    """Log bot interactions"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOGS_DIR / "telegram_bot.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{timestamp}] User {user_id}: {message}\n")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start command - show welcome message"""
    user_id = update.effective_user.id
    log_message(user_id, "Used /start command")

    welcome_text = f"""
🚀 Добро пожаловать в {APP_NAME} Video Farm!

Это закрытая ферма по генерации видео для обучения арабскому языку.

Доступные команды:
/generate - Начать генерацию видео
/status - Статус текущей задачи
/videos - Список созданных видео
/help - Справка

Введите /generate чтобы начать!
"""
    await update.message.reply_text(welcome_text)


async def generate_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start video generation process - ask for count"""
    user_id = update.effective_user.id
    log_message(user_id, "Started /generate command")

    # Check if already processing
    if user_id in JOBS and JOBS[user_id].get("status") == "processing":
        await update.message.reply_text(
            "⏳ У вас уже идёт процесс генерации видео. Подождите его завершения.\n\n"
            "Проверьте статус: /status"
        )
        return ConversationHandler.END

    text = (
        "📹 Сколько видео вы хотите сгенерировать?\n\n"
        "Введите число (1-20):"
    )
    await update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
    return AWAITING_COUNT


async def generate_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Receive count and start generation"""
    user_id = update.effective_user.id
    text = update.message.text.strip()

    # Validate input
    try:
        count = int(text)
        if count < 1 or count > 20:
            await update.message.reply_text(
                "❌ Пожалуйста, введите число от 1 до 20"
            )
            return AWAITING_COUNT
    except ValueError:
        await update.message.reply_text(
            "❌ Введите корректное число (например: 5)"
        )
        return AWAITING_COUNT

    log_message(user_id, f"Requested generation of {count} videos")

    # Start generation job
    job_id = str(int(time.time() * 1000))
    JOBS[user_id] = {
        "status": "processing",
        "count": count,
        "progress": 0,
        "job_id": job_id,
        "start_time": datetime.now(),
    }

    await update.message.reply_text(
        f"🎬 Начинаю генерацию {count} видео...\n"
        f"ID задачи: {job_id}\n\n"
        f"Проверяйте статус: /status"
    )

    # Run generation asynchronously
    context.application.create_task(
        run_generation_pipeline(update, context, user_id, count, job_id)
    )

    return ConversationHandler.END


async def run_generation_pipeline(
    update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, count: int, job_id: str
):
    """Run the full video generation pipeline"""
    try:
        await context.bot.send_chat_action(
            chat_id=user_id, action=ChatAction.TYPING
        )

        # Step 1: Generate scenarios
        await context.bot.send_message(
            chat_id=user_id,
            text="⏳ Этап 1/3: Генерация сценариев...",
        )
        JOBS[user_id]["progress"] = 1

        result = subprocess.run(
            [sys.executable, "scripts/01_generate_scenarios.py"],
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
            text="⏳ Этап 2/3: Создание кадров...",
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
            text="⏳ Этап 3/3: Монтаж видео...",
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
                text=f"✅ Успешно! Сгенерировано {len(video_files)} видео.\n\n"
                f"Отправляю файлы...",
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

                    await asyncio.sleep(0.5)  # Rate limiting

                except Exception as e:
                    log_message(user_id, f"Failed to send video {video_file.name}: {e}")
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=f"⚠️ Ошибка при отправке {video_file.name}",
                    )

            # Final summary
            elapsed = (datetime.now() - JOBS[user_id]["start_time"]).total_seconds()
            await context.bot.send_message(
                chat_id=user_id,
                text=f"🎉 Готово!\n\n"
                f"📊 Статистика:\n"
                f"  • Видео: {len(video_files)}\n"
                f"  • Время: {elapsed:.0f}с\n"
                f"  • ID: {job_id}",
            )

            JOBS[user_id]["status"] = "completed"
            log_message(user_id, f"Generation completed: {len(video_files)} videos in {elapsed:.0f}s")

        else:
            await context.bot.send_message(
                chat_id=user_id,
                text="❌ Ошибка: видео не были созданы. Проверьте логи.",
            )
            JOBS[user_id]["status"] = "failed"

    except asyncio.TimeoutError:
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Timeout: генерация заняла слишком много времени",
        )
        JOBS[user_id]["status"] = "timeout"
        log_message(user_id, "Generation timeout")

    except Exception as e:
        error_msg = str(e)
        log_message(user_id, f"Generation error: {error_msg}")
        await context.bot.send_message(
            chat_id=user_id,
            text=f"❌ Ошибка при генерации видео:\n{error_msg}",
        )
        JOBS[user_id]["status"] = "error"


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check status of video generation"""
    user_id = update.effective_user.id

    if user_id not in JOBS:
        await update.message.reply_text("📭 Нет активных задач. Начните с /generate")
        return

    job = JOBS[user_id]
    status_text = job.get("status", "unknown")

    if status_text == "processing":
        progress_map = {1: "Генерация сценариев", 2: "Создание кадров", 3: "Монтаж видео"}
        current_step = progress_map.get(job.get("progress", 0), "Подготовка")
        elapsed = (datetime.now() - job["start_time"]).total_seconds()

        status_msg = (
            f"⏳ Обработка...\n\n"
            f"Этап: {current_step}\n"
            f"Видео: {job.get('count', '?')}\n"
            f"Время: {elapsed:.0f}с"
        )

    elif status_text == "completed":
        elapsed = (datetime.now() - job["start_time"]).total_seconds()
        status_msg = (
            f"✅ Готово!\n\n"
            f"Видео: {job.get('count', '?')}\n"
            f"Время: {elapsed:.0f}с\n"
            f"ID: {job.get('job_id', '?')}"
        )

    elif status_text == "failed":
        status_msg = "❌ Ошибка при генерации. Попробуйте снова."

    else:
        status_msg = f"📊 Статус: {status_text}"

    await update.message.reply_text(status_msg)


async def list_videos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List all generated videos"""
    user_id = update.effective_user.id
    log_message(user_id, "Used /videos command")

    video_files = sorted(
        VIDEOS_DIR.glob("*.mp4"),
        key=lambda x: x.stat().st_mtime,
        reverse=True,
    )

    if not video_files:
        await update.message.reply_text("📭 Видео ещё не созданы.")
        return

    videos_text = f"📹 Доступные видео ({len(video_files)}):\n\n"
    for i, video_file in enumerate(video_files[:20], 1):
        size_kb = video_file.stat().st_size / 1024
        mod_time = datetime.fromtimestamp(video_file.stat().st_mtime)
        videos_text += f"{i}. {video_file.name} ({size_kb:.0f}KB) - {mod_time.strftime('%H:%M')}\n"

    await update.message.reply_text(videos_text)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show help message"""
    user_id = update.effective_user.id
    log_message(user_id, "Used /help command")

    help_text = f"""
🚀 {APP_NAME} Video Farm - Справка

📝 Команды:
/generate - Начать генерацию видео
/status - Статус текущей задачи
/videos - Список видео
/help - Эта справка
/cancel - Отменить текущую операцию

💡 Как использовать:
1. Отправьте /generate
2. Укажите количество видео (1-20)
3. Ждите результата
4. Видео будут отправлены в чат

⚙️ Настройки:
- Максимум 20 видео за задачу
- Формат: MP4 (1080x1920)
- Язык: Арабский + Английский

❓ Вопросы? Свяжитесь с администратором.
"""
    await update.message.reply_text(help_text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    user_id = update.effective_user.id
    log_message(user_id, "Used /cancel command")

    if user_id in JOBS and JOBS[user_id].get("status") == "processing":
        # Note: We can't actually kill the process, but we can mark it as cancelled
        await update.message.reply_text(
            "⚠️ Текущая задача уже в обработке. "
            "Дождитесь её завершения или используйте /status"
        )
    else:
        await update.message.reply_text("✅ Нет активных задач для отмены.")


async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Log errors and notify admin"""
    error_msg = f"Update {update}: {context.error}"
    print(f"Error: {error_msg}")
    log_message(0, f"ERROR: {error_msg}")

    if TELEGRAM_ADMIN_ID:
        try:
            await context.bot.send_message(
                chat_id=TELEGRAM_ADMIN_ID,
                text=f"🚨 Bot Error:\n{error_msg[:200]}",
            )
        except Exception as e:
            print(f"Failed to notify admin: {e}")


def main():
    """Main bot entry point"""
    if not TELEGRAM_BOT_TOKEN:
        print("❌ Error: TELEGRAM_BOT_TOKEN not set in .env file")
        print("\n📋 Setup Instructions:")
        print("1. Create a bot with @BotFather in Telegram")
        print("2. Copy the token and add to .env file:")
        print("   TELEGRAM_BOT_TOKEN=your_token_here")
        print("3. Get your user ID from @userinfobot")
        print("4. Add to .env file:")
        print("   TELEGRAM_ADMIN_ID=your_user_id")
        print("5. Run this script again")
        sys.exit(1)

    print(f"🚀 Starting {APP_NAME} Video Farm Bot...")
    print(f"📱 Bot Token: {TELEGRAM_BOT_TOKEN[:20]}...")

    # Create application
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Conversation handler for generation
    generate_handler = ConversationHandler(
        entry_points=[CommandHandler("generate", generate_start)],
        states={
            AWAITING_COUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, generate_count),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(generate_handler)
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("videos", list_videos))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("cancel", cancel))

    # Error handler
    app.add_error_handler(error_handler)

    # Start bot
    print(f"✅ Bot started successfully!")
    print(f"📝 Command: /start")
    print(f"📝 Logs: {LOGS_DIR}/telegram_bot.log")
    print(f"\nPress Ctrl+C to stop the bot\n")

    app.run_polling()


if __name__ == "__main__":
    main()
