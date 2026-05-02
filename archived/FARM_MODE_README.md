# 🚀 LinguaStart Video Farm - Closed Architecture Guide

## Overview

**LinguaStart Video Farm** is a private, Telegram-based service for generating Arabic+English educational videos.

Instead of a web dashboard, everything operates through Telegram:
- ✅ No web interface to manage
- ✅ No dashboard to keep running
- ✅ Private access (only you via Telegram)
- ✅ Videos delivered directly to your Telegram chat
- ✅ Perfect for automation and batch processing

---

## 🏗️ Architecture

### Old Setup (Web Dashboard)
```
User → Browser → Flask Web Server (http://localhost:5000) → Pipeline Scripts → Videos
```

### New Setup (Farm Mode)
```
User → Telegram Bot → Python Bot Process → Pipeline Scripts → Videos
```

**Benefits:**
- No web port conflicts
- Simpler deployment
- Better for automation
- Private by default
- Mobile-friendly (Telegram app)

---

## 📋 Quick Start (5 minutes)

### 1️⃣ Create Telegram Bot
- Chat with **@BotFather** in Telegram
- Send `/newbot`
- Follow the prompts → get token

### 2️⃣ Get Your Telegram ID
- Chat with **@userinfobot** in Telegram  
- It shows your ID

### 3️⃣ Configure
Edit `.env` file:
```ini
TELEGRAM_BOT_TOKEN=your_token_from_botfather
TELEGRAM_ADMIN_ID=your_id_from_userinfobot
```

### 4️⃣ Start Bot
```bash
start_farm_mode.bat
```

### 5️⃣ Send `/start` to Your Bot
Done! ✅

---

## 📁 File Structure

```
C:\langapp-automation\
├── telegram_bot.py              # Main bot (NEW)
├── start_farm_mode.bat          # Easy launcher (NEW)
├── start_telegram_bot.bat       # Alt launcher (NEW)
├── TELEGRAM_SETUP.md            # Setup guide (NEW)
├── FARM_MODE_README.md          # This file (NEW)
│
├── scripts/
│   ├── 01_generate_scenarios.py # Unchanged
│   ├── 02_generate_frames.py    # Unchanged
│   └── 03_assemble_videos.py    # Unchanged
│
├── output/
│   └── videos/                  # Generated videos (same location)
│
├── logs/
│   └── telegram_bot.log         # Bot activity log
│
├── .env                         # Configuration (UPDATE REQUIRED)
├── config.py                    # Configuration (unchanged)
└── ...other files...
```

---

## 🎯 Usage Examples

### Example 1: Generate 5 Videos
```
You:  /generate
Bot:  "How many videos? (1-20):"
You:  5
Bot:  ⏳ Processing...
      [After 3-5 minutes]
      ✅ Done! [Sends 5 MP4 files]
```

### Example 2: Check Job Status
```
You:  /status
Bot:  ⏳ Processing...
      Stage: Creating frames (2/3)
      Videos: 5
      Time: 124s
```

### Example 3: List All Videos
```
You:  /videos
Bot:  📹 Available videos (8):
      1. video_001.mp4 (56KB) - 18:14
      2. video_006.mp4 (47KB) - 18:14
      3. video_016.mp4 (76KB) - 18:34
      ...
```

---

## ⚙️ Configuration

### Required Settings in `.env`

```ini
# Telegram Bot (NEW)
TELEGRAM_BOT_TOKEN=6123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz1234567890
TELEGRAM_ADMIN_ID=123456789

# Existing Settings (unchanged)
FIREWORKS_API_KEY=fw_...
FIREWORKS_BASE_URL=https://api.fireworks.ai/inference/v1
...
```

### Optional Settings

```ini
# You can still run Flask alongside (not required)
FLASK_PORT=5000
FLASK_DEBUG=False

# Or disable Flask completely
# Just don't run app.py - use telegram_bot.py instead
```

---

## 🔄 Pipeline Details

When you request videos, the bot runs the full pipeline:

### Stage 1: Generate Scenarios (1 min)
- Uses Fireworks API (4 batches)
- Creates 6 scenarios (fact, dialect, mistake, phrase)
- Saves to `data/scenarios_*.json`

### Stage 2: Generate Frames (2 min)
- Uses PIL for image generation
- Creates PNG frames for each scenario
- Saves to `output/frames/`

### Stage 3: Assemble Videos (2-3 min)
- Uses FFmpeg for video encoding
- Creates MP4 files (1080x1920 TikTok format)
- Saves to `output/videos/`

**Total time:** ~5-8 minutes for 5 videos

---

## 📊 Monitoring

### Real-time Progress
```
/status - Check what stage the bot is on
```

### Log Files
```
Logs: C:\langapp-automation\logs\telegram_bot.log
```

### Video Storage
```
Videos: C:\langapp-automation\output\videos\*.mp4
```

---

## 🔐 Security

