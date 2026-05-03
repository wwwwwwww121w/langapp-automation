#!/usr/bin/env python3
"""
Video Generator using Stable Diffusion (diffusers) — прямая интеграция
Без WebUI — модели загружаются напрямую через HuggingFace diffusers
Генерирует кадры и собирает видео через ffmpeg
"""

import os
import sys
import time
import base64
import subprocess
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Callable, Dict

import torch
from PIL import Image
from diffusers import (
    StableDiffusionPipeline,
    DPMSolverMultistepScheduler,
    EulerAncestralDiscreteScheduler,
)

# ─── Пути ───────────────────────────────────────────────────────────────────
SD_WEBUI_MODELS = Path(
    r"C:\Users\Tetro\Downloads\stable-diffusion-webui-master"
    r"\stable-diffusion-webui-master\models\Stable-diffusion"
)
BASE_DIR    = Path(__file__).parent.parent
OUTPUT_DIR  = BASE_DIR / "output" / "videos"
FRAMES_DIR  = BASE_DIR / "output" / "frames"
MODELS_DIR  = BASE_DIR / "models"

for d in (OUTPUT_DIR, FRAMES_DIR, MODELS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# ─── Настройки ───────────────────────────────────────────────────────────────
DEFAULT_MODEL   = os.getenv("SD_MODEL", "runwayml/stable-diffusion-v1-5")
NUM_FRAMES      = int(os.getenv("SD_NUM_FRAMES", "8"))
VIDEO_FPS       = int(os.getenv("SD_FPS", "1"))          # 1 fps → 8 сек при 8 кадрах
STEPS           = int(os.getenv("SD_STEPS", "25"))
CFG_SCALE       = float(os.getenv("SD_CFG", "7.5"))
WIDTH           = int(os.getenv("SD_WIDTH", "512"))
HEIGHT          = int(os.getenv("SD_HEIGHT", "912"))      # ближайшее к 9:16
NEGATIVE_PROMPT = (
    "blurry, low quality, distorted, ugly, bad anatomy, "
    "watermark, text, nsfw, low resolution"
)


def _detect_device() -> str:
    if torch.cuda.is_available():
        name = torch.cuda.get_device_name(0)
        vram = torch.cuda.get_device_properties(0).total_memory / 1024**3
        print(f"✅ GPU: {name} ({vram:.1f} GB VRAM)")
        return "cuda"
    print("⚠️  GPU не найден — используется CPU (очень медленно!)")
    return "cpu"


def _find_local_checkpoint() -> Optional[Path]:
    """Ищет .safetensors / .ckpt в папке SD WebUI и в models/"""
    for folder in (SD_WEBUI_MODELS, MODELS_DIR):
        for ext in ("*.safetensors", "*.ckpt"):
            files = sorted(folder.glob(ext))
            if files:
                print(f"📦 Найдена локальная модель: {files[0]}")
                return files[0]
    return None


class StableDiffusionVideoGenerator:
    """Генератор видео напрямую через diffusers (без WebUI)"""

    def __init__(self):
        self.device   = _detect_device()
        self.dtype     = torch.float16 if self.device == "cuda" else torch.float32
        self.pipeline: Optional[StableDiffusionPipeline] = None

    # ── загрузка модели ───────────────────────────────────────────────────────
    def _load_pipeline(self) -> StableDiffusionPipeline:
        if self.pipeline is not None:
            return self.pipeline

        local_ckpt = _find_local_checkpoint()

        if local_ckpt:
            print(f"🔄 Загружаю локальный checkpoint: {local_ckpt.name}")
            pipe = StableDiffusionPipeline.from_single_file(
                str(local_ckpt),
                torch_dtype=self.dtype,
                safety_checker=None,
            )
        else:
            print(f"🌐 Скачиваю модель с HuggingFace: {DEFAULT_MODEL}")
            print("   (первый раз займёт несколько минут)")
            pipe = StableDiffusionPipeline.from_pretrained(
                DEFAULT_MODEL,
                torch_dtype=self.dtype,
                safety_checker=None,
                cache_dir=str(MODELS_DIR),
            )

        # быстрый планировщик
        pipe.scheduler = DPMSolverMultistepScheduler.from_config(
            pipe.scheduler.config,
            use_karras_sigmas=True,
        )

        pipe = pipe.to(self.device)

        # оптимизации памяти
        if self.device == "cuda":
            pipe.enable_attention_slicing()
            try:
                pipe.enable_xformers_memory_efficient_attention()
                print("✅ xFormers включён")
            except Exception:
                print("ℹ️  xFormers недоступен — используется стандартный attention")

        self.pipeline = pipe
        print("✅ Модель загружена")
        return pipe

    # ── генерация одного кадра ───────────────────────────────────────────────
    def _generate_frame(self, prompt: str, seed: int, frame_idx: int) -> Image.Image:
        pipe = self._load_pipeline()
        generator = torch.Generator(device=self.device).manual_seed(seed + frame_idx * 7)

        result = pipe(
            prompt=prompt,
            negative_prompt=NEGATIVE_PROMPT,
            width=WIDTH,
            height=HEIGHT,
            num_inference_steps=STEPS,
            guidance_scale=CFG_SCALE,
            generator=generator,
        )
        return result.images[0]

    # ── сборка видео через ffmpeg ─────────────────────────────────────────────
    @staticmethod
    def _assemble_video(frames_dir: Path, output_path: Path) -> bool:
        pattern = str(frames_dir / "frame_%03d.png")
        cmd = [
            "ffmpeg", "-y",
            "-framerate", str(VIDEO_FPS),
            "-i", pattern,
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-crf", "20",
            "-vf", "scale=720:-2",          # нормализуем ширину до 720
            str(output_path),
        ]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            if res.returncode != 0:
                print(f"FFmpeg error: {res.stderr[-500:]}")
                return False
            return True
        except FileNotFoundError:
            print("❌ ffmpeg не найден! Установите ffmpeg и добавьте в PATH.")
            return False
        except subprocess.TimeoutExpired:
            print("❌ FFmpeg завис (timeout 120 сек)")
            return False

    # ── очистка кадров ────────────────────────────────────────────────────────
    @staticmethod
    def _clear_frames(frames_dir: Path):
        for f in frames_dir.glob("frame_*.png"):
            f.unlink(missing_ok=True)

    # ── публичный метод ───────────────────────────────────────────────────────
    def generate_video(
        self,
        prompt: str,
        output_dir: Optional[str] = None,
        callback: Optional[Callable[[Dict], None]] = None,
    ) -> Dict:
        """
        Генерирует видео из текстового описания.

        Returns:
            {"success": bool, "url": str | None, "error": str | None, "status": str}
        """

        def report(status: str, progress: int, message: str):
            print(f"[{status}] {progress}% — {message}")
            if callback:
                try:
                    callback({"status": status, "progress": progress, "message": message})
                except Exception as e:
                    print(f"Callback error: {e}")

        out_dir = Path(output_dir) if output_dir else OUTPUT_DIR
        out_dir.mkdir(parents=True, exist_ok=True)

        # временная папка для кадров этого видео
        run_id     = datetime.now().strftime("%Y%m%d_%H%M%S")
        frames_dir = FRAMES_DIR / run_id
        frames_dir.mkdir(parents=True, exist_ok=True)

        try:
            # ── загрузка модели ──────────────────────────────────────────────
            report("LOADING", 5, "🔄 Загружаю модель Stable Diffusion...")
            self._load_pipeline()

            # ── генерация кадров ─────────────────────────────────────────────
            base_seed = int(time.time()) % 10_000_000
            ok_frames = 0

            for i in range(1, NUM_FRAMES + 1):
                pct = 10 + int((i / NUM_FRAMES) * 75)
                report("PROCESSING", pct, f"🖼️ Генерирую кадр {i}/{NUM_FRAMES}...")

                img  = self._generate_frame(prompt, base_seed, i)
                path = frames_dir / f"frame_{i:03d}.png"
                img.save(path)
                ok_frames += 1
                print(f"   ✅ Кадр {i} сохранён ({path.name})")

            if ok_frames < 3:
                raise RuntimeError(f"Сгенерировано только {ok_frames} кадров, нужно минимум 3")

            # ── сборка видео ─────────────────────────────────────────────────
            report("ASSEMBLING", 88, "🎞️ Собираю видео из кадров...")
            out_file = out_dir / f"video_sd_{run_id}.mp4"

            if not self._assemble_video(frames_dir, out_file):
                raise RuntimeError("FFmpeg не смог собрать видео")

            report("COMPLETE", 100, "✅ Видео готово!")
            return {"success": True, "url": str(out_file), "error": None, "status": "COMPLETE"}

        except Exception as e:
            msg = str(e)[:300]
            report("ERROR", 0, f"❌ {msg}")
            return {"success": False, "url": None, "error": msg, "status": "ERROR"}

        finally:
            # всегда удаляем временные кадры
            shutil.rmtree(frames_dir, ignore_errors=True)


# ── CLI тест ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    gen = StableDiffusionVideoGenerator()

    def cb(info):
        print(f"  [{info['status']}] {info['progress']}% — {info['message']}")

    result = gen.generate_video(
        prompt=(
            "beautiful mobile app interface for language learning, "
            "modern UI design, bright colors, vertical 9:16 format, "
            "high quality, professional"
        ),
        callback=cb,
    )
    print("\n=== Результат ===")
    print(result)
