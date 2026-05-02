import os
from dotenv import load_dotenv
import pathlib

load_dotenv()

BASE_DIR = pathlib.Path(__file__).parent.parent  # Go up from core/ to langapp-automation/

APP_NAME = os.getenv("APP_NAME", "LinguaStart")
APP_LINK = os.getenv("APP_LINK", "https://play.google.com/store/apps/details?id=com.linguastart.app")
APP_STORE_ID = os.getenv("APP_STORE_ID", "com.linguastart.app")
APP_SLOGAN_EN = os.getenv("APP_SLOGAN_EN", "Master Languages Together")
APP_SLOGAN_AR = os.getenv("APP_SLOGAN_AR", "اتقن اللغات معاً")

FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY", "")
FIREWORKS_BASE_URL = os.getenv("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1")
FIREWORKS_MODEL = os.getenv("FIREWORKS_MODEL", "accounts/fireworks/models/minimax-m2p7")
FIREWORKS_MODEL_CHEAP = FIREWORKS_MODEL
FIREWORKS_MODEL_QUALITY = FIREWORKS_MODEL

if not FIREWORKS_API_KEY:
    raise ValueError("FIREWORKS_API_KEY not set. Please create .env file from .env.example")

# Grok API Configuration
GROK_API_KEY = os.getenv("GROK_API_KEY", "")
GROK_BASE_URL = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
GROK_MODEL = os.getenv("GROK_MODEL", "grok-2")

REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USERNAME = os.getenv("REDDIT_USERNAME", "")
REDDIT_PASSWORD = os.getenv("REDDIT_PASSWORD", "")
REDDIT_SUBREDDITS = os.getenv("REDDIT_SUBREDDITS", "languagelearning,learn_arabic,learnenglish").split(",")

TIKTOK_USERNAME = os.getenv("TIKTOK_USERNAME", "")
TIKTOK_PASSWORD = os.getenv("TIKTOK_PASSWORD", "")

CHROME_DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "chromedriver")
FFMPEG_PATH = os.getenv("FFMPEG_PATH", "ffmpeg")

POST_SCHEDULE_HOUR = int(os.getenv("POST_SCHEDULE_HOUR", "18"))
POST_SCHEDULE_MINUTE = int(os.getenv("POST_SCHEDULE_MINUTE", "0"))
COMMENTS_CHECK_INTERVAL_MIN = int(os.getenv("COMMENTS_CHECK_INTERVAL_MIN", "120"))
REDDIT_CHECK_INTERVAL_MIN = int(os.getenv("REDDIT_CHECK_INTERVAL_MIN", "30"))
ANALYTICS_DAY = os.getenv("ANALYTICS_DAY", "sunday")

VIDEO_WIDTH = int(os.getenv("VIDEO_WIDTH", "1440"))
VIDEO_HEIGHT = int(os.getenv("VIDEO_HEIGHT", "2560"))
SECONDS_PER_FRAME = float(os.getenv("SECONDS_PER_FRAME", "3.5"))
FPS = int(os.getenv("FPS", "30"))

# Video quality settings
VIDEO_CRF = int(os.getenv("VIDEO_CRF", "18"))  # 18-28: lower is better quality
VIDEO_PRESET = os.getenv("VIDEO_PRESET", "slow")  # ultrafast, fast, medium, slow, veryslow
VIDEO_CODEC = os.getenv("VIDEO_CODEC", "libx264")  # libx264 or libx265 (HEVC)
FONT_PATH_AR = os.getenv("FONT_PATH_AR", "arial.ttf")
FONT_PATH_EN = os.getenv("FONT_PATH_EN", "arial.ttf")

BG_COLOR_DARK = os.getenv("BG_COLOR_DARK", "#0f0f23")
BG_COLOR_ACCENT = os.getenv("BG_COLOR_ACCENT", "#1a1a3e")
TEXT_COLOR_WHITE = os.getenv("TEXT_COLOR_WHITE", "#ffffff")
TEXT_COLOR_GOLD = os.getenv("TEXT_COLOR_GOLD", "#ffd700")
TEXT_COLOR_GREEN = os.getenv("TEXT_COLOR_GREEN", "#00e676")

ENABLE_TTS = os.getenv("ENABLE_TTS", "true").lower() == "true"
ENABLE_BACKGROUND_MUSIC = os.getenv("ENABLE_BACKGROUND_MUSIC", "true").lower() == "true"
VOICE_LANGUAGE = os.getenv("VOICE_LANGUAGE", "ar-EG")
MUSIC_VOLUME = float(os.getenv("MUSIC_VOLUME", "0.3"))

OUTPUT_DIR = os.getenv("OUTPUT_DIR", str(BASE_DIR / "output"))
DATA_DIR = os.getenv("DATA_DIR", str(BASE_DIR / "data"))
LOGS_DIR = os.getenv("LOGS_DIR", str(BASE_DIR / "logs"))
AUDIO_DIR = os.getenv("AUDIO_DIR", str(BASE_DIR / "output" / "audio"))
