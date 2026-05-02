# 🚀 LinguaStart Telegram Bot - Cloud Deployment Guide

## Запуск бота 24/7 в облаке (чтобы работал без ПК)

Бот работает круглосуточно на облачном сервере, генерирует видео через xAI Grok API!

---

## ⚡ Быстрое развертывание (5 минут)

### Вариант 1: Railway.app (РЕКОМЕНДУЕТСЯ)

**Плюсы:**
- ✅ Бесплатный tier (500 часов/месяц)
- ✅ Автоматический деплой с GitHub
- ✅ Автоперезагрузка если упадет
- ✅ Просто и быстро

**Шаги:**

1. **Перейди на Railway.app:**
   https://railway.app

2. **Залогинься с GitHub:**
   - Click "Login with GitHub"
   - Авторизуй Railway

3. **Создай новый проект:**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Выбери репозиторий с langapp-automation

4. **Загрузи переменные окружения:**
   ```
   TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
   TELEGRAM_ADMIN_ID=your-admin-id-here
   XAI_API_KEY=your-xai-api-key-here
   XAI_VIDEO_MODEL=grok-imagine-video
   XAI_VIDEO_DURATION=8
   XAI_VIDEO_ASPECT_RATIO=9:16
   XAI_VIDEO_RESOLUTION=720p
   FIREWORKS_API_KEY=your-fireworks-api-key-here
   ```

5. **Деплой:**
   - Click "Deploy"
   - Жди ~2-3 минуты
   - ✅ Готово!

---

### Вариант 2: Replit (САМЫЙ ПРОСТОЙ)

**Шаги:**

1. **Перейди на Replit.com:**
   https://replit.com

2. **Click "+ Create"**

3. **Select "Python"**

4. **Залей files:**
   - Загрузи все файлы проекта
   - Особенно: `bot/telegram_bot_grok_v3.py` и `.env`

5. **В консоли:**
   ```bash
   pip install -r requirements.txt
   python bot/telegram_bot_grok_v3.py
   ```

6. **Run forever:**
   - Нажми "Always on" (платный, но дешево)
   - Или используй Replit Webview для автоперезагрузки

---

### Вариант 3: PythonAnywhere (СВОБОДНЫЙ ВЫБОР)

**Шаги:**

1. Создай аккаунт: https://www.pythonanywhere.com

2. Upload files в "Files" tab

3. Create "Bash console"

4. Запусти:
   ```bash
   pip install --user -r requirements.txt
   python bot/telegram_bot_grok_v3.py &
   ```

5. Настрой "Always-on task" в "Web" tab

---

### Вариант 4: Heroku (СТАРЫЙ, НО МОЩНЫЙ)

**Примечание:** Heroku больше не предоставляет бесплатный tier, но если есть кредиты:

1. **Создай Procfile:**
   ```
   worker: python bot/telegram_bot_grok_v3.py
   ```

2. **Деплой:**
   ```bash
   heroku login
   heroku create linguastart-bot
   git push heroku main
   heroku ps:scale worker=1
   heroku logs --tail
   ```

---

## 🐳 Запуск в Docker (ЛОКАЛЬНО)

Если хочешь протестировать локально на Docker:

### На Windows (с Docker Desktop):

```bash
# Создай .env файл с переменными
copy .env.example .env

# Отредактируй .env со своими ключами

# Запусти контейнер
docker-compose up -d

# Смотри логи
docker-compose logs -f

# Останови
docker-compose down
```

---

## ✅ ПРОВЕРКА РАБОТЫ

### Локально (Docker):
```bash
docker exec linguastart-telegram-bot tail -f logs/telegram_bot_grok.log
```

### На Railway/Heroku:
1. Перейди в "Deployments"
2. Найди "Logs"
3. Смотри если видны сообщения:
   ```
   ✅ Bot token: ...
   ✅ Admin ID: ...
   ✅ Используется xAI Grok Video API
   ```

### В Telegram:
1. Отправь `/start` боту
2. Должна появиться меню с кнопками
3. Нажми "🎬 Генерировать видео Grok"
4. Жди 1-2 минуты
5. Получи ссылки на 3 видео!

---

## 🔧 НАСТРОЙКА ОКРУЖЕНИЯ

### Переменные окружения (.env):