### Token Safety
- ✅ Token stored in `.env` (locally)
- ✅ Never shared with external services
- ✅ Each request goes directly to Telegram API
- ⚠️ Keep `.env` file private!

### Access Control
- Only Telegram users with matching `TELEGRAM_ADMIN_ID` can use the bot
- No public access
- No authentication needed after setup

### Data Privacy
- Videos generated locally
- Not uploaded to cloud storage
- Can delete videos anytime with `rm output/videos/*.mp4`

---

## 🚀 Advanced Usage

### Batch Processing
```
/generate → 10 videos → sends all 10 files
```

### Scheduling
Run `start_farm_mode.bat` in Windows Task Scheduler:
```
Schedule: Daily at 2 AM
Action: Start Program → start_farm_mode.bat
```

### Multiple Users
To allow other users:
1. Create separate `.env` files
2. Different bot instances
3. Each with their own `TELEGRAM_BOT_TOKEN`

---

## ❌ Disabling Flask Web Server

If you want to completely disable the web dashboard:

### Option 1: Don't run Flask
Just run:
```bash
start_farm_mode.bat
```

Instead of:
```bash
python app.py
```

### Option 2: Disable in startup
Edit `launcher.py` to comment out Flask:
```python
# def run_server():
#     os.environ['FLASK_ENV'] = 'production'
#     from app import app
#     app.run(debug=False, port=5000, use_reloader=False, threaded=True)
```

### Result
- No web server running
- Port 5000 free
- Only Telegram bot active
- Lower resource usage

---

## 🔧 Troubleshooting

### Bot doesn't start
```
❌ Error: TELEGRAM_BOT_TOKEN not set
✅ Solution: Edit .env and add token, then restart
```

### Bot doesn't respond
```
❌ Bot appears offline
✅ Solution: Check internet connection
✅ Check TELEGRAM_BOT_TOKEN is correct
✅ Check logs: logs/telegram_bot.log
```

### Videos aren't being sent
```
❌ Generation completes but no videos sent
✅ Solution: Check file permissions in output/videos/
✅ Check internet speed (videos are large)
✅ Check logs for upload errors
```

### "Maximum retries exceeded"
```
❌ Telegram API timeout
✅ Solution: Bot will retry automatically
✅ Check your internet connection
```

---

## 📈 Performance Expectations

| Request | Time | CPU | Memory |
|---------|------|-----|--------|
| 1 video | 1 min | Low | 200MB |
| 5 videos | 5 min | Medium | 500MB |
| 10 videos | 8 min | High | 1GB |
| 20 videos | 15 min | Very High | 1.5GB |

**Tips:**
- Don't request multiple jobs simultaneously
- Let one complete before starting another
- 10+ videos may use significant CPU

---

## 🎓 What Gets Generated

### Videos Include:
- ✅ Arabic + English content
- ✅ Visual frames with text overlays
- ✅ Background music (optional)
- ✅ Professional transitions
- ✅ Call-to-action (LinguaStart branding)

### Formats:
- **Video**: MP4, H.264, 1080×1920 (9:16 TikTok)
- **Duration**: ~30-60 seconds per video
- **Size**: 50-100 MB per video

### Language:
- Content: Modern Standard Arabic (MSA) + English
- UI: Russian (Telegram bot)
- Captions: Both languages

---

## 📞 Support

### Check These First:
1. Read `TELEGRAM_SETUP.md` (detailed setup guide)
2. Check `logs/telegram_bot.log` (error details)
3. Verify `.env` configuration
4. Ensure all `scripts/` files are present

### Common Issues:
- "Bot offline" → Check token in `.env`
- "Videos not sent" → Check file sizes
- "Generation failed" → Check logs
- "Timeout" → Check internet, retry

---

## 🔄 Comparison: Web vs Farm Mode

| Feature | Web Dashboard | Telegram Farm |
|---------|---------------|---------------|
| **Interface** | Browser | Telegram App |
| **Setup** | Complex | Simple |
| **Access** | Open port | Private |
| **Mobile** | Responsive site | Native app |
| **Automation** | APIs | Bot commands |
| **Resource Use** | Higher (server) | Lower (bot) |
| **Video Delivery** | Download page | Direct messages |

---

## 🎯 Summary

**LinguaStart Video Farm** is a private, Telegram-based video generation service:

✅ **Setup**: 5 minutes  
✅ **Usage**: Simple commands  
✅ **Security**: Private by default  
✅ **Speed**: 5-15 min per batch  
✅ **Delivery**: Direct to Telegram  

**Get started:**
1. Create bot with @BotFather
2. Get ID from @userinfobot
3. Add to `.env`
4. Run `start_farm_mode.bat`
5. Send `/start` to bot!

---

## 📞 Next Steps

1. ✅ Read `TELEGRAM_SETUP.md` carefully
2. ✅ Create bot and get token
3. ✅ Configure `.env`
4. ✅ Start `start_farm_mode.bat`
5. ✅ Test with `/generate`

**Happy video generating! 🎬**
