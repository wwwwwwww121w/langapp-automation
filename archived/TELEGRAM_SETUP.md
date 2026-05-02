# 🚀 LinguaStart Telegram Video Farm - Setup Guide

## Overview
This is a closed "video farm" that operates entirely through Telegram. Instead of a web dashboard, you control everything via Telegram bot commands.

## Features
✅ Generate N videos on demand via Telegram  
✅ Automatic progress updates  
✅ Direct video delivery to your Telegram chat  
✅ Job tracking and status monitoring  
✅ Closed/private access (only you can use it)  

---

## 🔧 Step 1: Create a Telegram Bot

1. **Open Telegram** and find **@BotFather**
2. **Send** `/newbot`
3. **Follow the prompts:**
   - Choose a name (e.g., "LinguaStart Video Farm")
   - Choose a username (e.g., "linguastart_farm_bot" - must be unique)
4. **Copy the token** that @BotFather gives you
   - Example: `6123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz1234567890`

---

## 📍 Step 2: Get Your Telegram User ID

1. **Open Telegram** and find **@userinfobot**
2. **Send** any message
3. **Copy the "Id" field** shown in the response
   - Example: `123456789`

---

## 🔐 Step 3: Configure .env File

**Edit** `C:\langapp-automation\.env` and add:

```ini
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=6123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz1234567890
TELEGRAM_ADMIN_ID=123456789
```

⚠️ **Keep these credentials PRIVATE!**

---

## ▶️ Step 4: Start the Bot

### Option A: Windows Batch Script (Recommended)
```bash
Double-click: start_telegram_bot.bat
```

### Option B: Command Line
```bash
python telegram_bot.py
```

### Option C: Run in Background
```bash
python telegram_bot.py > telegram_bot.log 2>&1 &
```

---

## 📱 Step 5: Test the Bot

1. **Open Telegram**
2. **Search** for your bot username (the one you created with @BotFather)
3. **Send** `/start`
4. You should see a welcome message

---

## 💬 Bot Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message & info |
| `/generate` | Start video generation (asks for count) |
| `/status` | Check current job status |
| `/videos` | List all generated videos |
| `/help` | Show help and commands |
| `/cancel` | Cancel current operation |

---

## 🎬 How to Generate Videos

### Example Workflow:

**You:**  
`/generate`

**Bot:**  
"How many videos do you want to generate? (1-20):"

**You:**  
`5`

**Bot:**  
```
🎬 Starting generation of 5 videos...
Job ID: 1704067200000

⏳ Stage 1/3: Generating scenarios...
⏳ Stage 2/3: Creating frames...
⏳ Stage 3/3: Assembling videos...
✅ Success! Generated 5 videos. Sending files...
```

**Bot sends:**  
- #1 video_001.mp4 (56.2 MB)
- #2 video_006.mp4 (47.1 MB)
- #3 video_011.mp4 (47.3 MB)
- #4 video_016.mp4 (76.5 MB)
- #5 video_017.mp4 (73.2 MB)

---

## 📊 Monitoring

### Logs
All bot activity is logged to:
```
C:\langapp-automation\logs\telegram_bot.log
```

### Check Status Anytime
Send `/status` to check if a job is still processing

---

## 🔒 Security Notes

- **Token**: Never share your `TELEGRAM_BOT_TOKEN`
- **Access**: Only your Telegram account (TELEGRAM_ADMIN_ID) can use the bot
- **Privacy**: Videos are generated locally, not stored in the cloud
- **Logs**: Check logs for any errors or issues

---

## ⚡ Performance Tips

- **Large batches**: 10-20 videos may take 5-15 minutes depending on API response times
- **Wait between requests**: Generate one batch at a time
- **Check logs**: If generation fails, check `telegram_bot.log` for details

---

## 🆘 Troubleshooting

### "Token not found"
- Edit `.env` file
- Add `TELEGRAM_BOT_TOKEN=your_token`
- Restart bot

### "Bot doesn't respond"
- Check internet connection
- Verify token is correct in `.env`
- Check `telegram_bot.log` for errors

### "Videos aren't being sent"
- Bot might be having issues uploading
- Check video file sizes in `output/videos/`
- Check telegram_bot.log for upload errors

### "Generation takes too long"
- Normal for 10+ videos
- Check progress with `/status`
- API response times vary

---

## 🎯 Next Steps

1. ✅ Create bot with @BotFather
2. ✅ Get your user ID from @userinfobot
3. ✅ Add credentials to `.env`
4. ✅ Start the bot
5. ✅ Send `/start` to test
6. ✅ Generate your first videos!

---

## 📞 Support

If you encounter issues:
1. Check `logs/telegram_bot.log`
2. Verify `.env` configuration
3. Ensure all scripts in `scripts/` directory are present
4. Check that `output/videos/` directory exists

Good luck! 🚀
