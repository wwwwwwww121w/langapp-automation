#!/usr/bin/env python3
"""
Анализируем Runway интерфейс через Fireworks AI.
Потом напишем Playwright автоматизацию.
"""

import sys
import os
import json
from dotenv import load_dotenv
from openai import OpenAI

# Загружаем переменные окружения
load_dotenv()

# Инициализируем Fireworks клиент
api_key = os.getenv("FIREWORKS_API_KEY")
if not api_key:
    raise ValueError("FIREWORKS_API_KEY не найден в .env файле")

client = OpenAI(
    api_key=api_key,
    base_url="https://api.fireworks.ai/inference/v1"
)

def analyze_runway_with_fireworks():
    """Используем Fireworks для анализа Runway интерфейса"""

    print("\n📊 АНАЛИЗ RUNWAY ЧЕРЕЗ FIREWORKS")
    print("=" * 80)

    prompt = """
Ты эксперт по веб-автоматизации и Runway.com платформе для видео-генерации.

Дай мне ТОЧНУЮ и ПОДРОБНУЮ информацию о Runway интерфейсе для создания видео:

## 1. ВХОД В СИСТЕМУ
- URL для авторизации: https://app.runwayml.com/login
- URL для видео-генерации: https://app.runwayml.com/projects
- Нужна ли авторизация? ДА
- Как получить доступ? Нужен бесплатный или платный аккаунт

## 2. ИНТЕРФЕЙС ГЕНЕРАЦИИ ВИДЕО
Опиши точно:
- Какая кнопка "Create video" или "New project"?
- Какой выбрать модель для текст-в-видео? (Gen-3, Gen-2, и т.д.)
- Какие поля ввода есть?
  * Input: текст описания (обязательно)
  * Duration: длительность (секунды)
  * Aspect ratio: формат (16:9, 9:16, 1:1)
  * Style: стиль видео
  * Negative prompt: что избегать
- Значения по умолчанию?

## 3. ПРИМЕРЫ ЗАПОЛНЕНИЯ
Для видео "Arабские цифры от 1 до 5":
- Текст для ввода: ?
- Рекомендуемая длительность: ?
- Лучший стиль: ?
- Рекомендации: ?

## 4. КНОПКИ И ДЕЙСТВИЯ
- Кнопка "Generate" или "Create"?
- Индикатор прогресса генерации?
- Статусы: (Queued, Processing, Completed)?
- Кнопка скачивания результата?
- Откуда скачивается файл?

## 5. СЕЛЕКТОРЫ ДЛЯ PLAYWRIGHT
Дай CSS/XPath селекторы для:
- Поля ввода текста (textarea или input)
- Кнопки "Generate"
- Элемента с результатом видео
- Кнопки скачивания

## 6. АЛЬТЕРНАТИВНЫЙ ДОСТУП
- Есть ли REST API для автоматизации?
- Есть ли webhook для уведомления о завершении?
- URL для API документации?

Дай информацию в формате JSON для удобства парсинга.
"""

    # Используем доступную модель из конфига
    model = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/minimax-m2p7")

    print("\n🔄 Отправляю запрос к Fireworks...")
    print(f"Модель: {model}")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Ты эксперт по веб-автоматизации и Runway платформе. Дай точные, практические ответы."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.3,  # Более детерминированный ответ
        max_tokens=4000
    )

    analysis = response.choices[0].message.content

    print("\n✅ АНАЛИЗ RUNWAY:")
    print("=" * 80)
    print(analysis)
    print("=" * 80)

    # Сохраняем анализ
    with open('runway_interface_analysis.txt', 'w', encoding='utf-8') as f:
        f.write("АНАЛИЗ RUNWAY ИНТЕРФЕЙСА\n")
        f.write("=" * 80 + "\n\n")
        f.write(analysis)
        f.write("\n\n" + "=" * 80 + "\n")

    print("\n💾 Анализ сохранен в runway_interface_analysis.txt")

    return analysis


def create_playwright_template(analysis):
    """Создаем шаблон Playwright скрипта на основе анализа"""

    template = '''#!/usr/bin/env python3
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
'''

    with open('runway_playwright_template.py', 'w') as f:
        f.write(template)

    print("\n📄 Шаблон Playwright сохранен в runway_playwright_template.py")
    print("   (Селекторы нужно уточнить на основе анализа)")


if __name__ == "__main__":
    print("\n🎬 АНАЛИЗ RUNWAY И СОЗДАНИЕ PLAYWRIGHT СКРИПТА")
    print("=" * 80)

    # Анализируем Runway
    analysis = analyze_runway_with_fireworks()

    # Создаем шаблон Playwright
    print("\n" + "=" * 80)
    print("📝 Создаю шаблон Playwright скрипта...")
    create_playwright_template(analysis)

    print("\n" + "=" * 80)
    print("✅ ГОТОВО!")
    print("=" * 80)
    print("\nСледующие шаги:")
    print("1. Прочитайте runway_interface_analysis.txt")
    print("2. Откройте runway_playwright_template.py")
    print("3. Обновите селекторы на основе анализа")
    print("4. Протестируйте автоматизацию")
