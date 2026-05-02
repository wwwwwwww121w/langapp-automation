import json
import os
import sys
import time
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FIREWORKS_API_KEY, FIREWORKS_BASE_URL, FIREWORKS_MODEL_CHEAP, DATA_DIR, LOGS_DIR, APP_NAME, APP_LINK

from openai import OpenAI
client = OpenAI(api_key=FIREWORKS_API_KEY, base_url=FIREWORKS_BASE_URL)

REPLIED_LOG = os.path.join(DATA_DIR, "comments_replied.json")

COMMENT_SYSTEM_PROMPT = f"""You are a friendly community manager for the language learning app "{APP_NAME}".
You respond to comments on social media posts about the app.

Rules:
- Be warm, friendly, and helpful
- Answer in the SAME LANGUAGE as the comment (Arabic, English, or Russian)
- Keep it SHORT (1-2 sentences)
- If someone asks a question, answer it briefly
- If someone compliments, say thanks + mention a feature they might like
- If someone criticizes, acknowledge + say you'll pass it to the team
- NEVER be defensive or aggressive
- If relevant, mention that the app has: Arabic dialects, English lessons, flashcards, quizzes
"""

def generate_reply(comment_text, post_context=""):
    response = client.chat.completions.create(
        model=FIREWORKS_MODEL_CHEAP,
        messages=[
            {"role": "system", "content": COMMENT_SYSTEM_PROMPT},
            {"role": "user", "content": f"Post: {post_context}\nComment: {comment_text}"}
        ],
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

def load_replied():
    if os.path.exists(REPLIED_LOG):
        with open(REPLIED_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"replied": []}

def save_replied(data):
    with open(REPLIED_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def process_comments_from_file():
    comments_file = os.path.join(DATA_DIR, "new_comments.json")
    
    if not os.path.exists(comments_file):
        print("No new_comments.json found. Create it with this format:")
        print('[{"id": "1", "text": "Great app!", "post": "5 Arabic words"}, ...]')
        return
    
    with open(comments_file, "r", encoding="utf-8") as f:
        comments = json.load(f)
    
    replied = load_replied()
    log_path = os.path.join(LOGS_DIR, "comments.log")
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    replies = []
    
    for comment in comments:
        if comment["id"] in [r["id"] for r in replied["replied"]]:
            continue
        
        reply = generate_reply(comment["text"], comment.get("post", ""))
        replies.append({"id": comment["id"], "reply": reply})
        
        replied["replied"].append({
            "id": comment["id"],
            "original": comment["text"],
            "reply": reply,
            "timestamp": datetime.datetime.now().isoformat()
        })
        
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(f"[{datetime.datetime.now()}] Comment: {comment['text'][:50]}\n")
            log.write(f"  Reply: {reply[:50]}\n")
        
        print(f"Comment: {comment['text'][:60]}")
        print(f"Reply:   {reply[:60]}\n")
    
    save_replied(replied)
    
    replies_file = os.path.join(DATA_DIR, "generated_replies.json")
    with open(replies_file, "w", encoding="utf-8") as f:
        json.dump(replies, f, ensure_ascii=False, indent=2)
    
    print(f"Generated {len(replies)} replies → {replies_file}")
    print("Post these replies manually or integrate with platform APIs.")

def auto_reply_tiktok():
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.chrome.options import Options
    except ImportError:
        print("Selenium not installed. Run: pip install selenium")
        return
    
    options = Options()
    options.add_argument(f"--user-data-dir={os.path.join(DATA_DIR, 'chrome_profile')}")
    driver = webdriver.Chrome(options=options)
    
    try:
        driver.get("https://www.tiktok.com/creator")
        time.sleep(5)
        
        print("Navigate to your video comments page, then press Enter...")
        input()
        
        comments = driver.find_elements(By.CSS_SELECTOR, '[data-testid="comment-text"], .comment-text')
        
        for comment_el in comments:
            text = comment_el.text
            if not text:
                continue
            
            reply = generate_reply(text)
            print(f"\nComment: {text[:60]}")
            print(f"Suggested reply: {reply}")
            
            confirm = input("Post this reply? (y/n/s=skip): ").lower()
            if confirm == "y":
                try:
                    reply_btn = comment_el.find_element(By.XPATH, '..//button[contains(text(),"Reply")]')
                    reply_btn.click()
                    time.sleep(1)
                    
                    reply_input = driver.find_element(By.CSS_SELECTOR, '[contenteditable="true"]')
                    reply_input.send_keys(reply)
                    time.sleep(1)
                    
                    post_btn = driver.find_element(By.XPATH, '//button[contains(text(),"Post")]')
                    post_btn.click()
                    print("  Posted!")
                except Exception as e:
                    print(f"  Error: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--tiktok":
        auto_reply_tiktok()
    else:
        process_comments_from_file()
