@echo off
REM ===================================
REM LinguaStart Video Farm Mode
REM Pure Telegram-based operation (no web)
REM ===================================

echo.
echo ========================================
echo   LinguaStart Video Farm (Telegram Bot)
echo   Closed Private Video Generation Service
echo ========================================
echo.

REM Check if .env exists
if not exist ".env" (
    echo ERROR: .env file not found!
    pause
    exit /b 1
)

REM Check dependencies
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+
    pause
    exit /b 1
)

REM Check for telegram bot token
for /f "tokens=2 delims==" %%I in ('findstr /R "^TELEGRAM_BOT_TOKEN=" .env') do set BOT_TOKEN=%%I

if "%BOT_TOKEN%"=="" (
    echo.
    echo ❌ TELEGRAM_BOT_TOKEN not configured!
    echo.
    echo 📋 SETUP REQUIRED:
    echo.
    echo 1. Create a Telegram bot:
    echo    - Chat with @BotFather in Telegram
    echo    - Send /newbot and follow instructions
    echo    - Copy the token provided
    echo.
    echo 2. Get your Telegram ID:
    echo    - Chat with @userinfobot
    echo    - Copy the 'Id' shown
    echo.
    echo 3. Edit .env file and add:
    echo    TELEGRAM_BOT_TOKEN=your_token_here
    echo    TELEGRAM_ADMIN_ID=your_user_id
    echo.
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo ✅ Configuration found!
echo.
echo 🤖 Starting Telegram Bot...
echo 📡 Status: Waiting for commands...
echo.
echo Commands:
echo   /start     - Welcome & info
echo   /generate  - Generate N videos
echo   /status    - Check job status
echo   /videos    - List all videos
echo   /help      - Show all commands
echo.
echo Press Ctrl+C to stop
echo.

REM Start bot
python telegram_bot.py

if errorlevel 1 (
    echo.
    echo ❌ Bot failed to start!
    pause
    exit /b 1
)

pause
