import json
import os
import sys
import logging
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from config import DATA_DIR, OUTPUT_DIR, VIDEO_WIDTH, VIDEO_HEIGHT, SECONDS_PER_FRAME, LOGS_DIR, ENABLE_TTS
from modules.scenario_validator import ScenarioValidator

try:
    from moviepy.editor import (
        ImageClip, concatenate_videoclips, CompositeVideoClip,
        TextClip, ColorClip, vfx, AudioFileClip
    )
except ImportError:
    print("moviepy not installed. Run: pip install moviepy")
    sys.exit(1)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "video_assembly.log")),
        logging.StreamHandler()
    ]
)


def create_fade_transition(duration=0.5):
    """Create a fade transition effect"""
    return lambda gf, t: gf(t) * (1 - min(t / duration, 1))


def apply_fade_in_effect(clip, duration=0.3):
    """Apply fade in effect to start of clip"""
    return clip.fx(vfx.fadein, duration)


def apply_fade_out_effect(clip, duration=0.3):
    """Apply fade out effect to end of clip"""
    return clip.fx(vfx.fadeout, duration)


def apply_zoom_effect(clip, start_zoom=0.9, end_zoom=1.0, duration=None):
    """Apply zoom effect to clip"""
    if duration is None:
        duration = clip.duration

    def zoom_func(gf, t):
        zoom = start_zoom + (end_zoom - start_zoom) * (t / duration)
        return gf(t).resize(zoom)

    return clip.fl(zoom_func)


def adjust_frame_duration(frame_path: str, content: str = None) -> float:
    """Calculate frame duration based on content"""
    base_duration = SECONDS_PER_FRAME

    if content:
        word_count = len(content.split())
        reading_time = max(word_count * 0.3, 1.0)
        return min(max(reading_time, 1.5), 4.0)

    return base_duration


def create_video_from_frames(frames: list, output_path: str, audio_file: str = None,
                              add_effects: bool = True) -> bool:
    """Create video from frames with optional effects and audio"""
    try:
        if not frames:
            logger.error("No frames provided")
            return False

        clips = []
        for i, frame_path in enumerate(frames):
            if not os.path.exists(frame_path):
                logger.warning(f"Frame not found: {frame_path}")
                continue

            duration = adjust_frame_duration(frame_path)
            clip = ImageClip(frame_path).set_duration(duration)

            if add_effects:
                if i == 0:
                    clip = apply_fade_in_effect(clip, duration=0.3)
                elif i == len(frames) - 1:
                    clip = apply_fade_out_effect(clip, duration=0.5)
                else:
                    clip = apply_zoom_effect(clip, start_zoom=0.98, end_zoom=1.02)

            clip = clip.set_position("center").resize(width=VIDEO_WIDTH, height=VIDEO_HEIGHT)
            clips.append(clip)

        if not clips:
            logger.error("No valid clips created")
            return False

        logger.info(f"Concatenating {len(clips)} clips...")
        final_video = concatenate_videoclips(clips)

        if audio_file and os.path.exists(audio_file):
            logger.info(f"Adding audio: {audio_file}")
            audio = AudioFileClip(audio_file)
            if audio.duration > final_video.duration:
                audio = audio.set_duration(final_video.duration)
            final_video = final_video.set_audio(audio)

        logger.info(f"Writing video: {output_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        final_video.write_videofile(
            output_path,
            fps=30,
            codec='libx264',
            audio_codec='aac',
            verbose=False,
            logger=None
        )

        logger.info(f"Video created successfully: {output_path}")
        return True

    except Exception as e:
        logger.error(f"Error creating video: {e}", exc_info=True)
        return False


def generate_captions(scenario: dict) -> str:
    """Generate captions for video"""
    hashtags = " ".join(scenario.get("hashtags", []))
    return f"{scenario['hook_en']} {scenario['cta_en']} {hashtags}"


def assemble_all_videos(use_effects: bool = True, audio_enabled: bool = ENABLE_TTS):
    """Assemble all videos from manifest"""
    manifest_path = os.path.join(DATA_DIR, "manifest.json")
    if not os.path.exists(manifest_path):
        logger.error("No manifest found. Run 02_generate_frames.py first.")
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    os.makedirs(LOGS_DIR, exist_ok=True)
    videos_dir = os.path.join(OUTPUT_DIR, "videos")
    os.makedirs(videos_dir, exist_ok=True)

    captions = []
    success_count = 0
    failed_scenarios = []

    logger.info(f"Starting video assembly for {len(manifest)} scenarios...")

    for i, entry in enumerate(manifest, 1):
        sid = entry["id"]
        output_path = os.path.join(videos_dir, f"video_{sid:03d}.mp4")

        if os.path.exists(output_path):
            logger.info(f"[{i}/{len(manifest)}] Skipping scenario {sid} (video exists)")
            success_count += 1
            caption = generate_captions(entry)
            captions.append({"id": sid, "caption": caption, "video": output_path})
            continue

        logger.info(f"[{i}/{len(manifest)}] Processing scenario {sid}...")

        audio_file = None
        if audio_enabled:
            audio_file = os.path.join(OUTPUT_DIR, "audio", f"scenario_{sid:03d}_audio.mp3")

        ok = create_video_from_frames(entry["frames"], output_path, audio_file, add_effects=use_effects)

        if ok:
            caption = generate_captions(entry)
            captions.append({"id": sid, "caption": caption, "video": output_path})
            success_count += 1
            logger.info(f"[{i}/{len(manifest)}] ✓ OK: {output_path}")
        else:
            failed_scenarios.append(sid)
            logger.error(f"[{i}/{len(manifest)}] ✗ FAILED: scenario {sid}")

    captions_path = os.path.join(DATA_DIR, "captions.json")
    with open(captions_path, "w", encoding="utf-8") as f:
        json.dump(captions, f, ensure_ascii=False, indent=2)

    summary = f"\nAssembly Summary:\n✓ Success: {success_count}/{len(manifest)}\n✗ Failed: {len(failed_scenarios)}"
    if failed_scenarios:
        summary += f"\nFailed IDs: {failed_scenarios}"
    logger.info(summary)
    print(summary)

    return success_count, len(failed_scenarios)


if __name__ == "__main__":
    assemble_all_videos()
