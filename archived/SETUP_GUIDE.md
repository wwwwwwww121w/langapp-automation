# 🚀 Setup Guide - Video Generation System

## Prerequisites

- Python 3.8+
- pip (Python package manager)
- FFmpeg installed and in PATH
- Git (optional, for version control)

---

## Step 1: Install Dependencies

```bash
# Navigate to project directory
cd langapp-automation

# Install all required packages
pip install -r requirements.txt
```

**If you get errors:**

### FFmpeg Installation
```bash
# Windows (using winget)
winget install ffmpeg

# macOS (using Homebrew)
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt-get install ffmpeg
```

### Pillow Issues
```bash
pip install --upgrade Pillow
```

---

## Step 2: Configure API Keys

### Option A: Using .env file (Recommended)

1. Copy existing `.env` file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your favorite editor:
   ```bash
   # Windows
   notepad .env
   
   # macOS/Linux
   nano .env
   ```

3. Fill in your API keys:
   ```env
   FIREWORKS_API_KEY=your_actual_api_key_here
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/google/credentials.json
   REDIS_CLIENT_ID=your_reddit_id
   # ... other settings
   ```

### Fireworks API Key
1. Go to https://www.fireworks.ai
2. Sign up and get your API key
3. Add to `.env`: `FIREWORKS_API_KEY=your_key`

### Google Cloud TTS (Optional)
1. Create a Google Cloud project
2. Enable Text-to-Speech API
3. Create service account credentials (JSON)
4. Download the JSON file
5. Set in `.env`: `GOOGLE_APPLICATION_CREDENTIALS=/path/to/file.json`

### Reddit API (Optional, for Reddit posting)
1. Go to https://www.reddit.com/prefs/apps
2. Create a new app (select "script")
3. Get your credentials
4. Add to `.env`:
   ```env
   REDDIT_CLIENT_ID=your_id
   REDDIT_CLIENT_SECRET=your_secret
   REDDIT_USERNAME=your_username
   REDDIT_PASSWORD=your_password
   ```

---

## Step 3: Verify Installation

Run the test script:
```bash
python test_models.py
```

This checks:
- ✅ Fireworks API connectivity
- ✅ Required packages
- ✅ Configuration loading

---

## Step 4: Customize Configuration

### Video Settings
Edit `.env` to adjust:
```env
VIDEO_WIDTH=1080          # Video width in pixels
VIDEO_HEIGHT=1920         # Video height (TikTok format)
SECONDS_PER_FRAME=2       # Duration each frame displays
FPS=30                    # Frames per second
```

### Colors
Customize the visual theme:
```env
BG_COLOR_DARK=#0f0f23     # Dark background
BG_COLOR_ACCENT=#1a1a3e   # Accent color
TEXT_COLOR_GOLD=#ffd700   # Highlight color
TEXT_COLOR_GREEN=#00e676  # Accent text color
```

### Audio Settings
```env
ENABLE_TTS=true           # Enable text-to-speech
ENABLE_BACKGROUND_MUSIC=true  # Add background music
VOICE_LANGUAGE=ar-EG      # Arabic (Egyptian dialect)
MUSIC_VOLUME=0.3          # Background music volume (0.0-1.0)
```

### App Details
```env
APP_NAME=ArabicEngLearn
APP_LINK=https://play.google.com/store/apps/details?id=...
APP_STORE_ID=com.example.arabicenglearn
```

---

## Step 5: Create Output Directories

```bash
# Directories are created automatically, but you can pre-create them:
mkdir -p output/videos output/audio output/frames
mkdir -p data logs
```

---

## Step 6: Test the Pipeline

### Quick Test
```bash
# Generate just one scenario to test
python scripts/01_generate_scenarios_enhanced.py
```

Check output:
- ✅ `data/scenarios_latest.json` created
- ✅ `logs/scenario_gen.log` contains execution details

### Full Test
```bash
# Run complete pipeline
python scripts/run_pipeline.py
```

This will:
1. Generate scenarios
2. Validate them
3. Create frames
4. Assemble videos (with effects)

**Output locations:**
- `output/videos/` - Generated MP4 files
- `output/audio/` - Generated audio files (if TTS enabled)
- `output/frames/` - Individual frames
- `data/` - Scenario and manifest JSON files
- `logs/` - Detailed execution logs

