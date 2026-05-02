# 🌐 Grok Browser-Based Integration

## ✨ ЧТО ЭТО?

Система для взаимодействия с Grok **через твой реальный браузер аккаунт**, без необходимости хранить API ключи!

```
Старый подход:                    Новый подход:
┌──────────────┐                 ┌──────────────────┐
│  API Key     │ → Grok API      │  Твой браузер    │
└──────────────┘                 │  + Твой аккаунт  │
❌ Небезопасно                    │  → Grok          │
❌ Ключ в памяти                  └──────────────────┘
                                  ✅ Безопасно
                                  ✅ Используется реальный аккаунт
```

---

## 🚀 БЫСТРЫЙ СТАРТ

### 1. Установить Playwright (браузер автоматизация)

```bash
pip install playwright
playwright install chromium
```

### 2. Запустить скрипт

```bash
python grok_browser_delegate.py
```

### 3. Вот что произойдет:

```
1️⃣  Откроется браузер
2️⃣  Если ты не авторизован → введи свои данные (как обычно)
3️⃣  Если авторизован → скрипт будет отправлять запросы от твоего имени
4️⃣  Ты видишь все что происходит в браузере (не скрытно!)
```

---

## 💻 ИСПОЛЬЗОВАНИЕ В КОДЕ

### Простой вариант - задать вопрос:

```python
from grok_browser_delegate import GrokBrowserDelegate
import asyncio

async def main():
    grok = GrokBrowserDelegate(headless=False)
    await grok.setup()
    await grok.login_if_needed()

    # Задать вопрос
    response = await grok.ask_question("Write hello world in Python")
    print(response)

    await grok.close()

asyncio.run(main())
```

### Делегировать документацию:

```python
async def main():
    grok = GrokBrowserDelegate()
    await grok.setup()
    await grok.login_if_needed()

    # Попросить написать документацию
    docs = await grok.write_documentation(
        topic="Setup Guide",
        requirements="Include examples, installation, usage"
    )
    print(docs)

    await grok.close()

asyncio.run(main())
```

---

## ✅ ПРЕИМУЩЕСТВА

| Аспект | API Key | Browser |
|--------|---------|---------|
| **Безопасность** | ⚠️ Ключ хранится | ✅ Ключ не хранится |
| **Видимость** | 🚫 Черный ящик | 👀 Видишь все в браузере |
| **Аккаунт** | 🔑 Техническое | 👤 Твой реальный аккаунт |
| **Проблемы** | Сложно отладить | Легко отладить |
| **Контроль** | Ограниченный | 🎮 Полный контроль |

---

## 🎯 КАК ЭТО РАБОТАЕТ

### Шаг 1: Setup
```python
grok = GrokBrowserDelegate(headless=False)
await grok.setup()
```
✅ Открывается браузер, загружается console.x.ai

### Шаг 2: Login
```python
await grok.login_if_needed()
```
✅ Если не авторизован → появится форма входа
✅ Если авторизован → продолжит работу

### Шаг 3: Отправить сообщение
```python
response = await grok.ask_question("What is Python?")
```
✅ Пишет в текстовое поле чата
✅ Нажимает Enter
✅ Ждет ответ
✅ Возвращает результат

### Шаг 4: Закрыть
```python
await grok.close()
```
✅ Браузер закрывается

---

## 🔐 БЕЗОПАСНОСТЬ

### Что происходит:

```
┌─────────────────────────────────────────────────┐
│                  Твой компьютер                │
│                                                 │
│  ┌──────────────────────────────────────────┐  │
│  │         Playwright + Chromium             │  │
│  │     (контролируемый браузер)              │  │
│  │                                            │  │
│  │  grok_browser_delegate.py                 │  │
│  │  ├─ Вводит сообщение                      │  │
│  │  ├─ Нажимает Enter                        │  │
│  │  └─ Читает ответ                          │  │
│  └────────────────┬─────────────────────────┘  │
│                   │ HTTPS (зашифровано)        │
│                   ▼                             │
│            console.x.ai                        │
│         (твой реальный аккаунт)                │
│                                                 │
└─────────────────────────────────────────────────┘

✅ Ключ не хранится
✅ Все зашифровано (HTTPS)
✅ Используется реальный браузер
✅ Полный контроль
```

---

## 🎮 ИНТЕРАКТИВНОЕ ИСПОЛЬЗОВАНИЕ

