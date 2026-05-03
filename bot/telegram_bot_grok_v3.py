#!/usr/bin/env python3
"""
LinguaStart Telegram Bot v3.0
Railway — принимает команды и держит очередь заданий.
Генерация видео — на локальном ПК через local_worker.py
"""

import os
import sys
import json
import uuid
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from aiohttp import web

load_dotenv()

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode

# ─── Конфиг ─────────────────────────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_ADMIN_ID  = int(os.getenv("TELEGRAM_ADMIN_ID", "0"))
PORT               = int(os.getenv("PORT", "8080"))
APP_NAME           = "LinguaStart"

if not TELEGRAM_BOT_TOKEN:
    print("ERROR: TELEGRAM_BOT_TOKEN не задан!")
    sys.exit(1)

print(f"DEBUG: TOKEN={'SET' if TELEGRAM_BOT_TOKEN else 'EMPTY'} | ADMIN={TELEGRAM_ADMIN_ID}")

# ─── Пути ────────────────────────────────────────────────────────────────────
VIDEOS_DIR = Path(__file__).parent.parent / "output" / "videos"
LOGS_DIR   = Path(__file__).parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)
VIDEOS_DIR.mkdir(parents=True, exist_ok=True)

# ─── Очередь заданий (в памяти Railway) ──────────────────────────────────────
# job_id → {chat_id, user_id, prompts, status, created_at}
pending_jobs: dict = {}

# Сохраняем глобальный bot объект чтобы воркер мог уведомлять пользователей
_bot: Optional[Bot] = None

PROMPTS = [
    "Beautiful language learning app LinguaStart interface for English, "
    "modern UI design, bright colors, vertical 9:16 format, students learning, "
    "high quality professional video.",

    "LinguaStart app for Arabic language learning, student progress, "
    "achievements, gamification, vertical 9:16 format, modern design.",

    "LinguaStart promo video, fast learning, interactive lessons, "
    "community, games, viral social media content, 9:16 vertical format.",
]


