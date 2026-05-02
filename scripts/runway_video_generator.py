#!/usr/bin/env python3
"""
Runway видео-генератор через браузер + Playwright.

Интеграция:
1. Fireworks генерирует описание видео
2. Playwright автоматизирует Runway в браузере
3. Скачивает результат MP4
"""

import asyncio
import os
import sys
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI
from playwright.async_api import async_playwright, expect

# Загружаем переменные окружения
load_dotenv()


class RunwayVideoGenerator:
    """Генератор видео через Runway браузер"""

    def __init__(self):
        # Fireworks API
        api_key = os.getenv("FIREWORKS_API_KEY")
        if not api_key:
            raise ValueError("FIREWORKS_API_KEY не найден в .env")

        self.fireworks = OpenAI(
            api_key=api_key,
            base_url="https://api.fireworks.ai/inference/v1"
        )
        self.model = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/minimax-m2p7")

        # Runway API (если будет)
        self.runway_api_key = os.getenv("RUNWAY_API_KEY", "")

    def generate_video_description_with_fireworks(self, topic: str) -> dict:
        """Генерирует описание видео через Fireworks"""

        print(f"\n📝 Генерирую описание для видео: {topic}")

        prompt = f"""
Создай описание для обучающего видео про {topic} на арабском языке.

Верни JSON с полями:
{{
  "title": "Название видео",
  "description": "Подробное описание видео (для Runway)",
  "duration": 10,  // в секундах
  "style": "cinematic или minimal или educational",
  "aspect_ratio": "16:9 или 9:16",
  "hashtags": ["#learn", "#arabic"],
  "prompt_for_runway": "Точное описание для Runway (сфокусировано на визуальных элементах)"
}}

Примеры тем:
- Арабские цифры 1-5
- Приветствия на арабском
- Названия животных

Для {topic} создай оригинальное описание.
"""

        response = self.fireworks.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "Ты помощник для создания описаний обучающих видео на арабском языке. Верни JSON."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        content = response.choices[0].message.content

        # Извлекаем JSON
        try:
            # Ищем JSON в ответе
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                result = json.loads(json_str)
                print(f"✅ Описание готово:")
                print(f"   Название: {result.get('title')}")
                print(f"   Стиль: {result.get('style')}")
                return result
        except json.JSONDecodeError:
            print(f"⚠️ Не удалось распарсить JSON, используем текст как есть")

        return {
            "title": f"Video about {topic}",
            "description": content,
            "duration": 10,
            "style": "cinematic",
            "aspect_ratio": "16:9",
            "prompt_for_runway": content,
            "hashtags": ["#learn", "#arabic"]
        }

    async def generate_video_on_runway(self, video_description: dict, output_dir: str = "output/videos"):
        """Генерирует видео через Runway в браузере"""

        print(f"\n🎬 ГЕНЕРАЦИЯ ВИДЕО НА RUNWAY")
        print("=" * 70)

        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"runway_{int(time.time())}.mp4")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)  # Видим браузер
            page = await browser.new_page(viewport={"width": 1280, "height": 720})

            try:
                # 1. Переходим на Runway
                print("\n🌐 1. Открываю Runway (https://app.runwayml.com)...")
                await page.goto("https://app.runwayml.com", wait_until="networkidle")
                await page.wait_for_timeout(2000)

                # Проверяем авторизацию
                current_url = page.url
                if "login" in current_url:
                    print("👤 Требуется авторизация. Пожалуйста, авторизуйтесь в Runway")
                    print("   Нажмите Enter в консоли когда авторизуетесь...")
                    input()
                    await page.goto("https://app.runwayml.com/projects", wait_until="networkidle")
                    await page.wait_for_timeout(2000)

                print("✅ Авторизация подтверждена")

                # 2. Ищем кнопку создания нового проекта
                print("\n📁 2. Ищу кнопку создания видео...")

                create_found = False
                selectors = [
                    'button:has-text("Create")',
                    'button:has-text("Generate")',
                    'a:has-text("Create")',
                ]

                for selector in selectors:
                    try:
                        btn = page.locator(selector)
                        count = await btn.count()
                        if count > 0:
                            print(f"   ✓ Нашел кнопку: {selector} (найдено {count})")
                            try:
                                await btn.first().click()
                                print(f"   ✓ Кликнул успешно")
                                await page.wait_for_timeout(3000)
                                create_found = True
                                break
                            except Exception as click_err:
                                print(f"   ⚠️ Ошибка при клике: {click_err}")
                                continue
                        else:
                            print(f"   ℹ️ Селектор не найден: {selector}")
                    except Exception as e:
                        print(f"   ⚠️ Ошибка при проверке {selector}: {e}")
                        continue

                if not create_found:
                    print("   ⚠️ Не удалось найти и кликнуть на Create, делаю скриншот...")
                    await page.screenshot(path=f"{output_dir}/debug_no_create.png")
                    return None

                print(f"   ✓ Create успешно нажата")

                # 2.5. Выбираем тип видео (обычно "Film or shorts")
                print("\n🎬 2.5. Выбираю тип видео...")
                video_type_selectors = [
                    'text=Film or shorts',
                    'div:has-text("Film or shorts")',
                    '[role="button"]:has-text("Film or shorts")',
                    'button >> text=Film',
                ]

                type_selected = False
                for selector in video_type_selectors:
                    try:
                        type_btn = page.locator(selector)
                        if await type_btn.count() > 0:
                            print(f"   ✓ Выбираю тип видео: Film or shorts")
                            await type_btn.first().click()
                            await page.wait_for_timeout(3000)
                            type_selected = True
                            break
                    except Exception as e:
                        continue

                if not type_selected:
                    # Пробуем кликнуть на первый элемент если видим галерею
                    try:
                        first_option = page.locator('[role="button"]').first()
                        print(f"   ℹ️ Кликаю на первый доступный вариант")
                        await first_option.click()
                        await page.wait_for_timeout(3000)
                        type_selected = True
                        print(f"   ✓ Тип видео выбран")
                    except Exception as e:
                        print(f"   ⚠️ Не удалось выбрать тип видео: {e}")
                        await page.screenshot(path=f"{output_dir}/debug_no_type.png")
                        return None

                print(f"   ✓ Переходу к заполнению формы...")

                # 3. Заполняем форму
                print("\n📝 3. Заполняю форму для видео...")
                prompt = video_description.get("prompt_for_runway", "")

                # Ищем textarea для ввода промпта
                textarea_selectors = ['textarea', '[role="textbox"]', 'input[type="text"][placeholder*="prompt"]', 'input[type="text"][placeholder*="Prompt"]']

                textarea_filled = False
                for sel in textarea_selectors:
                    try:
                        textarea = page.locator(sel).first()
                        if await textarea.count() > 0:
                            await textarea.click()
                            await textarea.fill(prompt)
                            print(f"   ✓ Введен промпт ({sel})")
                            textarea_filled = True
                            break
                    except Exception as e:
                        continue

                if not textarea_filled:
                    print(f"   ⚠️ Не удалось заполнить поле для промпта")

                # 4. Устанавливаем параметры
                print("\n⚙️ 4. Устанавливаю параметры видео...")

                # Длительность
                duration = video_description.get("duration", 10)
                try:
                    duration_input = page.locator('input[type="number"], input[placeholder*="duration"]').first()
                    await duration_input.fill(str(duration))
                    print(f"   ✓ Длительность: {duration}s")
                except:
                    print(f"   ⚠️ Не удалось установить длительность")

                # 5. Запускаем генерацию
                print("\n▶️ 5. Запускаю генерацию...")
                gen_selectors = ['button:has-text("Generate")', 'button >> text=Generate', '[role="button"]:has-text("Generate")']

                gen_started = False
                for sel in gen_selectors:
                    try:
                        gen_btn = page.locator(sel)
                        if await gen_btn.count() > 0:
                            await gen_btn.first().click()
                            print(f"   ✓ Генерация запущена ({sel})")
                            await page.wait_for_timeout(3000)
                            gen_started = True
                            break
                    except Exception as e:
                        continue

                if not gen_started:
                    print(f"   ⚠️ Не удалось запустить генерацию")

                # 6. Ждем результат
                print("\n⏳ 6. Жду результата (может занять 2-5 минут)...")
                try:
                    # Ждем видео элемента
                    video_elem = page.locator('video')
                    if await video_elem.count() > 0:
                        await video_elem.first().wait_for(timeout=300000)  # 5 минут макс
                        print("   ✓ Видео готово!")
                    else:
                        # Пробуем ждать по изменению на странице
                        await page.wait_for_timeout(60000)  # Жди 1 минуту
                        print("   ℹ️ Прошла минута, проверяю наличие видео...")
                except Exception as e:
                    print(f"   ⚠️ Видео не сгенерировалось: {e}")

                # 7. Скачиваем результат
                print(f"\n📥 7. Скачиваю видео...")
                download_selectors = ['button:has-text("Download")', 'button >> text=Download', '[role="button"]:has-text("Download")']

                video_downloaded = False
                for sel in download_selectors:
                    try:
                        download_btn = page.locator(sel)
                        if await download_btn.count() > 0:
                            async with page.expect_download() as download_info:
                                await download_btn.first().click()

                            download = await download_info.value
                            await download.save_as(output_path)
                            print(f"   ✓ Видео сохранено: {output_path}")
                            video_downloaded = True
                            return output_path
                    except Exception as e:
                        continue

                if not video_downloaded:
                    print(f"   ⚠️ Не удалось скачать видео")
                    # Пробуем альтернативный способ - screenshot как доказательство
                    await page.screenshot(path=f"{output_path}.png")
                    print(f"   📸 Screenshot сохранен: {output_path}.png")

            finally:
                print("\n🔄 Закрываю браузер...")
                await browser.close()

        return None

    async def full_pipeline(self, topic: str):
        """Полный пайплайн: текст → описание → видео"""

        print("\n" + "=" * 70)
        print(f"🎬 ПОЛНЫЙ ПАЙПЛАЙН ГЕНЕРАЦИИ ВИДЕО")
        print(f"   Тема: {topic}")
        print("=" * 70)

        # Шаг 1: Генерируем описание через Fireworks
        video_desc = self.generate_video_description_with_fireworks(topic)

        # Шаг 2: Генерируем видео через Runway
        result = await self.generate_video_on_runway(video_desc)

        return result


async def main(topic=None):
    """Главная функция"""

    generator = RunwayVideoGenerator()

    # Примеры тем
    default_topics = [
        "LinguaStart - приложение для изучения английского и арабского языка",
        "Почему LinguaStart лучше всех конкурентов для учебы языкам",
        "Как быстро выучить английский с LinguaStart",
        "Арабский язык с мобильного приложения LinguaStart"
    ]

    # Если тема не передана, используем первую
    if not topic:
        topic = default_topics[0]
        print(f"\n📌 Использую тему: {topic}")

    # Запускаем полный пайплайн
    result = await generator.full_pipeline(topic)

    if result:
        print(f"\n✅ УСПЕХ! Видео создано: {result}")
    else:
        print(f"\n⚠️ Видео не скачалось, но генерация запущена на Runway")


if __name__ == "__main__":
    import sys
    topic = sys.argv[1] if len(sys.argv) > 1 else None
    asyncio.run(main(topic))
