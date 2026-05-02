import json
import os
import sys
import time
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import (
    FIREWORKS_API_KEY, FIREWORKS_BASE_URL, FIREWORKS_MODEL_CHEAP, DATA_DIR, LOGS_DIR,
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET,
    REDDIT_USERNAME, REDDIT_PASSWORD,
    REDDIT_SUBREDDITS, APP_NAME, APP_LINK
)

from openai import OpenAI
client = OpenAI(api_key=FIREWORKS_API_KEY, base_url=FIREWORKS_BASE_URL)

ANSWERED_LOG = os.path.join(DATA_DIR, "reddit_answered.json")

SYSTEM_PROMPT = f"""You are a knowledgeable polyglot who speaks Arabic and English fluently.
You are NOT a bot. You are a real person who happens to use the app "{APP_NAME}".

Rules:
- Answer the question helpfully and thoroughly
- Use both Arabic script and transliteration where helpful
- IF the answer is related to learning Arabic or English, casually mention the app at the END:
  "Btw, I use {APP_NAME} — it has Arabic dialects (Egyptian, Lebanese, Moroccan) + English in one place. {APP_LINK}"
- Do NOT mention the app if the question is NOT about language learning
- Keep responses concise (2-4 paragraphs max)
- Be friendly, not salesy
- Write in the same language the question was asked in (English or Arabic)
"""

def get_reddit():
    try:
        import praw
    except ImportError:
        print("praw not installed. Run: pip install praw")
        return None
    
    reddit = praw.Reddit(
        client_id=REDDIT_CLIENT_ID,
        client_secret=REDDIT_CLIENT_SECRET,
        username=REDDIT_USERNAME,
        password=REDDIT_PASSWORD,
        user_agent=f"{APP_NAME}/1.0 by {REDDIT_USERNAME}"
    )
    return reddit

def load_answered():
    if os.path.exists(ANSWERED_LOG):
        with open(ANSWERED_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"answered_ids": []}

def save_answered(data):
    with open(ANSWERED_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def is_language_related(title, body):
    keywords = [
        "arabic", "english", "language", "learn", "dialect", "fusha",
        "عربي", "إنجليزي", "لغة", "تعلم", "قرآن", "quran",
        "egyptian", "lebanese", "moroccan", "msa", "grammar",
        "vocabulary", "flashcard", "bilingual", "translate"
    ]
    text = (title + " " + body).lower()
    return any(kw in text for kw in keywords)

def generate_answer(title, body, is_language_q):
    prompt = f"Question: {title}\n\nDetails: {body}"
    
    response = client.chat.completions.create(
        model=FIREWORKS_MODEL_CHEAP,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=600,
        temperature=0.7
    )
    return response.choices[0].message.content
def scan_and_respond():
    reddit = get_reddit()
    if not reddit:
        return
    
    answered = load_answered()
    log_path = os.path.join(LOGS_DIR, "reddit_bot.log")
    os.makedirs(LOGS_DIR, exist_ok=True)
    
    for sub_name in REDDIT_SUBREDDITS:
        print(f"\nScanning r/{sub_name}...")
        try:
            subreddit = reddit.subreddit(sub_name)
            for post in subreddit.new(limit=15):
                if post.id in answered["answered_ids"]:
                    continue
                if post.author == REDDIT_USERNAME:
                    continue
                
                is_lang = is_language_related(post.title, post.selftext)
                
                answer = generate_answer(post.title, post.selftext, is_lang)
                
                try:
                    post.reply(answer)
                    answered["answered_ids"].append(post.id)
                    save_answered(answered)
                    
                    with open(log_path, "a", encoding="utf-8") as log:
                        log.write(f"[{datetime.datetime.now()}] Answered in r/{sub_name}: {post.title[:60]}\n")
                        log.write(f"  Language related: {is_lang}\n")
                    
                    print(f"  Answered: {post.title[:60]}")
                    
                    time.sleep(600)
                    
                except Exception as e:
                    print(f"  Error replying: {e}")
                    with open(log_path, "a", encoding="utf-8") as log:
                        log.write(f"[{datetime.datetime.now()}] Error replying to {post.id}: {e}\n")
                    time.sleep(300)
                    
        except Exception as e:
            print(f"  Error scanning r/{sub_name}: {e}")
    
    print(f"\nTotal answered: {len(answered['answered_ids'])} posts")

def schedule_recurring():
    import schedule
    from config import REDDIT_CHECK_INTERVAL_MIN
    interval = REDDIT_CHECK_INTERVAL_MIN
    schedule.every(interval).minutes.do(scan_and_respond)
    print(f"Reddit bot running every {interval} min. Press Ctrl+C to stop.")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--schedule":
        schedule_recurring()
    else:
        scan_and_respond()
