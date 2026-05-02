import json
import os
import sys
import time
import datetime
import subprocess

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATA_DIR, LOGS_DIR, FIREWORKS_API_KEY

STEPS = [
    ("Step 1: Generate scenarios", "01_generate_scenarios.py", "scripts"),
    ("Step 2: Generate frames", "02_generate_frames.py", "scripts"),
    ("Step 3: Assemble videos", "03_assemble_videos.py", "scripts"),
    ("Step 4: Auto-post TikTok", "04_autopost_tiktok.py", "scripts"),
    ("Step 5: Reddit responder", "05_reddit_responder.py", "scripts"),
    ("Step 6: Comment responder", "06_comment_responder.py", "scripts"),
    ("Step 7: Analytics report", "07_analytics_report.py", "scripts"),
]

BANNER = """
╔══════════════════════════════════════════════╗
║     ArabicEngLearn — Automation Suite        ║
║     AI-Powered Marketing Pipeline             ║
╚══════════════════════════════════════════════╝
"""

def check_dependencies():
    missing = []
    try:
        import openai
    except ImportError:
        missing.append("openai")
    try:
        from PIL import Image
    except ImportError:
        missing.append("Pillow")
    try:
        import praw
    except ImportError:
        missing.append("praw")
    try:
        from selenium import webdriver
    except ImportError:
        missing.append("selenium")
    try:
        import schedule
    except ImportError:
        missing.append("schedule")
    
    if missing:
        print(f"Missing packages: {', '.join(missing)}")
        print(f"Run: pip install {' '.join(missing)}")
        return False
    return True

def check_ffmpeg():
    try:
        result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print("  ffmpeg: OK")
            return True
    except:
        pass
    print("  ffmpeg: NOT FOUND — install from https://ffmpeg.org")
    print("  Or run: winget install ffmpeg")
    return False

def check_config():
    config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "config.py")
    if not os.path.exists(config_path):
        print("  config.py: NOT FOUND")
        return False
    
    sys.path.insert(0, os.path.dirname(config_path))
    from config import FIREWORKS_API_KEY, REDDIT_CLIENT_ID
    
    issues = []
    if FIREWORKS_API_KEY == "YOUR_FIREWORKS_KEY_HERE":
        issues.append("FIREWORKS_API_KEY not set — get from fireworks.ai")
    if REDDIT_CLIENT_ID == "YOUR_ID":
        issues.append("REDDIT credentials not set (optional for now)")
    
    if issues:
        print(f"  config.py: {len(issues)} issue(s)")
        for i in issues:
            print(f"    - {i}")
        return len([i for i in issues if "optional" not in i]) == 0
    print("  config.py: OK")
    return True

def run_step(name, script, subdir):
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), script)
    if not os.path.exists(script_path):
        print(f"  Script not found: {script_path}")
        return False
    
    print(f"\n{'='*50}")
    print(f"  {name}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=False,
            text=True,
            timeout=300
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print(f"  TIMEOUT: {name}")
        return False
    except Exception as e:
        print(f"  ERROR: {e}")
        return False

def show_menu():
    print(BANNER)
    print("Choose an action:\n")
    print("  1. Full pipeline (generate scenarios → frames → videos)")
    print("  2. Generate scenarios only (ChatGPT)")
    print("  3. Generate frames from scenarios")
    print("  4. Assemble videos from frames")
    print("  5. Post next video to TikTok")
    print("  6. Run Reddit responder (once)")
    print("  7. Generate comment replies")
    print("  8. Generate analytics report")
    print("  9. Check dependencies & config")
    print("  10. Login to TikTok (first time)")
    print("  11. Schedule daily posting (runs forever)")
    print("  0. Exit\n")

def main():
    while True:
        show_menu()
        choice = input("Enter choice (0-11): ").strip()
        
        if choice == "0":
            print("Bye!")
            break
        elif choice == "1":
            print("\nRunning full content pipeline...")
            run_step(STEPS[0][0], STEPS[0][1], STEPS[0][2])
            run_step(STEPS[1][0], STEPS[1][1], STEPS[1][2])
            run_step(STEPS[2][0], STEPS[2][1], STEPS[2][2])
            print("\nPipeline complete! Videos are in output/videos/")
        elif choice == "2":
            run_step(STEPS[0][0], STEPS[0][1], STEPS[0][2])
        elif choice == "3":
            run_step(STEPS[1][0], STEPS[1][1], STEPS[1][2])
        elif choice == "4":
            run_step(STEPS[2][0], STEPS[2][1], STEPS[2][2])
        elif choice == "5":
            run_step(STEPS[3][0], STEPS[3][1], STEPS[3][2])
        elif choice == "6":
            run_step(STEPS[4][0], STEPS[4][1], STEPS[4][2])
        elif choice == "7":
            run_step(STEPS[5][0], STEPS[5][1], STEPS[5][2])
        elif choice == "8":
            run_step(STEPS[6][0], STEPS[6][1], STEPS[6][2])
        elif choice == "9":
            print("\nChecking dependencies...")
            check_dependencies()
            check_ffmpeg()
            check_config()
        elif choice == "10":
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "04_autopost_tiktok.py")
            subprocess.run([sys.executable, script_path, "--login"])
        elif choice == "11":
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "04_autopost_tiktok.py")
            subprocess.run([sys.executable, script_path, "--schedule"])
        else:
            print("Invalid choice.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
