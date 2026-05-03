#!/usr/bin/env python3
"""
LinguaStart — Локальный воркер (запускается на ПК с GPU)
1. Опрашивает Railway бот на наличие заданий
2. Генерирует видео через Stable Diffusion (GPU)
3. Отправляет готовые видео прямо в Telegram
4. Сообщает боту об успехе / ошибке
"""

import os
import sys
import asyncio
import aiohttp
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

sys.path.insert(0, str(Path(__file__).parent))
from generate_videos_via_stable_diffusion import StableDiffusionVideoGenerator

# ─── Конфиг ──────────────────────────────────────────────────────────────────
BOT_TOKEN    = os.getenv("TELEGRAM_BOT_TOKEN", "")
RAILWAY_URL  = os.getenv("RAILWAY_URL", "").rstrip("/")   # напр. https://xxx.up.railway.app
POLL_INTERVAL = int(os.getenv("WORKER_POLL_SEC", "10"))   # проверять каждые 10 сек
OUTPUT_DIR   = Path(__file__).parent.parent / "output" / "videos"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

if not BOT_TOKEN:
    print("❌ TELEGRAM_BOT_TOKEN не задан в .env")
    sys.exit(1)
if not RAILWAY_URL:
    print("❌ RAILWAY_URL не задан в .env")
    print("   Пример: RAILWAY_URL=https://langapp-automation.up.railway.app")
    sys.exit(1)

TITLES = [
    "🇬🇧 Английский язык",
    "🇸🇦 Арабский язык",
    "🚀 Преимущества LinguaStart",
]

# ─── Telegram API ─────────────────────────────────────────────────────────────
TG_API = f"https://api.telegram.org/bot{BOT_TOKEN}"


async def tg_send_message(session: aiohttp.ClientSession, chat_id: int, text: str):
    await session.post(f"{TG_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
    })


async def tg_send_video(
    session: aiohttp.ClientSession,
    chat_id: int,
    video_path: Path,
    caption: str,
):
    data = aiohttp.FormData()
    data.add_field("chat_id",         str(chat_id))
    data.add_field("caption",         caption)
    data.add_field("parse_mode",      "Markdown")
    data.add_field("supports_streaming", "true")
    data.add_field(
        "video",
        open(video_path, "rb"),
        filename=video_path.name,
        content_type="video/mp4",
    )
    async with session.post(f"{TG_API}/sendVideo", data=data) as resp:
        result = await resp.json()
        if not result.get("ok"):
            print(f"   ⚠️  Telegram sendVideo error: {result}")
        return result


