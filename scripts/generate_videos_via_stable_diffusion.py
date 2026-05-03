#!/usr/bin/env python3
"""
Video Generator using Stable Diffusion WebUI API
Generates video by creating frames and assembling them with ffmpeg
"""

import os
import sys
import json
import requests
import base64
from pathlib import Path
from typing import Optional, Callable, Dict
import subprocess
import time
from datetime import datetime

# Stable Diffusion WebUI API URL
SD_API_URL = os.getenv("SD_API_URL", "http://127.0.0.1:7860")
OUTPUT_DIR = Path(__file__).parent.parent / "output" / "videos"
FRAMES_DIR = Path(__file__).parent.parent / "output" / "frames"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
FRAMES_DIR.mkdir(parents=True, exist_ok=True)


class StableDiffusionVideoGenerator:
    """Генератор видео через Stable Diffusion API"""

    def __init__(self):
        self.api_url = SD_API_URL
        self.num_frames = 8  # 8 кадров на видео
        self.fps = 1  # 1 кадр в секунду = 8 сек видео

    def report_status(self, callback: Optional[Callable], status: str, progress: int, message: str):
        """Отправить статус прогресса"""
        if callback:
            try:
                callback({
                    'status': status,
                    'progress': progress,
                    'message': message
                })
            except Exception as e:
                print(f"Error reporting status: {e}")

    def check_api_connection(self) -> bool:
        """Проверить подключение к API"""
        try:
            response = requests.get(f"{self.api_url}/api/sd-models", timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"API Connection Error: {e}")
            return False

    def generate_frame(self, prompt: str, frame_num: int, seed: int) -> bool:
        """Генерировать один кадр через Stable Diffusion"""
        try:
            payload = {
                "prompt": prompt,
                "negative_prompt": "blurry, low quality, distorted",
                "steps": 20,
                "cfg_scale": 7.5,
                "width": 720,
                "height": 1280,  # 9:16 формат
                "seed": seed + frame_num,  # Разные семена для разных кадров
                "sampler_name": "DPM++ 2M Karras",
                "scheduler": "karras"
            }

            print(f"Generating frame {frame_num}...")
            response = requests.post(
                f"{self.api_url}/api/txt2img",
                json=payload,
                timeout=120
            )

            if response.status_code != 200:
                print(f"API Error: {response.text}")
                return False

            result = response.json()

            if "images" not in result or not result["images"]:
                print("No image in response")
                return False

            # Сохранить кадр
            image_data = base64.b64decode(result["images"][0])
            frame_path = FRAMES_DIR / f"frame_{frame_num:03d}.png"

            with open(frame_path, "wb") as f:
                f.write(image_data)

            print(f"✅ Frame {frame_num} saved: {frame_path}")
            return True

        except Exception as e:
            print(f"Error generating frame: {e}")
            return False

    def assemble_video(self, output_path: Path, prompt_theme: str) -> bool:
        """Собрать видео из кадров"""
        try:
            # Найти все кадры
            frames = sorted(FRAMES_DIR.glob("frame_*.png"))

            if not frames:
                print("No frames found")
                return False

            print(f"Assembling {len(frames)} frames into video...")

            # FFmpeg команда для создания видео из кадров
            cmd = [
                "ffmpeg",
                "-framerate", str(self.fps),
                "-i", str(FRAMES_DIR / "frame_%03d.png"),
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-crf", "23",
                str(output_path),
                "-y"  # Перезаписать файл без вопросов
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)

            if result.returncode != 0:
                print(f"FFmpeg Error: {result.stderr}")
                return False

            print(f"✅ Video assembled: {output_path}")

            # Очистить кадры
            for frame in frames:
                frame.unlink()

            return True

        except Exception as e:
            print(f"Error assembling video: {e}")
            return False

    def generate_video(
        self,
        prompt: str,
        output_dir: str = None,
        callback: Optional[Callable] = None
    ) -> Dict:
        """
        Генерировать видео

        Args:
            prompt: Текстовое описание для видео
            output_dir: Директория для сохранения видео
            callback: Функция для отправки статуса прогресса

        Returns:
            Dict с ключами: success, url, error, status
        """
        try:
            if output_dir is None:
                output_dir = str(OUTPUT_DIR)

            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

            # Проверить подключение к API
            self.report_status(callback, "CHECKING", 5, "🔍 Проверка подключения к Stable Diffusion...")

            if not self.check_api_connection():
                error_msg = f"Cannot connect to Stable Diffusion API at {self.api_url}. Is WebUI running?"
                self.report_status(callback, "ERROR", 0, f"❌ {error_msg}")
                return {
                    'success': False,
                    'url': None,
                    'error': error_msg,
                    'status': 'ERROR'
                }

            # Генерировать кадры
            self.report_status(callback, "STARTING", 10, "🎬 Начинаю генерацию видео...")

            seed = int(time.time()) % 1000000
            successful_frames = 0

            for frame_num in range(1, self.num_frames + 1):
                progress = 10 + (frame_num / self.num_frames) * 70
                self.report_status(
                    callback,
                    "PROCESSING",
                    int(progress),
                    f"🖼️ Генерирую кадр {frame_num}/{self.num_frames}..."
                )

                if self.generate_frame(prompt, frame_num, seed):
                    successful_frames += 1
                else:
                    # Продолжить даже если один кадр не получился
                    print(f"Warning: Frame {frame_num} generation failed, continuing...")

            if successful_frames < 3:
                error_msg = f"Generated only {successful_frames} frames, need at least 3"
                self.report_status(callback, "ERROR", 0, f"❌ {error_msg}")
                return {
                    'success': False,
                    'url': None,
                    'error': error_msg,
                    'status': 'ERROR'
                }

            # Собрать видео
            self.report_status(callback, "ASSEMBLING", 85, "🎞️ Собираю видео из кадров...")

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = output_dir / f"video_sd_{timestamp}.mp4"

            if not self.assemble_video(output_file, prompt):
                error_msg = "Failed to assemble video with ffmpeg"
                self.report_status(callback, "ERROR", 0, f"❌ {error_msg}")
                return {
                    'success': False,
                    'url': None,
                    'error': error_msg,
                    'status': 'ERROR'
                }

            # Успех!
            self.report_status(callback, "COMPLETE", 100, "✅ Видео готово!")

            return {
                'success': True,
                'url': str(output_file),
                'error': None,
                'status': 'COMPLETE'
            }

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            self.report_status(callback, "ERROR", 0, f"❌ {error_msg}")
            return {
                'success': False,
                'url': None,
                'error': error_msg,
                'status': 'ERROR'
            }


if __name__ == "__main__":
    # Пример использования
    generator = StableDiffusionVideoGenerator()

    def status_callback(info):
        print(f"[{info['status']}] {info['progress']}% - {info['message']}")

    result = generator.generate_video(
        prompt="Красивое видео про приложение для изучения языков, яркие цвета, современный дизайн",
        callback=status_callback
    )

    print(f"\nResult: {result}")
