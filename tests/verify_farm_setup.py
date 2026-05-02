#!/usr/bin/env python3
"""
Verify LinguaStart Video Farm Setup
Checks all required configurations before starting the bot
"""

import os
import sys
from pathlib import Path

def check_file_exists(path: str, description: str) -> bool:
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✅ {description}")
        return True
    else:
        print(f"❌ {description} - NOT FOUND: {path}")
        return False

def check_directory_exists(path: str, description: str) -> bool:
    """Check if directory exists"""
    if os.path.isdir(path):
        print(f"✅ {description}")
        return True
    else:
        print(f"⚠️  {description} - NOT FOUND (will be created): {path}")
        return False

def check_env_variable(var_name: str, description: str, required: bool = False) -> bool:
    """Check if environment variable is set"""
    value = os.getenv(var_name, "")

    if value and value != "your_telegram_bot_token_here" and value != "your_telegram_user_id_here":
        masked = value[:10] + "..." if len(value) > 10 else value
        print(f"✅ {description}: {masked}")
        return True
    elif not required:
        print(f"⚠️  {description}: NOT SET (optional)")
        return True
    else:
        print(f"❌ {description}: MISSING or NOT CONFIGURED")
        return False

def main():
    """Run all checks"""
    print("\n" + "="*60)
    print("  LinguaStart Video Farm Setup Verification")
    print("="*60 + "\n")

    all_good = True

    # Check Python version
    print("🐍 Python Environment:")
    if sys.version_info >= (3, 8):
        print(f"✅ Python version: {sys.version.split()[0]}")
    else:
        print(f"❌ Python 3.8+ required, you have {sys.version}")
        all_good = False

    # Load .env file
    print("\n📋 Configuration Files:")
    env_file = ".env"
    if not check_file_exists(env_file, ".env file"):
        print("   ⚠️  Creating placeholder .env file...")
        with open(env_file, "w") as f:
            f.write("# LinguaStart Configuration\n")
            f.write("TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here\n")
            f.write("TELEGRAM_ADMIN_ID=your_telegram_user_id_here\n")
        all_good = False

    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Check configuration
    print("\n🔐 Telegram Bot Configuration:")
    token_ok = check_env_variable(
        "TELEGRAM_BOT_TOKEN",
        "Bot Token",
        required=True
    )
    admin_ok = check_env_variable(
        "TELEGRAM_ADMIN_ID",
        "Admin ID",
        required=True
    )

    if not (token_ok and admin_ok):
        all_good = False

    # Check Python modules
    print("\n📦 Required Python Packages:")
    packages = [
        ("telegram", "python-telegram-bot"),
        ("PIL", "Pillow"),
        ("openai", "openai"),
        ("ffmpeg", "ffmpeg-python (optional)"),
    ]

    for module, package_name in packages:
        try:
            __import__(module)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - Run: pip install {package_name.split()[0]}")
            if "optional" not in package_name:
                all_good = False

    # Check directories
    print("\n📂 Directory Structure:")
    dirs = [
        ("scripts", "Scripts directory"),
        ("output", "Output directory"),
        ("output/videos", "Videos directory"),
        ("output/frames", "Frames directory"),
        ("data", "Data directory"),
        ("logs", "Logs directory"),
    ]

    for dir_path, description in dirs:
        if not check_directory_exists(dir_path, description):
            os.makedirs(dir_path, exist_ok=True)
            print(f"   Created: {dir_path}")

    # Check scripts
    print("\n🔧 Pipeline Scripts:")
    scripts = [
        ("scripts/01_generate_scenarios.py", "Scenario generation"),
        ("scripts/02_generate_frames.py", "Frame generation"),
        ("scripts/03_assemble_videos.py", "Video assembly"),
    ]

    for script_path, description in scripts:
        check_file_exists(script_path, description)

    # Check bot files
    print("\n🤖 Bot Files:")
    bot_files = [
        ("telegram_bot.py", "Main bot script"),
        ("start_farm_mode.bat", "Farm mode launcher"),
        ("TELEGRAM_SETUP.md", "Setup guide"),
        ("FARM_MODE_README.md", "Farm mode documentation"),
    ]

    for file_path, description in bot_files:
        check_file_exists(file_path, description)

    # Summary
    print("\n" + "="*60)
    if all_good and token_ok and admin_ok:
        print("✅ ALL CHECKS PASSED!")
        print("\n🚀 You're ready to start the bot!")
        print("\n📝 Next steps:")
        print("   1. Edit .env file with your Telegram token and admin ID")
        print("   2. Run: start_farm_mode.bat")
        print("   3. Send /start to your bot in Telegram")
        return 0
    else:
        print("⚠️  SETUP INCOMPLETE - See above for issues")
        print("\n📝 Next steps:")
        print("   1. Read TELEGRAM_SETUP.md for detailed instructions")
        print("   2. Create bot with @BotFather in Telegram")
        print("   3. Get your ID from @userinfobot")
        print("   4. Edit .env with your token and ID")
        print("   5. Run this script again to verify")
        return 1

if __name__ == "__main__":
    try:
        from dotenv import load_dotenv
    except ImportError:
        print("Installing python-dotenv...")
        import subprocess
        subprocess.run([sys.executable, "-m", "pip", "install", "python-dotenv", "-q"])
        from dotenv import load_dotenv

    sys.exit(main())