# ─── Утилиты ─────────────────────────────────────────────────────────────────
def log(user_id: int, msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_file = LOGS_DIR / "bot.log"
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(f"[{ts}] User {user_id}: {msg}\n")


def get_main_menu_keyboard():
    keyboard = [
        [InlineKeyboardButton("🎬 Генерировать видео", callback_data="generate")],
        [
            InlineKeyboardButton("📊 Статус",    callback_data="status"),
            InlineKeyboardButton("📹 Видео",     callback_data="videos"),
        ],
        [
            InlineKeyboardButton("❓ Справка",   callback_data="help"),
            InlineKeyboardButton("⚙️ Настройки", callback_data="settings"),
        ],
        [
            InlineKeyboardButton("🔄 Обновить",  callback_data="refresh"),
            InlineKeyboardButton("📞 Поддержка", callback_data="support"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def welcome_text():
    return (
        f"╔══════════════════════════════════╗\n"
        f"║  🚀 {APP_NAME} Video Generator 🚀  ║\n"
        f"║  Powered by Stable Diffusion      ║\n"
        f"╚══════════════════════════════════╝\n\n"
        f"👋 Добро пожаловать!\n\n"
        f"🎯 *Как работает:*\n"
        f"  1️⃣ Нажми «🎬 Генерировать видео»\n"
        f"  2️⃣ Задание уходит в очередь\n"
        f"  3️⃣ ПК с GPU генерирует видео\n"
        f"  4️⃣ Видео приходит прямо сюда\n\n"
        f"⏰ Время генерации: 3–5 мин (GPU)\n\n"
        f"Нажми кнопку ниже! 👇"
    )


# ─── Telegram handlers ────────────────────────────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log(update.effective_user.id, "start")
    await update.message.reply_text(
        welcome_text(),
        reply_markup=get_main_menu_keyboard(),
        parse_mode=ParseMode.MARKDOWN,
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log(update.effective_user.id, "help")
    text = (
        "❓ *Справка*\n\n"
        "🎬 *Генерация видео:*\n"
        "1. Нажми «🎬 Генерировать видео»\n"
        "2. Задание попадает в очередь на Railway\n"
        "3. Запусти воркер на ПК с GPU:\n"
        "   `python scripts/local_worker.py`\n"
        "4. Видео придёт прямо в этот чат\n\n"
        "🎥 *Параметры видео:*\n"
        "  • 720p, формат 9:16 (вертикальное)\n"
        "  • 8 кадров ≈ 8 сек\n"
        "  • Stable Diffusion + ffmpeg\n\n"
        "🚀 *Технология:* Stable Diffusion (GPU)"
    )
    await update.message.reply_text(
        text, reply_markup=get_main_menu_keyboard(), parse_mode=ParseMode.MARKDOWN
    )


async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    log(update.effective_user.id, "menu")
    text = (
        "📋 *Доступные функции:*\n\n"
        "🎬 *Генерировать видео* — создать 3 видео для TikTok/Reels\n"
        "📊 *Статус* — очередь и состояние системы\n"
        "📹 *Видео* — список готовых видео\n"
        "⚙️ *Настройки* — параметры генерации\n"
        "🔄 *Обновить* — перезапросить статус\n"
        "📞 *Поддержка* — связаться с командой\n\n"
        "✨ Выбери действие:"
    )
    await update.message.reply_text(
        text, reply_markup=get_main_menu_keyboard(), parse_mode=ParseMode.MARKDOWN
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query    = update.callback_query
    user_id  = query.from_user.id
    chat_id  = query.message.chat_id
    await query.answer()

    # ── ГЕНЕРАЦИЯ ──────────────────────────────────────────────────────────
    if query.data == "generate":
        log(user_id, "generate requested")

        # Проверяем — нет ли уже активного задания для этого пользователя
        active = [j for j in pending_jobs.values()
                  if j["user_id"] == user_id and j["status"] in ("pending", "processing")]
        if active:
            await query.edit_message_text(
                text="⏳ *У вас уже есть задание в очереди!*\n\nПодождите завершения текущей генерации.",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_main_menu_keyboard(),
            )
            return

        job_id = str(uuid.uuid4())[:8].upper()
        pending_jobs[job_id] = {
            "job_id":     job_id,
            "chat_id":    chat_id,
            "user_id":    user_id,
            "prompts":    PROMPTS,
            "status":     "pending",
            "created_at": datetime.now().isoformat(),
        }

        log(user_id, f"job created: {job_id}")

        await query.edit_message_text(
            text=(
                f"✅ *Задание #{job_id} принято!*\n\n"
                f"📋 Будет сгенерировано *3 видео* про LinguaStart\n\n"
                f"*Запустите воркер на ПК с GPU:*\n"
                f"`python scripts/local_worker.py`\n\n"
                f"⏰ Видео придут сюда через 3–5 минут после запуска воркера."
            ),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_main_menu_keyboard(),
        )

    # ── СТАТУС ─────────────────────────────────────────────────────────────
    elif query.data in ("status", "refresh"):
        total   = len(pending_jobs)
        pending = sum(1 for j in pending_jobs.values() if j["status"] == "pending")
        proc    = sum(1 for j in pending_jobs.values() if j["status"] == "processing")
        done    = sum(1 for j in pending_jobs.values() if j["status"] == "done")

        text = (
            f"📊 *Статус системы*\n\n"
            f"🌐 *Railway бот:* ✅ Online\n"
            f"🖥️ *Воркер:* запустите `python scripts/local_worker.py`\n\n"
            f"📋 *Очередь заданий:*\n"
            f"  • Ожидают: {pending}\n"
            f"  • В работе: {proc}\n"
            f"  • Завершено: {done}\n"
            f"  • Всего: {total}\n\n"
            f"🤖 *Генератор:* Stable Diffusion\n"
            f"🎥 *Параметры:* 720p, 9:16, 8 кадров"
        )
        await query.edit_message_text(
            text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu_keyboard()
        )

    # ── ВИДЕО ──────────────────────────────────────────────────────────────
    elif query.data == "videos":
        mp4_files = list(VIDEOS_DIR.glob("*.mp4")) if VIDEOS_DIR.exists() else []
        if mp4_files:
            mp4_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
            files_text = "\n".join(f"  • {f.name}" for f in mp4_files[:10])
            text = f"📹 *Последние видео:*\n\n{files_text}"
        else:
            text = "📭 *Видео ещё не сгенерированы*\n\nНажми «🎬 Генерировать видео»"
        await query.edit_message_text(
            text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu_keyboard()
        )

    # ── СПРАВКА ────────────────────────────────────────────────────────────
    elif query.data == "help":
        text = (
            "❓ *Справка*\n\n"
            "🎬 *Как генерировать:*\n"
            "1. Нажми «🎬 Генерировать видео»\n"
            "2. Запусти на ПК: `python scripts/local_worker.py`\n"
            "3. Видео придут в этот чат автоматически\n\n"
            "⚙️ *Требования для воркера:*\n"
            "  • NVIDIA GPU 4GB+ VRAM\n"
            "  • ffmpeg в PATH\n"
            "  • Python пакеты из requirements.txt\n\n"
            "🎥 *Характеристики видео:*\n"
            "  • 720p, 9:16 (вертикальное)\n"
            "  • ~8 сек, MP4"
        )
        await query.edit_message_text(
            text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu_keyboard()
        )

    # ── НАСТРОЙКИ ──────────────────────────────────────────────────────────
    elif query.data == "settings":
        sd_model = os.getenv("SD_MODEL", "runwayml/stable-diffusion-v1-5")
        text = (
            f"⚙️ *Настройки*\n\n"
            f"🤖 *Модель:* `{sd_model}`\n"
            f"📐 *Разрешение:* 512×912 (9:16)\n"
            f"🖼️ *Кадров:* 8\n"
            f"🔢 *Шагов:* 25\n"
            f"🎚️ *CFG Scale:* 7.5\n"
            f"📦 *Планировщик:* DPMSolver++ Karras\n\n"
            f"💾 *Видео:* /output/videos\n"
            f"📝 *Логи:* /logs/bot.log"
        )
        await query.edit_message_text(
            text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu_keyboard()
        )

    # ── ПОДДЕРЖКА ──────────────────────────────────────────────────────────
    elif query.data == "support":
        text = (
            "📞 *Поддержка*\n\n"
            "🐛 Если что-то не работает:\n"
            "  1. Проверьте логи Railway\n"
            "  2. Убедитесь что воркер запущен\n"
            "  3. Проверьте VRAM GPU\n\n"
            "📚 *Документация:*\n"
            "  https://github.com/wwwwwwww121w/langapp-automation\n\n"
            "⏰ Поддержка: 24/7"
        )
        await query.edit_message_text(
            text=text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_main_menu_keyboard()
        )

    else:
        await query.edit_message_text(
            text=welcome_text(), reply_markup=get_main_menu_keyboard(), parse_mode=ParseMode.MARKDOWN
        )


# ─── HTTP сервер (очередь для воркера) ───────────────────────────────────────
async def http_get_jobs(request: web.Request) -> web.Response:
    """Воркер запрашивает следующее задание"""
    for job_id, job in pending_jobs.items():
        if job["status"] == "pending":
            job["status"] = "processing"
            return web.json_response(job)
    return web.json_response({"job_id": None})


async def http_complete_job(request: web.Request) -> web.Response:
    """Воркер сообщает о завершении задания"""
    global _bot
    try:
        data   = await request.json()
        job_id = data.get("job_id")
        success= data.get("success", False)
        error  = data.get("error", "")

        if job_id not in pending_jobs:
            return web.json_response({"ok": False, "error": "job not found"})

        job = pending_jobs[job_id]
        job["status"] = "done" if success else "error"

        # Уведомляем пользователя об ошибке (видео отправляет сам воркер)
        if not success and _bot:
            await _bot.send_message(
                chat_id=job["chat_id"],
                text=(
                    f"❌ *Задание #{job_id} завершилось с ошибкой:*\n\n"
                    f"`{error[:300]}`"
                ),
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=get_main_menu_keyboard(),
            )

        # Удаляем выполненные задания через 5 минут (не сразу, чтобы воркер не дублировал)
        async def cleanup():
            await asyncio.sleep(300)
            pending_jobs.pop(job_id, None)
        asyncio.create_task(cleanup())

        return web.json_response({"ok": True})

    except Exception as e:
        return web.json_response({"ok": False, "error": str(e)})


async def http_healthcheck(request: web.Request) -> web.Response:
    return web.json_response({
        "status": "ok",
        "bot": APP_NAME,
        "jobs_pending": sum(1 for j in pending_jobs.values() if j["status"] == "pending"),
        "jobs_processing": sum(1 for j in pending_jobs.values() if j["status"] == "processing"),
    })


async def start_http_server():
    app = web.Application()
    app.router.add_get ("/",              http_healthcheck)
    app.router.add_get ("/jobs/pending",  http_get_jobs)
    app.router.add_post("/jobs/complete", http_complete_job)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", PORT)
    await site.start()
    print(f"✅ HTTP сервер запущен на порту {PORT}")


# ─── Запуск ──────────────────────────────────────────────────────────────────
async def run_all():
    global _bot

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    _bot = application.bot

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help",  help_command))
    application.add_handler(CommandHandler("menu",  menu_command))
    application.add_handler(CallbackQueryHandler(button_callback))

    print(f"\n{'=' * 60}")
    print(f"🤖 {APP_NAME} Bot v3.0 запущен (Railway режим)")
    print(f"{'=' * 60}")
    print(f"✅ Admin ID : {TELEGRAM_ADMIN_ID}")
    print(f"✅ HTTP порт: {PORT}")
    print(f"{'=' * 60}\n")

    # Запускаем HTTP сервер параллельно с ботом
    await start_http_server()

    # Запускаем бота
    await application.initialize()
    await application.start()
    await application.updater.start_polling()

    # Держим процесс живым
    try:
        await asyncio.Event().wait()
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()


def main():
    asyncio.run(run_all())


if __name__ == "__main__":
    main()