### Браузер НЕ скрытый (headless=False):

```python
grok = GrokBrowserDelegate(headless=False)  # Видишь браузер!
```

Ты сможешь:
- 👀 Видеть что происходит в реальном времени
- 🖱️ Кликать вручную, если нужно
- 🔍 Отлаживать проблемы
- 📸 Снимать скриншоты

---

## 📚 ПРОДВИНУТОЕ ИСПОЛЬЗОВАНИЕ

### Несколько сообщений в одной сессии:

```python
async def main():
    grok = GrokBrowserDelegate()
    await grok.setup()
    await grok.login_if_needed()

    # Несколько запросов
    response1 = await grok.ask_question("Question 1?")
    response2 = await grok.ask_question("Question 2?")
    response3 = await grok.ask_question("Question 3?")

    print(response1)
    print(response2)
    print(response3)

    await grok.close()
```

### Сохранить браузер открытым:

```python
async def main():
    grok = GrokBrowserDelegate(headless=False)
    await grok.setup()
    await grok.login_if_needed()

    # Отправить сообщение
    await grok.ask_question("Hello!")

    # Браузер остается открытым!
    # Ты можешь продолжить в браузере вручную
    print("Browser is open. Type Ctrl+C to close")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        await grok.close()
```

---

## 🔧 ИНТЕГРАЦИЯ С VIDEO FARM

Обновим `telegram_bot_v2.py` для использования браузера:

```python
from grok_browser_delegate import GrokBrowserDelegate

async def generate_with_grok_browser(count: int):
    """Generate videos using Grok via browser"""
    
    grok = GrokBrowserDelegate(headless=True)  # Скрытый браузер
    await grok.setup()
    await grok.login_if_needed()

    # Отправить запрос на генерацию сценариев
    prompt = f"Generate {count} TikTok video scenarios..."
    response = await grok.ask_question(prompt)

    await grok.close()

    return response
```

---

## ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

### Требования:

1. **Браузер Chrome/Chromium** (устанавливается автоматически)
2. **Открытый доступ в интернет**
3. **Аккаунт на console.x.ai** (бесплатно!)

### Ограничения:

- Чуть медленнее чем API (браузер требует времени)
- Требует больше памяти (браузер)
- Нужен X11/GUI для headless=False (на серверах)

### Плюсы:

- ✅ Полная безопасность
- ✅ Используется реальный аккаунт
- ✅ Видешь все что происходит
- ✅ Легко отлаживать
- ✅ Никакие ключи не хранятся

---

## 🚀 ПОЛНЫЙ ПРИМЕР

```python
#!/usr/bin/env python3

from grok_browser_delegate import GrokBrowserDelegate
import asyncio

async def main():
    print("🚀 Starting Grok Browser Delegate")
    print()

    # Создать делегат
    grok = GrokBrowserDelegate(headless=False)

    try:
        # Setup
        print("1️⃣  Setting up browser...")
        await grok.setup()

        # Login
        print("2️⃣  Checking login...")
        if not await grok.login_if_needed():
            print("❌ Login failed")
            return

        # Отправить запросы
        print("3️⃣  Sending requests...")

        response = await grok.ask_question(
            "Write a Python function that returns 'Hello World'"
        )

        print()
        print("📤 Response from Grok:")
        print("-" * 80)
        print(response)
        print("-" * 80)

        # Закрыть
        print()
        print("✅ Done!")

    finally:
        await grok.close()


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📋 ЧЕКЛИСТ ЗАПУСКА

- [ ] Установить Playwright: `pip install playwright`
- [ ] Установить Chromium: `playwright install chromium`
- [ ] Иметь аккаунт на console.x.ai
- [ ] Запустить: `python grok_browser_delegate.py`
- [ ] Авторизоваться (если нужно)
- [ ] Видеть ответ от Grok в браузере
- [ ] ✅ Готово!

---

## 🎯 ИТОГО

**Вместо API ключа:**
- 🌐 Используешь реальный браузер
- 👤 От своего реального аккаунта
- 👀 Видишь все в реальном времени
- 🔒 Ключи не хранятся
- 💪 Полный контроль

**Процесс:**
1. Установить Playwright
2. Запустить скрипт
3. Авторизоваться (один раз)
4. Использовать в коде

**Готово!** 🚀
