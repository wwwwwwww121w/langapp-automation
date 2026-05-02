#!/usr/bin/env python3
"""
Генерация видео для LinguaStart через xAI Grok Video API.
Использует xai_sdk для создания профессиональных видео.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Загружаем переменные окружения
load_dotenv()

# Проверяем установку xai_sdk
try:
    from xai_sdk import Client
except ImportError:
    print("❌ xai_sdk не установлен!")
    print("Установи: pip install xai-sdk")
    sys.exit(1)


class GrokVideoGenerator:
    """Генератор видео через xAI Grok API"""

    def __init__(self):
        """Инициализируем xAI клиент"""
        api_key = os.getenv("XAI_API_KEY")
        if not api_key:
            raise ValueError("XAI_API_KEY не найден в .env")

        self.client = Client(api_key=api_key)
        self.model = os.getenv("XAI_VIDEO_MODEL", "grok-imagine-video")
        self.duration = int(os.getenv("XAI_VIDEO_DURATION", "8"))
        self.aspect_ratio = os.getenv("XAI_VIDEO_ASPECT_RATIO", "9:16")
        self.resolution = os.getenv("XAI_VIDEO_RESOLUTION", "720p")

        print(f"✅ xAI Client инициализирован")
        print(f"   API Key: {api_key[:30]}...")
        print(f"   Model: {self.model}")
        print(f"   Duration: {self.duration}s")
        print(f"   Aspect Ratio: {self.aspect_ratio}")
        print(f"   Resolution: {self.resolution}")

    def generate_video(self, prompt: str, output_dir: str = "output/videos", callback=None) -> dict:
        """Генерирует видео через xAI Grok API с отслеживанием прогресса

        Args:
            prompt: Описание видео для генерации
            output_dir: Папка для сохранения URLs
            callback: Функция обратного вызова для отслеживания прогресса (получает dict со статусом)

        Returns:
            dict с ключами: success, url, error, status
        """

        def report_status(status: str, progress: int = 0, message: str = ""):
            """Отправить статус генерации"""
            if callback:
                callback({
                    "status": status,
                    "progress": progress,
                    "message": message,
                    "prompt": prompt[:50]
                })
            print(f"[{status}] {message}")

        report_status("STARTING", 10, "🎬 Начинаю генерацию видео...")
        report_status("PROCESSING", 20, f"Промпт: {prompt[:60]}...")

        try:
            # Генерируем видео
            report_status("API_CALL", 30, "📡 Отправляю запрос к xAI Grok API...")

            response = self.client.video.generate(
                prompt=prompt,
                model=self.model,
                duration=self.duration,
                aspect_ratio=self.aspect_ratio,
                resolution=self.resolution
            )

            report_status("PROCESSING_RESPONSE", 60, "⏳ Обрабатываю ответ от API...")

            # Получаем URL видео (зависит от структуры ответа)
            video_url = None
            if hasattr(response, 'url'):
                video_url = response.url
            elif hasattr(response, 'video') and hasattr(response.video, 'url'):
                video_url = response.video.url
            elif isinstance(response, dict) and 'url' in response:
                video_url = response['url']
            else:
                # Если не знаем структуру, печатаем для диагностики
                print(f"   Ответ: {response}")
                print(f"   Тип: {type(response)}")
                print(f"   Атрибуты: {dir(response)}")
                report_status("ERROR", 0, "Не удалось получить URL видео из ответа")
                return {
                    "success": False,
                    "url": None,
                    "error": "Не удалось получить URL видео из ответа",
                    "status": "ERROR"
                }

            report_status("SAVING", 80, "💾 Сохраняю URL видео...")

            # Сохраняем URL в файл
            os.makedirs(output_dir, exist_ok=True)
            url_file = os.path.join(output_dir, "video_url.txt")

            with open(url_file, 'a', encoding='utf-8') as f:
                f.write(f"{video_url}\n")

            report_status("COMPLETE", 100, f"✅ Видео готово!")

            return {
                "success": True,
                "url": video_url,
                "error": None,
                "status": "COMPLETE"
            }

        except Exception as e:
            error_msg = f"❌ Ошибка при генерации видео: {str(e)}"
            report_status("ERROR", 0, error_msg)
            return {
                "success": False,
                "url": None,
                "error": str(e),
                "status": "ERROR"
            }


def main():
    """Главная функция"""

    print("\n" + "=" * 80)
    print("🎬 ГЕНЕРАЦИЯ ВИДЕО LINGUASTART ЧЕРЕЗ GROK VIDEO API")
    print("=" * 80)

    try:
        generator = GrokVideoGenerator()
    except ValueError as e:
        print(f"❌ Ошибка: {e}")
        return

    # Промпты для видео про LinguaStart
    video_prompts = [
        {
            "title": "LinguaStart - Приложение для изучения английского",
            "prompt": """
