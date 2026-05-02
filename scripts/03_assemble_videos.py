import json
import os
import sys
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core'))
from config import (
    DATA_DIR, OUTPUT_DIR, FFMPEG_PATH, SECONDS_PER_FRAME,
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_CRF, VIDEO_PRESET, VIDEO_CODEC
)

def create_video_from_frames(frames, output_path):
    frames_dir = os.path.dirname(frames[0])
    concat_file = os.path.join(frames_dir, "concat.txt")
    
    with open(concat_file, "w", encoding="utf-8") as f:
        for frame in frames:
            abs_path = os.path.abspath(frame)
            dur = SECONDS_PER_FRAME
            f.write(f"file '{abs_path}'\n")
            f.write(f"duration {dur}\n")
        f.write(f"file '{os.path.abspath(frames[-1])}'\n")
    
    cmd = [
        FFMPEG_PATH, "-y",
        "-f", "concat", "-safe", "0",
        "-i", concat_file,
        "-c:v", VIDEO_CODEC,
        "-pix_fmt", "yuv420p",
        "-vf", f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT}:force_original_aspect_ratio=decrease,pad={VIDEO_WIDTH}:{VIDEO_HEIGHT}:(ow-iw)/2:(oh-ih)/2",
        "-preset", VIDEO_PRESET,
        "-crf", str(VIDEO_CRF),
        output_path
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            print(f"FFmpeg error: {result.stderr[-500:]}")
            return False
        return True
    except FileNotFoundError:
        print("ffmpeg not found. Install from https://ffmpeg.org/download.html")
        print("Or run: winget install ffmpeg")
        return False
    except subprocess.TimeoutExpired:
        print("FFmpeg timed out")
        return False

def generate_captions(scenario):
    hashtags = " ".join(scenario.get("hashtags", []))
    return f"{scenario['hook_en']} {scenario['cta_en']} {hashtags}"

def assemble_all_videos():
    manifest_path = os.path.join(DATA_DIR, "manifest.json")
    if not os.path.exists(manifest_path):
        print("No manifest found. Run 02_generate_frames.py first.")
        return
    
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)
    
    videos_dir = os.path.join(OUTPUT_DIR, "videos")
    os.makedirs(videos_dir, exist_ok=True)
    
    captions = []
    success_count = 0
    
    for entry in manifest:
        sid = entry["id"]
        output_path = os.path.join(videos_dir, f"video_{sid:03d}.mp4")
        
        if os.path.exists(output_path):
            print(f"  Skipping scenario {sid} (video exists)")
            success_count += 1
            caption = generate_captions(entry)
            captions.append({"id": sid, "caption": caption, "video": output_path})
            continue
        
        print(f"  Processing scenario {sid}...")
        ok = create_video_from_frames(entry["frames"], output_path)
        
        if ok:
            caption = generate_captions(entry)
            captions.append({"id": sid, "caption": caption, "video": output_path})
            success_count += 1
            print(f"  -> OK: {output_path}")
        else:
            print(f"  -> FAILED: scenario {sid}")
    
    captions_path = os.path.join(DATA_DIR, "captions.json")
    with open(captions_path, "w", encoding="utf-8") as f:
        json.dump(captions, f, ensure_ascii=False, indent=2)
    
    print(f"\nDone: {success_count}/{len(manifest)} videos created")
    print(f"Captions saved to {captions_path}")

if __name__ == "__main__":
    assemble_all_videos()
