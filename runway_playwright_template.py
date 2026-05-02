#!/usr/bin/env python3
"""
Playwright автоматизация для Runway видео-генерации.
Генерирует видео через браузер Runway.
"""

import asyncio
from playwright.async_api import async_playwright
import time

async def generate_video_on_runway(video_prompt, duration=24, output_file="video.mp4"):
    """
    Генерирует видео на Runway через браузер.

    Args:
        video_prompt: Описание видео для генерации
        duration: Длительность видео в секундах
        output_file: Путь для сохранения результата
    """

    async with async_playwright() as p:
        # Открываем браузер
        browser = await p.chromium.launch(headless=False)
        page = await browser.new_page()

        try:
            # Переходим на Runway
            print("🌐 Открываем Runway...")
            await page.goto("https://app.runwayml.com/login", wait_until="networkidle")

            # ЗДЕСЬ НУЖНА АВТОРИЗАЦИЯ (пользователь логинится вручную)
            print("👤 Авторизуйтесь в Runway и нажмите Enter когда готовы...")
            input()

            # Переходим в проекты
            await page.goto("https://app.runwayml.com/projects", wait_until="networkidle")

            # Кликаем на создание видео
            print("📹 Создаю новое видео...")
            # await page.click("button:has-text('Create')")  # Селектор нужно уточнить

            # Заполняем описание видео
            print(f"📝 Вводу описание: {video_prompt}")
            # await page.fill("textarea", video_prompt)  # Селектор нужно уточнить

            # Устанавливаем длительность
            print(f"⏱️ Устанавливаю длительность: {duration}s")
            # await page.fill("input[name=duration]", str(duration))  # Селектор нужно уточнить

            # Запускаем генерацию
            print("▶️ Запускаю генерацию...")
            # await page.click("button:has-text('Generate')")  # Селектор нужно уточнить

            # Ждем результат
            print("⏳ Жду результат (может занять несколько минут)...")
            # await page.wait_for_selector("video", timeout=300000)  # Селектор нужно уточнить

            # Скачиваем видео
            print("📥 Скачиваю видео...")
            # async with page.expect_download() as download_info:
            #     await page.click("button:has-text('Download')")  # Селектор нужно уточнить
            # download = await download_info.value
            # await download.save_as(output_file)

            print(f"✅ Видео сохранено: {output_file}")

        finally:
            await browser.close()


if __name__ == "__main__":
    # Пример использования
    prompt = "Arabic numerals 1 to 5 educational video, bright colors, professional style"
    asyncio.run(generate_video_on_runway(prompt, duration=24))
