import os
import sys
import json
import logging
from pathlib import Path
from typing import Optional, List

sys.path.append(str(Path(__file__).parent.parent))
from config import ENABLE_TTS, VOICE_LANGUAGE, AUDIO_DIR, MUSIC_VOLUME, LOGS_DIR

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

try:
    from google.cloud import texttospeech
except ImportError:
    logger.warning("google-cloud-texttospeech not installed. TTS will be disabled.")
    texttospeech = None

try:
    import pydub
    from pydub import AudioSegment
    from pydub.generators import Sine
    from pydub.exceptions import CouldntDecodeError
except ImportError:
    logger.warning("pydub not installed. Audio mixing will be limited.")
    AudioSegment = None

import requests


class AudioGenerator:
    def __init__(self):
        os.makedirs(AUDIO_DIR, exist_ok=True)
        self.audio_cache = {}
        self._initialize_tts()

    def _initialize_tts(self):
        if ENABLE_TTS and texttospeech:
            try:
                self.tts_client = texttospeech.TextToSpeechClient()
                logger.info("TTS initialized successfully")
            except Exception as e:
                logger.warning(f"Could not initialize TTS: {e}")
                self.tts_client = None
        else:
            self.tts_client = None

    def generate_tts(self, text: str, language_code: str = "ar-EG", gender: str = "FEMALE") -> Optional[str]:
        """Generate TTS audio from text using Google Cloud"""
        if not self.tts_client or not text:
            return None

        try:
            cache_key = f"{language_code}_{text[:50]}_{gender}"
            if cache_key in self.audio_cache:
                return self.audio_cache[cache_key]

            synthesis_input = texttospeech.SynthesisInput(text=text)
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=getattr(texttospeech.SsmlVoiceGender, gender)
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            response = self.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            filename = os.path.join(AUDIO_DIR, f"tts_{hash(text)}.mp3")
            with open(filename, "wb") as out:
                out.write(response.audio_content)

            self.audio_cache[cache_key] = filename
            logger.info(f"Generated TTS: {text[:30]}... -> {filename}")
            return filename

        except Exception as e:
            logger.error(f"TTS generation failed for '{text[:30]}...': {e}")
            return None

    def get_audio_duration(self, filepath: str) -> float:
        """Get duration of audio file in seconds"""
        if not os.path.exists(filepath):
            return 0.0

        try:
            if AudioSegment:
                audio = AudioSegment.from_file(filepath)
                return len(audio) / 1000.0
            return 0.0
        except Exception as e:
            logger.error(f"Could not get duration of {filepath}: {e}")
            return 0.0

    def download_background_music(self, genre: str = "ambient") -> Optional[str]:
        """Download royalty-free background music"""
        try:
            music_file = os.path.join(AUDIO_DIR, f"bg_music_{genre}.mp3")
            if os.path.exists(music_file):
                logger.info(f"Using cached music: {music_file}")
                return music_file

            urls = {
                "ambient": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
                "upbeat": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-5.mp3",
            }

            url = urls.get(genre, urls["ambient"])
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            with open(music_file, "wb") as f:
                f.write(response.content)

            logger.info(f"Downloaded background music: {music_file}")
            return music_file

        except Exception as e:
            logger.warning(f"Could not download background music: {e}")
            return None

    def mix_audio(self, speech_file: str, music_file: Optional[str] = None,
                  output_file: str = None, speech_volume: float = 1.0,
                  music_volume: float = MUSIC_VOLUME) -> Optional[str]:
        """Mix speech and background music"""
        if not AudioSegment:
            logger.warning("pydub not available, skipping audio mixing")
            return speech_file

        if output_file is None:
            output_file = os.path.join(AUDIO_DIR, f"mixed_{os.path.basename(speech_file)}")

        try:
            speech = AudioSegment.from_file(speech_file)
            speech = speech + int(20 * np.log10(speech_volume)) if speech_volume else speech

            if music_file and os.path.exists(music_file):
                music = AudioSegment.from_file(music_file)
                music = music + int(20 * np.log10(music_volume))

                if len(music) < len(speech):
                    repetitions = (len(speech) // len(music)) + 1
                    music = music * repetitions
                    music = music[:len(speech)]

                mixed = speech.overlay(music)
            else:
                mixed = speech

            mixed.export(output_file, format="mp3")
            logger.info(f"Mixed audio saved: {output_file}")
            return output_file

        except Exception as e:
            logger.error(f"Audio mixing failed: {e}")
            return speech_file

    def create_scenario_audio(self, scenario: dict, output_dir: str = None) -> dict:
        """Create complete audio for scenario (hook + items + cta)"""
        if output_dir is None:
            output_dir = AUDIO_DIR

        result = {
            "hook": None,
            "items": [],
            "cta": None,
            "total_duration": 0.0
        }

        try:
            hook_file = self.generate_tts(scenario.get("hook_ar", ""), language_code="ar-EG")
            result["hook"] = hook_file

            for item in scenario.get("items", []):
                text = f"{item.get('ar', '')} {item.get('pronunciation', '')}"
                item_file = self.generate_tts(text, language_code="ar-EG")
                if item_file:
                    result["items"].append(item_file)

            cta_file = self.generate_tts(scenario.get("cta_ar", ""), language_code="ar-EG")
            result["cta"] = cta_file

            total = sum(self.get_audio_duration(f) for f in [result["hook"]] + result["items"] + [result["cta"]] if f)
            result["total_duration"] = total

            logger.info(f"Created audio for scenario {scenario.get('id', 'unknown')}, duration: {total:.1f}s")
            return result

        except Exception as e:
            logger.error(f"Error creating scenario audio: {e}")
            return result


if __name__ == "__main__":
    gen = AudioGenerator()
    scenario = {
        "hook_ar": "هل تعرف أصول الكلمات الإنجليزية من العربية؟",
        "items": [{"ar": "علم", "pronunciation": "ilm"}, {"ar": "كيمياء", "pronunciation": "kimia"}],
        "cta_ar": "تعلم معنا"
    }
    audio = gen.create_scenario_audio(scenario)
    print(f"Audio created: {audio}")