---

## Step 7: Run Individual Steps

### Generate Scenarios Only
```bash
python scripts/01_generate_scenarios_enhanced.py
```

### Generate Frames Only
```bash
python scripts/02_generate_frames_enhanced.py
```

### Assemble Videos Only
```bash
python scripts/03_assemble_videos_enhanced.py
```

### Run Specific Pipeline Steps
```bash
python scripts/run_pipeline.py generate_scenarios validate_scenarios generate_frames
```

---

## Troubleshooting

### Error: "FIREWORKS_API_KEY not set"
**Solution:** Make sure `.env` file exists and has valid API key
```bash
# Check if .env exists
ls -la .env

# Verify key format
grep FIREWORKS_API_KEY .env
```

### Error: "ffmpeg not found"
**Solution:** Install FFmpeg and add to PATH
```bash
# Test installation
ffmpeg -version

# If not found, install:
# Windows: winget install ffmpeg
# macOS: brew install ffmpeg
# Linux: sudo apt-get install ffmpeg
```

### Error: "Pillow not installed"
**Solution:** Install PIL
```bash
pip install --upgrade Pillow
```

### Audio Generation Fails
**Solution:** Disable TTS in `.env`
```env
ENABLE_TTS=false
```

### Font Issues
**Solution:** System will auto-select available fonts. If issues persist:
- Windows: Install Arial font from Windows/Fonts
- macOS: DejaVuSans fonts are usually available
- Linux: Install fonts package

### Out of Memory
**Solution:** Process fewer scenarios at a time
```bash
# Edit .env or script to reduce BATCH_SIZE
```

---

## Project Structure

```
langapp-automation/
├── .env                           # Configuration (create from .env.example)
├── .env.example                   # Configuration template
├── config.py                      # Load configuration
├── requirements.txt               # Python dependencies
├── app.py                         # Flask web interface
│
├── modules/
│   ├── audio_generator.py        # TTS and audio mixing
│   ├── scenario_validator.py     # Scenario validation
│   └── utils.py                  # Utility functions
│
├── scripts/
│   ├── 01_generate_scenarios_enhanced.py    # Generate scenarios
│   ├── 02_generate_frames_enhanced.py       # Generate frames
│   ├── 03_assemble_videos_enhanced.py       # Create videos
│   ├── 03_assemble_videos.py                # Original video script
│   ├── run_pipeline.py            # Unified pipeline
│   └── [other posting scripts]
│
├── output/
│   ├── videos/                   # Generated MP4 files
│   ├── audio/                    # Generated audio files
│   ├── frames/                   # Generated PNG frames
│   └── [other output]
│
├── data/
│   ├── scenarios_*.json          # Generated scenarios
│   ├── scenarios_latest.json     # Latest scenarios
│   ├── manifest.json             # Frame manifest
│   └── [other data files]
│
├── logs/
│   ├── scenario_gen.log          # Scenario generation log
│   ├── frame_gen.log             # Frame generation log
│   ├── video_assembly.log        # Video assembly log
│   ├── pipeline.log              # Pipeline execution log
│   └── pipeline_results_*.json   # Pipeline results
│
└── templates_web/                # Flask templates
    └── dashboard.html
```

---

## Next Steps

1. **Test the system** with sample scenarios
2. **Adjust settings** based on output quality
3. **Configure posting** scripts for TikTok/Reddit
4. **Set up scheduling** for automated generation
5. **Monitor logs** and iterate on improvements

---

## Common Commands

```bash
# Full pipeline
python scripts/run_pipeline.py

# Generate only
python scripts/01_generate_scenarios_enhanced.py

# Check logs
tail -f logs/pipeline.log
cat logs/pipeline_results_*.json

# Web dashboard (optional)
python app.py

# Install requirements
pip install -r requirements.txt

# Test configuration
python test_models.py
```

---

## Support

For issues:
1. Check logs in `logs/` directory
2. Review `.env` configuration
3. Ensure all dependencies installed: `pip install -r requirements.txt`
4. Check internet connection for API calls
5. Verify API keys are valid

---

**Happy video generation! 🎬**