Создай привлекательное видео для TikTok про мобильное приложение LinguaStart для изучения английского языка.

Видео должно показывать:
1. Молодого человека, открывающего приложение LinguaStart на смартфоне
2. Интерфейс приложения с интерактивными уроками
3. Примеры английских слов и фраз на экране
4. Прогресс-бар с зелёным цветом (#00ff41)
5. Геймификацию - монеты, уровни, достижения
6. Счастливое выражение лица пользователя
7. Логотип LinguaStart в конце
8. Текст "Скачай LinguaStart - начни учить английский"

Стиль: современный, энергичный, мотивирующий.
Цвета: зелёный (#00ff41), золотой (#FFD700), чёрный фон.
Формат: 9:16 для TikTok/Reels.
"""
        },
        {
            "title": "LinguaStart - Изучай арабский язык",
            "prompt": """
Создай привлекательное видео для TikTok про изучение арабского языка в приложении LinguaStart.

Видео должно показывать:
1. Красивый интерфейс с арабскими буквами и словами
2. Произношение слов (аудиовизуальное отображение)
3. Примеры: "مرحبا" (привет), "شكراً" (спасибо) и др.
4. Интерактивные упражнения на выбор правильного ответа
5. Достижения и прогресс в зелёном цвете
6. Культурные элементы (исламская архитектура, восточные узоры)
7. Логотип LinguaStart с луной (символ арабского мира)
8. Call-to-action: "Учи арабский весело с LinguaStart"

Стиль: культурный, образовательный, дружелюбный.
Цвета: зелёный (#00ff41), золотой (#FFD700), восточные мотивы.
Формат: 9:16 для TikTok/Reels.
"""
        },
        {
            "title": "LinguaStart - Почему это приложение лучше всех",
            "prompt": """
Создай мотивирующее видео для TikTok про преимущества приложения LinguaStart.

Видео должно демонстрировать:
1. Быстрые 5-минутные уроки (часы пока учится пользователь)
2. Геймификацию - рейтинги, соревнования, медали
3. Персональные рекомендации - приложение "знает" твой уровень
4. Оба языка: английский 🇬🇧 и арабский 🇸🇦
5. Высокий рейтинг (4.9 звёзд) с количеством загрузок
6. Реального пользователя, который прогрессирует и достигает целей
7. Превращение новичка в опытного пользователя
8. Финальный текст: "Начни свой путь сегодня - скачай LinguaStart"

Стиль: вдохновляющий, позитивный, профессиональный.
Цвета: зелёный (#00ff41), золотой (#FFD700), современный дизайн.
Формат: 9:16 для TikTok/Reels.
Длительность: 8-10 секунд.
"""
        }
    ]

    os.makedirs("output/videos", exist_ok=True)
    results = []

    for i, video_info in enumerate(video_prompts, 1):
        print(f"\n{'=' * 80}")
        print(f"📹 ВИДЕО {i}/3: {video_info['title']}")
        print("=" * 80)

        video_url = generator.generate_video(video_info['prompt'])

        if video_url:
            results.append({
                "title": video_info['title'],
                "url": video_url
            })
            print(f"✅ Видео {i} успешно сгенерировано!")
        else:
            print(f"❌ Ошибка при генерации видео {i}")

    # Финальный отчет
    print(f"\n{'=' * 80}")
    print("🎉 ГЕНЕРАЦИЯ ЗАВЕРШЕНА!")
    print("=" * 80)

    if len(results) > 0:
        print(f"\n✅ Успешно сгенерировано видео: {len(results)}/3\n")

        for i, result in enumerate(results, 1):
            print(f"{i}. {result['title']}")
            print(f"   🔗 {result['url']}\n")

        print("=" * 80)
        print("📝 Все ссылки на видео сохранены в: output/videos/video_url.txt")
        print("\n✨ Видео готовы к публикации на TikTok/Instagram Reels!")
        print("🚀 LinguaStart готов к вирусному распространению!\n")
    else:
        print("\n⚠️ Видео не были сгенерированы")
        print("Проверь:")
        print("  1. XAI_API_KEY в .env файле")
        print("  2. Подключение к интернету")
        print("  3. Статус xAI API\n")


if __name__ == "__main__":
    main()