# ─── Railway API ──────────────────────────────────────────────────────────────
async def fetch_job(session: aiohttp.ClientSession) -> dict | None:
    try:
        async with session.get(f"{RAILWAY_URL}/jobs/pending", timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            return data if data.get("job_id") else None
    except Exception as e:
        print(f"   ⚠️  Не могу связаться с Railway: {e}")
        return None


async def complete_job(
    session: aiohttp.ClientSession,
    job_id: str,
    success: bool,
    error: str = "",
):
    try:
        await session.post(f"{RAILWAY_URL}/jobs/complete", json={
            "job_id":  job_id,
            "success": success,
            "error":   error,
        })
    except Exception as e:
        print(f"   ⚠️  Не могу отправить результат в Railway: {e}")


# ─── Генерация + отправка ─────────────────────────────────────────────────────
async def process_job(job: dict, generator: StableDiffusionVideoGenerator):
    job_id  = job["job_id"]
    chat_id = job["chat_id"]
    prompts = job.get("prompts", [])

    print(f"\n{'─' * 50}")
    print(f"📋 Задание #{job_id} | chat_id={chat_id}")
    print(f"   Видео: {len(prompts)} шт.")
    print(f"{'─' * 50}")

    async with aiohttp.ClientSession() as session:

        # Уведомляем пользователя о старте
        await tg_send_message(
            session, chat_id,
            f"🎬 *Задание #{job_id} запущено!*\n\n"
            f"⏳ Генерирую {len(prompts)} видео на GPU...\n"
            f"Это займёт около {len(prompts) * 3}–{len(prompts) * 5} минут."
        )

        generated_videos = []

        for idx, prompt in enumerate(prompts, 1):
            title = TITLES[idx - 1] if idx <= len(TITLES) else f"Видео {idx}"
            print(f"\n🖼️  [{idx}/{len(prompts)}] {title}")

            # Прогресс-колбэк → уведомление в Telegram (раз в 30%)
            last_pct_sent = [0]

            def make_callback(idx=idx, title=title):
                async def _async_cb(info):
                    pct = info.get("progress", 0)
                    msg = info.get("message", "")
                    if pct - last_pct_sent[0] >= 30 or info.get("status") in ("COMPLETE", "ERROR"):
                        last_pct_sent[0] = pct
                        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
                        async with aiohttp.ClientSession() as s:
                            await tg_send_message(
                                s, chat_id,
                                f"🎬 *Видео {idx}/{len(prompts)}: {title}*\n"
                                f"`[{bar}] {pct}%`\n{msg}"
                            )

                def sync_cb(info):
                    try:
                        loop = asyncio.get_event_loop()
                        if loop.is_running():
                            asyncio.ensure_future(_async_cb(info))
                        else:
                            loop.run_until_complete(_async_cb(info))
                    except Exception:
                        pass
                return sync_cb

            # Генерируем в thread pool (SD синхронный)
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                lambda p=prompt, cb=make_callback(): generator.generate_video(p, str(OUTPUT_DIR), cb)
            )

            if result["success"]:
                generated_videos.append((title, Path(result["url"])))
                print(f"   ✅ {Path(result['url']).name}")
            else:
                print(f"   ❌ Ошибка: {result['error']}")
                await tg_send_message(
                    session, chat_id,
                    f"⚠️ Видео {idx} не сгенерировано: `{result['error'][:200]}`"
                )

        # Отправляем готовые видео
        if generated_videos:
            for title, video_path in generated_videos:
                if video_path.exists():
                    print(f"📤 Отправляю: {video_path.name}")
                    await tg_send_video(
                        session, chat_id, video_path,
                        caption=f"{title}\n\n📲 Готово для TikTok / Instagram Reels! 🚀"
                    )

            await tg_send_message(
                session, chat_id,
                f"✅ *Задание #{job_id} выполнено!*\n\n"
                f"Отправлено *{len(generated_videos)}* видео.\n"
                f"Загружай на TikTok/Reels! 🚀"
            )
            await complete_job(session, job_id, success=True)
        else:
            await complete_job(session, job_id, success=False, error="Ни одно видео не сгенерировано")


# ─── Основной цикл ────────────────────────────────────────────────────────────
async def main():
    print(f"\n{'=' * 55}")
    print(f"🖥️  LinguaStart Local Worker запущен")
    print(f"{'=' * 55}")
    print(f"✅ Railway URL : {RAILWAY_URL}")
    print(f"✅ Bot token   : {BOT_TOKEN[:30]}...")
    print(f"✅ Output dir  : {OUTPUT_DIR}")
    print(f"✅ Poll interval: {POLL_INTERVAL} сек")
    print(f"{'=' * 55}")
    print(f"\nОжидание заданий... (Ctrl+C для остановки)\n")

    # Загружаем модель заранее (чтобы не ждать при первом задании)
    print("🔄 Предзагрузка модели Stable Diffusion...")
    generator = StableDiffusionVideoGenerator()
    generator._load_pipeline()
    print("✅ Модель готова!\n")

    async with aiohttp.ClientSession() as session:
        while True:
            job = await fetch_job(session)

            if job:
                try:
                    await process_job(job, generator)
                except Exception as e:
                    print(f"❌ Критическая ошибка при обработке задания: {e}")
                    async with aiohttp.ClientSession() as s:
                        await complete_job(s, job["job_id"], success=False, error=str(e))
            else:
                print(".", end="", flush=True)
                await asyncio.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⛔ Воркер остановлен.")
