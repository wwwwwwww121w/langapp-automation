# ✅ LinguaStart Telegram Bot - Quick Setup Checklist

**Estimated Time: 5-10 minutes**

---

## 📱 STEP 1: Create Telegram Bot (2 min)

- [ ] Open **Telegram app**
- [ ] Search for **@BotFather**
- [ ] Send `/newbot`
- [ ] Choose a name (e.g., "LinguaStart Video Farm")
- [ ] Choose a username (e.g., "linguastart_farm_bot") - *must be unique*
- [ ] **Copy the token** that appears
  ```
  Example: 6123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz1234567890
  ```
- [ ] Save token somewhere safe (you'll need it in 5 minutes)

✅ **Bot created!**

---

## 👤 STEP 2: Get Your Telegram ID (2 min)

- [ ] Open **Telegram app**
- [ ] Search for **@userinfobot**
- [ ] Send any message to it
- [ ] **Copy your "Id"** (the number shown)
  ```
  Example: 123456789
  ```
- [ ] Save ID somewhere safe

✅ **ID obtained!**

---

## 📝 STEP 3: Configure .env File (2 min)

- [ ] Open `C:\langapp-automation\.env` in a text editor
- [ ] Find these lines:
  ```ini
  TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
  TELEGRAM_ADMIN_ID=your_telegram_user_id_here
  ```
- [ ] Replace `your_telegram_bot_token_here` with your **token from Step 1**
- [ ] Replace `your_telegram_user_id_here` with your **ID from Step 2**
- [ ] **Save the file** (Ctrl+S)

Example of completed `.env`:
```ini
TELEGRAM_BOT_TOKEN=6123456789:ABCDEFGHIJKLMNOPQRSTuvwxyz1234567890
TELEGRAM_ADMIN_ID=123456789
```

✅ **Configuration complete!**

---

## ▶️ STEP 4: Start the Bot (1 min)

### Option A: Easy Way (Recommended)
- [ ] Open File Explorer
- [ ] Navigate to `C:\langapp-automation\`
- [ ] Double-click **`start_farm_mode.bat`**
- [ ] Wait for message: **"Bot started successfully!"**
- [ ] Leave window open

### Option B: Command Line
- [ ] Open Command Prompt
- [ ] Run:
  ```
  cd C:\langapp-automation
  python telegram_bot.py
  ```

### Option C: Verify Setup First
- [ ] Open Command Prompt
- [ ] Run:
  ```
  cd C:\langapp-automation
  python verify_farm_setup.py
  ```
- [ ] Should show: ✅ ALL CHECKS PASSED!
- [ ] Then run:
  ```
  start_farm_mode.bat
  ```

✅ **Bot is running!**

---

## 🧪 STEP 5: Test the Bot (2 min)

- [ ] Open **Telegram app**
- [ ] Search for your bot username (from Step 1)
  ```
  Example: linguastart_farm_bot
  ```
- [ ] Tap to open the chat
- [ ] Send command:
  ```
  /start
  ```
- [ ] You should see:
  ```
  🚀 Welcome to LinguaStart Video Farm!
  
  Available commands:
  /generate - Start generating videos
  /status - Check job status
  ...
  ```

If you see this message:
✅ **Bot is working!**

If bot doesn't respond:
- [ ] Check that bot window is still open
- [ ] Verify `.env` configuration
- [ ] Check for error messages
- [ ] Read `TELEGRAM_SETUP.md` for troubleshooting

---

## 🎬 STEP 6: Generate Your First Video (5 min)

- [ ] Send to your bot:
  ```
  /generate
  ```
- [ ] Bot asks: "How many videos? (1-20):"
- [ ] Send:
  ```
  1
  ```
- [ ] Wait for generation (should take 5-10 minutes total)
- [ ] Bot sends back a video file (MP4)

When you see the video file:
✅ **Everything works!**

---

## 📋 Full Command Reference

Once bot is running, you can send these commands:

| Command | Does What |
|---------|-----------|
| `/start` | Show welcome message |
| `/generate` | Start generating videos |
| `/status` | Check current job status |
| `/videos` | List all generated videos |
| `/help` | Show help info |
| `/cancel` | Cancel current task |

---

## 🚨 If Something Goes Wrong

### Bot won't start
```
❌ Error: "TELEGRAM_BOT_TOKEN not set"
✅ Fix: Check .env file, make sure token is added correctly
```

### Bot is offline
```
❌ Bot doesn't respond to /start
✅ Fix: 
  1. Check bot window is still open
  2. Check internet connection
  3. Read logs/telegram_bot.log for errors
```

### Videos don't generate
```
❌ Generation gets stuck
✅ Fix:
  1. Check /status
  2. Wait (might still processing)
  3. Check logs for errors
  4. Try just 1 video first
```

**For detailed help:** Read `TELEGRAM_SETUP.md`

---

## 🎯 What To Do Next

### ✅ Everything working?
Congratulations! You're done! 🎉

Now you can:
- [ ] Generate videos anytime via `/generate`
- [ ] Check progress with `/status`
- [ ] List videos with `/videos`
- [ ] Keep bot running for 24/7 access
- [ ] Schedule bot to start automatically

### ⚠️ Having issues?

1. [ ] Check `.env` file is correct
2. [ ] Run `python verify_farm_setup.py`
3. [ ] Read `TELEGRAM_SETUP.md`
4. [ ] Check `logs/telegram_bot.log`
5. [ ] Restart the bot

### 🚀 Want to automate?

To run bot automatically on Windows startup:
1. Open **Task Scheduler**
2. Create new task: "LinguaStart Bot"
3. Set trigger: "At system startup"
4. Set action: Run `start_farm_mode.bat`
5. Check "Run with highest privileges"
6. Save

---

## 📚 Documentation Files

If you need more info:
- **TELEGRAM_SETUP.md** - Detailed setup guide (read this if stuck)
- **FARM_MODE_README.md** - Complete feature documentation
- **TELEGRAM_BOT_SUMMARY.md** - Full reference guide
- **telegram_bot.py** - Source code with comments

---

## ⏱️ Setup Timeline

```
Step 1 (Create bot):     2 min  ████
Step 2 (Get ID):         2 min  ████
Step 3 (Edit .env):      2 min  ████
Step 4 (Start bot):      1 min  ██
Step 5 (Test):           2 min  ████
Step 6 (First video):    5 min  ██████████

Total:                   14 min 
(Most of step 6 is waiting for video generation)
```

---

## ✨ Quick Reference

**Bot Location:**
```
C:\langapp-automation\telegram_bot.py
```

**Launcher:**
```
C:\langapp-automation\start_farm_mode.bat
(Double-click to start)
```

**Configuration:**
```
C:\langapp-automation\.env
(Edit with: Notepad)
```

**Logs:**
```
C:\langapp-automation\logs\telegram_bot.log
```

**Videos:**
```
C:\langapp-automation\output\videos\*.mp4
```

---

## 🎉 You're All Set!

**Summary of what you now have:**

✅ Private Telegram video generation service  
✅ Closed "farm" - only you can use it  
✅ No web interface to manage  
✅ Mobile-friendly via Telegram  
✅ Generates 5-20 videos on demand  
✅ Complete documentation  

**Ready to generate videos?** Open Telegram and send `/start` to your bot!

---

**Questions?** Check `TELEGRAM_SETUP.md`

**Stuck?** Run `python verify_farm_setup.py` to diagnose issues

**Ready?** Double-click `start_farm_mode.bat` and start generating! 🚀
