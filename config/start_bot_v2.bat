@echo off
REM ===================================
REM LinguaStart Video Farm Bot v2.0
REM Enhanced UI with buttons and interface
REM ===================================

echo.
echo ========================================
echo   LinguaStart Video Farm Bot v2.0
echo   Enhanced UI Edition
echo ========================================
echo.

REM Check if .env file exists
if not exist ".env" (
    echo ERROR: .env file not found!
    echo Please create .env file first.
    pause
    exit /b 1
)

REM Check if TELEGRAM_BOT_TOKEN is set
for /f "tokens=2 delims==" %%I in ('findstr /R "^TELEGRAM_BOT_TOKEN=" .env') do set BOT_TOKEN=%%I

if "%BOT_TOKEN%"=="" (
    echo.
    echo ERROR: TELEGRAM_BOT_TOKEN not configured!
    echo.
    echo Setup instructions:
    echo 1. Open Telegram and chat with @BotFather
    echo 2. Send /newbot and follow instructions
    echo 3. Copy the token and edit .env file:
    echo    TELEGRAM_BOT_TOKEN=your_token_here
    echo.
    echo 4. Get your Telegram ID:
    echo    - Chat with @userinfobot
    echo    - It will show you your ID
    echo 5. Add to .env file:
    echo    TELEGRAM_ADMIN_ID=your_user_id
    echo.
    pause
    exit /b 1
)

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.8+
    pause
    exit /b 1
)

REM Start the bot
echo Starting Enhanced Bot v2.0...
echo Features: Inline buttons, progress bar, better UI
echo.
python telegram_bot_v2.py

if errorlevel 1 (
    echo.
    echo ERROR: Bot failed to start!
    echo Check that TELEGRAM_BOT_TOKEN is correct in .env file
    pause
    exit /b 1
)

pause
