import json
import os
import sys
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FIREWORKS_API_KEY, FIREWORKS_BASE_URL, FIREWORKS_MODEL_CHEAP, DATA_DIR, LOGS_DIR, APP_NAME

from openai import OpenAI
client = OpenAI(api_key=FIREWORKS_API_KEY, base_url=FIREWORKS_BASE_URL)

def collect_analytics_data():
    posted_path = os.path.join(DATA_DIR, "posted_videos.json")
    reddit_path = os.path.join(DATA_DIR, "reddit_answered.json")
    comments_path = os.path.join(DATA_DIR, "comments_replied.json")
    
    data = {
        "period": datetime.datetime.now().strftime("%Y-%m-%d"),
        "tiktok_posts": 0,
        "reddit_answers": 0,
        "comment_replies": 0,
        "tiktok_details": [],
        "reddit_details": [],
    }
    
    if os.path.exists(posted_path):
        with open(posted_path, "r", encoding="utf-8") as f:
            posted = json.load(f)
        data["tiktok_posts"] = len(posted.get("posted", []))
        data["tiktok_details"] = posted.get("posted", [])[-10:]
    
    if os.path.exists(reddit_path):
        with open(reddit_path, "r", encoding="utf-8") as f:
            reddit = json.load(f)
        data["reddit_answers"] = len(reddit.get("answered_ids", []))
    
    if os.path.exists(comments_path):
        with open(comments_path, "r", encoding="utf-8") as f:
            comments = json.load(f)
        data["comment_replies"] = len(comments.get("replied", []))
    
    manual_data_path = os.path.join(DATA_DIR, "manual_analytics.json")
    if os.path.exists(manual_data_path):
        with open(manual_data_path, "r", encoding="utf-8") as f:
            manual = json.load(f)
        data.update(manual)
    
    return data

def generate_report(data):
    prompt = f"""Analyze the following marketing data for the app "{APP_NAME}" and generate a weekly report with recommendations.

Data:
{json.dumps(data, ensure_ascii=False, indent=2)}

Generate a report in this format:

## Weekly Report - {data['period']}

### Summary
(2-3 sentences overview)

### Key Metrics
- TikTok videos posted: {data['tiktok_posts']}
- Reddit answers: {data['reddit_answers']}
- Comment replies: {data['comment_replies']}
{( "- Total views: " + str(data.get("total_views", "N/A")) if "total_views" in data else "")}
{( "- Total installs: " + str(data.get("total_installs", "N/A")) if "total_installs" in data else "")}

### What's Working
(2-3 points based on the data)

### What's Not Working  
(2-3 points)

### Recommendations
(5 specific, actionable recommendations for next week)

### Content Ideas for Next Week
(5 specific video/post ideas based on what's trending)

### Priority Actions
(3 things to focus on THIS week)
"""

    response = client.chat.completions.create(
        model=FIREWORKS_MODEL_CHEAP,
        messages=[
            {"role": "system", "content": "You are a growth marketing analyst specializing in mobile app marketing. Be specific and actionable."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=2000,
        temperature=0.6
    )
    
    return response.choices[0].message.content

def run_analytics():
    print("Collecting data...")
    data = collect_analytics_data()
    
    print(f"  TikTok posts: {data['tiktok_posts']}")
    print(f"  Reddit answers: {data['reddit_answers']}")
    print(f"  Comment replies: {data['comment_replies']}")
    
    print("\nGenerating AI report...")
    report = generate_report(data)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = os.path.join(DATA_DIR, f"report_{timestamp}.md")
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    latest_path = os.path.join(DATA_DIR, "report_latest.md")
    with open(latest_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    log_path = os.path.join(LOGS_DIR, "analytics.log")
    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.datetime.now()}] Report generated: {report_path}\n")
    
    print(f"\nReport saved → {report_path}")
    print("\n" + "="*60)
    print(report[:2000])

if __name__ == "__main__":
    run_analytics()
