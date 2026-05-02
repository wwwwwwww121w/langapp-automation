# ⚡ Quick Start - Video Generation

## 30-Second Setup

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure (edit with your API key)
notepad .env

# 3. Run pipeline
python scripts/run_pipeline.py

# Done! Check output/videos/ for your videos
```

---

## Common Tasks

### Generate Videos from Scratch
```bash
python scripts/run_pipeline.py
```
📁 Output: `output/videos/*.mp4`

### Generate Only Scenarios
```bash
python scripts/01_generate_scenarios_enhanced.py
```
📁 Output: `data/scenarios_latest.json`

### Generate Only Frames
```bash
python scripts/02_generate_frames_enhanced.py
```
📁 Output: `output/frames/`

### Generate Only Videos from Frames
```bash
python scripts/03_assemble_videos_enhanced.py
```
📁 Output: `output/videos/*.mp4`

### Run Web Dashboard
```bash
python app.py
```
🌐 Open: http://localhost:5000

### View Logs
```bash
# Real-time pipeline log
tail -f logs/pipeline.log

# View all scenarios generated
cat data/scenarios_latest.json | python -m json.tool

# View execution results
cat logs/pipeline_results_*.json | python -m json.tool
```

---

## Configuration Quick Reference

### Enable/Disable Features
```env
ENABLE_TTS=true                 # Turn on text-to-speech
ENABLE_BACKGROUND_MUSIC=true    # Add background music
```

### API Keys
```env
FIREWORKS_API_KEY=your_key_here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google/creds.json
REDDIT_CLIENT_ID=your_id
```

### Video Settings
```env
VIDEO_WIDTH=1080
VIDEO_HEIGHT=1920
SECONDS_PER_FRAME=2
FPS=30
```

### App Details
```env
APP_NAME=ArabicEngLearn
APP_LINK=https://play.google.com/store/apps/details?id=...
```

---

## File Locations

| What | Where |
|------|-------|
| Generated videos | `output/videos/video_001.mp4` etc. |
| Video frames | `output/frames/scenario_001/` |
| Generated audio | `output/audio/` |
| Scenario data | `data/scenarios_latest.json` |
| Execution logs | `logs/pipeline.log` |
| Configuration | `.env` |

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not set" | Update `.env` with valid key |
| "ffmpeg not found" | Install: `winget install ffmpeg` |
| "No module named PIL" | Install: `pip install Pillow` |
| Audio fails | Set `ENABLE_TTS=false` in `.env` |
| Out of memory | Reduce number of scenarios generated |

---

## Advanced Usage

### Create Specific Type of Videos
```python
# In scripts, modify the batch types
types = ["fact"]  # Only generate "fact" videos
```

### Custom Colors
Edit `.env`:
```env
BG_COLOR_DARK=#0f0f23
BG_COLOR_ACCENT=#1a1a3e
TEXT_COLOR_GOLD=#ffd700
```

### Disable Effects
Edit `scripts/03_assemble_videos_enhanced.py`:
```python
ok = create_video_from_frames(entry["frames"], output_path, 
                             add_effects=False)  # Disable effects
```

### Skip Audio Generation
Edit `scripts/run_pipeline.py`:
```python
success = pipeline.run(steps=[
    "generate_scenarios",
    "validate_scenarios",
    # "generate_audio",  # <-- Skip this
    "generate_frames",
    "assemble_videos"
])
```

---

## Performance Tips

- ✅ **Disable TTS** if audio generation is slow: `ENABLE_TTS=false`
- ✅ **Process in batches**: System auto-batches scenarios
- ✅ **Use SSD**: Faster storage improves frame generation
- ✅ **Monitor memory**: Large videos may need 4GB+ RAM
- ✅ **Parallel processing**: Each step can be run independently

---

## Useful Imports (for development)

```python
# Load configuration
from config import *

# Audio generation
from modules.audio_generator import AudioGenerator

# Validation
from modules.scenario_validator import ScenarioValidator

# Utilities
from modules.utils import retry, ProgressTracker, CircuitBreaker

# Retry with backoff
@retry(max_attempts=3, delay=1.0, backoff=2.0)
def api_call():
    return client.chat.completions.create(...)
```

---

## API Reference

### AudioGenerator
```python
gen = AudioGenerator()
audio_file = gen.generate_tts("مرحبا", language_code="ar-EG")
mixed = gen.mix_audio(speech_file, music_file)
duration = gen.get_audio_duration(audio_file)
```

### ScenarioValidator
```python
valid, errors = ScenarioValidator.validate_scenario(scenario)
valid_list, invalid = ScenarioValidator.validate_scenarios(scenarios)
fixed = ScenarioValidator.fix_scenario(bad_scenario)
```

### Utils
```python
tracker = ProgressTracker(total=100, name="Processing")
tracker.update(1, "Processing item")

breaker = CircuitBreaker(failure_threshold=5)
success, result = breaker.call(risky_function)

@retry(max_attempts=3)
def my_function():
    return result
```

---

## Keyboard Shortcuts

When running pipeline:
- `Ctrl+C` - Stop execution
- See logs in real-time: `tail -f logs/pipeline.log`

---

## Getting Help

1. **Check logs**: `cat logs/pipeline.log`
2. **Read docs**: See `IMPROVEMENTS.md` and `SETUP_GUIDE.md`
3. **Test connection**: `python test_models.py`
4. **Verify config**: `cat .env | grep -v "^#"`

---

## Example Workflow

```bash
# 1. Setup (one time)
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key

# 2. Generate videos
python scripts/run_pipeline.py

# 3. Check results
ls output/videos/
cat logs/pipeline_results_*.json

# 4. Customize if needed
# Edit .env or scripts for different settings

# 5. Regenerate with new settings
python scripts/run_pipeline.py
```

---

## What's New (v2.0)

✨ **Major Improvements:**
- 🔐 Secure API key management (.env)
- 🔊 Text-to-speech audio generation
- 🎵 Background music support
- 🎬 Video effects and transitions
- ✓ Scenario validation system
- 🔄 Advanced error handling & retries
- 📊 Detailed logging and monitoring
- 🔗 Unified pipeline orchestration

---

**Version:** 2.0.0  
**Last Updated:** 2026-04-30  
**Status:** Production Ready ✅