```bash
# TELEGRAM
TELEGRAM_BOT_TOKEN=your-telegram-bot-token-here
TELEGRAM_ADMIN_ID=your-admin-id-here

# xAI GROK
XAI_API_KEY=your-xai-api-key-here
XAI_VIDEO_MODEL=grok-imagine-video
XAI_VIDEO_DURATION=8
XAI_VIDEO_ASPECT_RATIO=9:16
XAI_VIDEO_RESOLUTION=720p

# FIREWORKS (для других функций)
FIREWORKS_API_KEY=your-fireworks-api-key-here
FIREWORKS_BASE_URL=https://api.fireworks.ai/inference/v1
FIREWORKS_MODEL=accounts/fireworks/models/minimax-m2p7
```

---

## 📊 МОНИТОРИНГ

### Railway Dashboard:
- Перейди в проект → "Deployments"
- Смотри CPU, Memory, Logs
- Если упал - автоматически перезагружается

### Replit:
- Console tab показывает все логи
- Если ошибка - сразу видно

### Docker:
```bash
docker stats linguastart-telegram-bot
```

---

## 🚨 TROUBLESHOOTING

### Бот не отвечает

```bash
# Проверь логи
docker-compose logs linguastart-bot

# Перезагрузи
docker-compose restart linguastart-bot

# Или на Railway:
# Нажми "Redeploy" в Dashboard
```

### API Key ошибка

```
Error: XAI_API_KEY не найден в .env
```

**Решение:**
1. Проверь что .env загружен в облако
2. На Railway: добавь в "Variables"
3. На Replit: добавь в "Secrets"

### xAI Grok API ошибка

```
Error: Model not found: grok-imagine-video
```

**Решение:**
1. Проверь XAI_API_KEY верный
2. Проверь интернет
3. Проверь статус xAI API: https://status.x.ai

---

## 📈 МАСШТАБИРОВАНИЕ

### Если много пользователей:

1. **Увеличь resources:**
   - Railway: Toggle "Deployment Size" (Starter → Standard)
   - Heroku: `heroku dyno:type standard`

2. **Добавь Webhook вместо polling:**
   - Более эффективно для большого трафика
   - Меньше нагрузки на API

3. **Кэширование видео:**
   - Сохраняй сгенерированные видео
   - Переиспользуй для похожих запросов

---

## 🎯 ПОЛНАЯ ИНСТРУКЦИЯ ДЛЯ RAILWAY (РЕКОМЕНДУЕТСЯ)

### Шаг за шагом:

1. **Подготовка кода:**
   ```bash
   # Убедись что есть файлы:
   # - bot/telegram_bot_grok_v3.py
   # - Dockerfile
   # - docker-compose.yml
   # - requirements.txt
   # - .env (или переменные окружения)
   ```

2. **Push на GitHub:**
   ```bash
   git add .
   git commit -m "Deploy to Railway"
   git push origin main
   ```

3. **Railway Deploy:**
   - Перейди https://railway.app
   - Нажми "New Project"
   - "Deploy from GitHub"
   - Выбери repo
   - Подожди деплой (~2 мин)

4. **Настрой переменные:**
   - Project Settings → Variables
   - Добавь все из .env

5. **Проверь работу:**
   ```bash
   # В Telegram: /start
   # Должно работать!
   ```

---

## 📱 ИСПОЛЬЗОВАНИЕ

### Как пользователь будет использовать:

1. Найти бота в Telegram
2. `/start` или "Start"
3. Нажать "🎬 Генерировать видео Grok"
4. Ждать 1-2 минуты
5. Получить 3 ссылки на готовые видео
6. Скачать и загрузить на TikTok/Reels

### Бот работает 24/7:
- ✅ Утром - видео генерируются
- ✅ Днем - видео генерируются
- ✅ Ночью - видео генерируются
- ✅ В выходные - видео генерируются

---

## 🔐 БЕЗОПАСНОСТЬ

### Ключи в облаке:

```bash
# НИКОГДА не коммитай .env в GitHub!

# На Railway/Replit - используй UI для переменных
# На Docker - используй .env.local (добавлен в .gitignore)

# Переменные окружения защищены в облаке
✅ Безопасно на Railway
✅ Безопасно на Replit
✅ Безопасно на PythonAnywhere
```

---

## 📞 ПОДДЕРЖКА

Если что-то не работает:

1. Проверь логи (Railway Dashboard или Console)
2. Убедись все переменные окружения загружены
3. Проверь интернет
4. Перезагрузи приложение (Redeploy на Railway)
5. Проверь статус xAI API

---

## 🎉 ГОТОВО!

Теперь твой Telegram бот работает 24/7 в облаке и может генерировать видео даже когда ПК выключен! 🚀

**Следующие шаги:**
1. Выбери один из вариантов деплоя (Railway рекомендуется)
2. Следуй инструкциям
3. Бот работает круглосуточно!

**Генери видео без перерывов! 🎬📱**
