import json
import os
import sys
import time
import glob
import random

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    DATA_DIR, OUTPUT_DIR, LOGS_DIR,
    TIKTOK_USERNAME, TIKTOK_PASSWORD,
    CHROME_DRIVER_PATH, POST_SCHEDULE_HOUR
)

HASHTAGS_ROTATE = [
    "#learnarabic #learnenglish #bilingual #عربي #languagelearning #arabiclanguage #englishlearning",
    "#arabicwords #englishwords #studyarabic #لغة_عربية #polyglot #languages",
    "#arabicdialects #msa #egyptianarabic #lebanesearabic #moroccanarabic #learnlanguages",
    "#arabicenglish #vocabulary #flashcards #languageapp #تعلم_الإنجليزية #تعلم_العربية",
    "#arabicforkids #englishforarabs #dualanguage #languageexchange #arabicculture"
]

SESSION_FILE = os.path.join(DATA_DIR, ".tiktok_session")
POSTED_LOG = os.path.join(DATA_DIR, "posted_videos.json")

def get_driver():
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("Selenium not installed. Run: pip install selenium")
        return None
    
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"--user-data-dir={os.path.join(DATA_DIR, 'chrome_profile')}")
    
    try:
        driver = webdriver.Chrome(options=options)
    except:
        try:
            from selenium.webdriver.chrome.service import Service
            service = Service(CHROME_DRIVER_PATH)
            driver = webdriver.Chrome(service=service, options=options)
        except Exception as e:
            print(f"Cannot start Chrome: {e}")
            print("Install ChromeDriver: https://chromedriver.chromium.org/")
            return None
    return driver

def login_tiktok(driver):
    driver.get("https://www.tiktok.com/login")
    print("Please log in manually in the browser window (first time only).")
    print("After logging in, press Enter here to continue...")
    input()
    print("Session saved for future auto-login.")

def load_posted_log():
    if os.path.exists(POSTED_LOG):
        with open(POSTED_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"posted": [], "last_index": 0}

def save_posted_log(log_data):
    with open(POSTED_LOG, "w", encoding="utf-8") as f:
        json.dump(log_data, f, ensure_ascii=False, indent=2)

def post_video(driver, video_path, caption):
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    try:
        driver.get("https://www.tiktok.com/creator")
        time.sleep(5)
        
        upload_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
        if not upload_inputs:
            print("  Upload button not found. Need to re-login.")
            login_tiktok(driver)
            driver.get("https://www.tiktok.com/creator")
            time.sleep(5)
            upload_inputs = driver.find_elements(By.CSS_SELECTOR, 'input[type="file"]')
        
        upload_inputs[0].send_keys(os.path.abspath(video_path))
        print("  Video uploaded, waiting for processing...")
        time.sleep(15)
        
        caption_inputs = driver.find_elements(
            By.CSS_SELECTOR, '[data-testid="caption-input"], .caption-input, [contenteditable="true"]')
        if caption_inputs:
            caption_inputs[0].clear()
            caption_inputs[0].send_keys(caption)
        else:
            print("  Caption input not found, trying tab + type...")
            from selenium.webdriver.common.keys import Keys
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.TAB, Keys.TAB)
            time.sleep(1)
            driver.switch_to.active_element.send_keys(caption)
        
        time.sleep(3)
        
        post_buttons = driver.find_elements(
            By.XPATH, '//button[contains(text(),"Post") or contains(text(),"Publish")]')
        if post_buttons:
            post_buttons[0].click()
            print("  Post submitted!")
            time.sleep(10)
            return True
        else:
            print("  Post button not found.")
            driver.save_screenshot(os.path.join(LOGS_DIR, "tiktok_post_fail.png"))
            return False
            
    except Exception as e:
        print(f"  Error posting: {e}")
        driver.save_screenshot(os.path.join(LOGS_DIR, "tiktok_error.png"))
        return False

def auto_post_all():
    captions_path = os.path.join(DATA_DIR, "captions.json")
    if not os.path.exists(captions_path):
        print("No captions found. Run 03_assemble_videos.py first.")
        return
    
    with open(captions_path, "r", encoding="utf-8") as f:
        captions = json.load(f)
    
    posted = load_posted_log()
    next_idx = posted["last_index"]
    
    if next_idx >= len(captions):
        print("All videos already posted!")
        return
    
    entry = captions[next_idx]
    video_path = entry["video"]
    
    if not os.path.exists(video_path):
        print(f"Video not found: {video_path}")
        return
    
    hashtags = random.choice(HASHTAGS_ROTATE)
    full_caption = f"{entry['caption']} {hashtags}"
    
    if len(full_caption) > 2200:
        full_caption = full_caption[:2197] + "..."
    
    driver = get_driver()
    if not driver:
        return
    
    try:
        print(f"Posting video {next_idx + 1}/{len(captions)}: {entry['caption'][:50]}...")
        
        success = post_video(driver, video_path, full_caption)
        
        if success:
            posted["posted"].append({
                "id": entry["id"],
                "caption": full_caption,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "video": video_path
            })
            posted["last_index"] = next_idx + 1
            save_posted_log(posted)
            print(f"  Posted! Next video index: {posted['last_index']}")
        else:
            print("  Failed to post. Will retry next run.")
    
    finally:
        driver.quit()

def schedule_daily():
    import schedule
    schedule.every().day.at(f"{POST_SCHEDULE_HOUR:02d}:00").do(auto_post_all)
    print(f"Scheduled daily post at {POST_SCHEDULE_HOUR}:00. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        schedule_daily()
    elif len(sys.argv) > 1 and sys.argv[1] == "--login":
        driver = get_driver()
        if driver:
            login_tiktok(driver)
            driver.quit()
    else:
        auto_post_all()
