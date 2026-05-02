#!/usr/bin/env python3
"""
Исследуем интерфейс Runway через Grok в браузере.
Grok подскажет как работает видео-генерация в Runway.
"""

import sys
import os
import asyncio

# Add core to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core'))

from grok_browser_delegate import GrokBrowserDelegate


async def investigate_runway():
    """Используем Grok для исследования Runway интерфейса"""

    print("🔍 ИССЛЕДОВАНИЕ RUNWAY ЧЕРЕЗ GROK")
    print("=" * 70)

    delegate = GrokBrowserDelegate()

    try:
        # Инициализируем браузер
        print("\n🌐 Инициализируем браузер Grok...")
        await delegate.setup()
        print("✅ Браузер готов!")

        # Попрашиваем Grok исследовать Runway
        prompt = """
Пожалуйста, исследуй интерфейс Runway (runway.com) для генерации видео и дай мне подробную информацию:

1. КАК ПОПАСТЬ В ИНТЕРФЕЙС ВИДЕО-ГЕНЕРАЦИИ:
   - Какой URL или кнопка для видео-генерации?
   - Нужно ли быть авторизованным?

2. ЧТО ЗАПОЛНЯТЬ ДЛЯ ВИДЕО:
   - Какие поля есть? (текст, стиль, язык, длительность и т.д.)
   - Какие параметры обязательные?
   - Какие параметры опциональные?

3. КАК ЗАПУСТИТЬ ГЕНЕРАЦИЮ:
   - Какая кнопка запускает процесс?
   - Какой статус показывает генерацию?

4. КАК СКАЧАТЬ РЕЗУЛЬТАТ:
   - Где кнопка скачивания видео?
   - Какой формат видео? (MP4, WebM и т.д.)
   - Можно ли автоматизировать скачивание?

5. ПРИМЕРЫ ЗАПОЛНЕНИЯ:
   - Пример заполнения формы для видео про "Арабские цифры 1-5"
   - Какой стиль выбрать для обучающего видео?

Дай подробный ответ с точными названиями полей, кнопок и URL'ов.
"""

        print("\n📝 Отправляю запрос Grok...")
        print("\nВопрос для Grok:")
        print("-" * 70)
        print(prompt)
        print("-" * 70)

        # Отправляем вопрос Grok
        response = await delegate.ask_question(prompt)

        print("\n✅ ОТВЕТ GROK:")
        print("=" * 70)
        print(response)
        print("=" * 70)

        # Сохраняем ответ в файл для дальнейшего использования
        with open('runway_analysis.txt', 'w', encoding='utf-8') as f:
            f.write("ИССЛЕДОВАНИЕ RUNWAY ИНТЕРФЕЙСА ЧЕРЕЗ GROK\n")
            f.write("=" * 70 + "\n\n")
            f.write("ВОПРОС:\n")
            f.write(prompt)
            f.write("\n\n")
            f.write("ОТВЕТ GROK:\n")
            f.write(response)
            f.write("\n\n")
            f.write("=" * 70 + "\n")

        print("\n💾 Анализ сохранен в runway_analysis.txt")

        return response

    except Exception as e:
        print(f"❌ Ошибка: {e}")
        raise
    finally:
        await delegate.close()
        print("\n🌐 Браузер закрыт")


if __name__ == "__main__":
    print("\n🎬 АВТОМАТИЗАЦИЯ RUNWAY ЧЕРЕЗ GROK")
    print("=" * 70 + "\n")

    response = asyncio.run(investigate_runway())

    print("\n" + "=" * 70)
    print("✅ ИССЛЕДОВАНИЕ ЗАВЕРШЕНО!")
    print("=" * 70)
    print("\nСледующие шаги:")
    print("1. Прочитайте runway_analysis.txt")
    print("2. На основе информации напишем Playwright скрипт")
    print("3. Интегрируем в пайплайн видео-генерации")
