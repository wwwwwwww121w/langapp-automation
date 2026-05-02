import json
import os
import sys
import time
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import FIREWORKS_API_KEY, FIREWORKS_BASE_URL, FIREWORKS_MODEL_CHEAP, DATA_DIR, LOGS_DIR, APP_NAME, APP_LINK

from openai import OpenAI
client = OpenAI(api_key=FIREWORKS_API_KEY, base_url=FIREWORKS_BASE_URL)

QUORA_SYSTEM_PROMPT = f"""You are a bilingual language expert (Arabic + English) who answers questions on Quora.
Be helpful, detailed, and authoritative. Include both Arabic script and romanized pronunciation.

IF the question is about learning Arabic or English, add at the END:
"P.S. If you want a structured way to learn both Arabic (including dialects) and English, check out {APP_NAME} — {APP_LINK}"

IF the question is NOT about language learning, just answer normally without mentioning the app.
"""

ANSWERED_LOG = os.path.join(DATA_DIR, "quora_answered.json")

def load_answered():
    if os.path.exists(ANSWERED_LOG):
        with open(ANSWERED_LOG, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"answered_ids": []}

def save_answered(data):
    with open(ANSWERED_LOG, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def is_language_related(title, detail):
    keywords = [
        "arabic", "english", "learn", "language", "dialect", "quran",
        "عربي", "لغة", "تعلم", "fusha", "msa", "egyptian arabic",
        "lebanese", "moroccan", "grammar", "vocabulary", "bilingual",
        "translate", "pronunciation", "flashcard"
    ]
    text = (title + " " + (detail or "")).lower()
    return any(kw in text for kw in keywords)

def generate_answer(title, detail, is_lang_q):
    context = f"Question: {title}"
    if detail:
        context += f"\n\nDetails: {detail}"
    
    response = client.chat.completions.create(
        model=FIREWORKS_MODEL_CHEAP,
        messages=[
            {"role": "system", "content": QUORA_SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ],
        max_tokens=800,
        temperature=0.7
    )
    return response.choices[0].message.content

def generate_answers_from_file():
    questions_file = os.path.join(DATA_DIR, "quora_questions.json")
    
    if not os.path.exists(questions_file):
        sample = [
            {"id": "1", "title": "What is the best way to learn Arabic?", "detail": "I want to learn Arabic but I'm confused by all the dialects."},
            {"id": "2", "title": "How similar are Arabic dialects?", "detail": "Can a Moroccan understand an Egyptian?"},
            {"id": "3", "title": "What English words come from Arabic?", "detail": ""}
        ]
        with open(questions_file, "w", encoding="utf-8") as f:
            json.dump(sample, f, ensure_ascii=False, indent=2)
        print(f"Created sample file: {questions_file}")
        print("Edit it with real Quora questions, then run again.")
    
    with open(questions_file, "r", encoding="utf-8") as f:
        questions = json.load(f)
    
    answered = load_answered()
    answers = []
    
    for q in questions:
        if q["id"] in answered["answered_ids"]:
            continue
        
        is_lang = is_language_related(q["title"], q.get("detail", ""))
        answer = generate_answer(q["title"], q.get("detail", ""), is_lang)
        
        answers.append({
            "id": q["id"],
            "question": q["title"],
            "answer": answer,
            "language_related": is_lang
        })
        
        answered["answered_ids"].append(q["id"])
        
        print(f"\nQ: {q['title'][:60]}")
        print(f"A: {answer[:100]}...")
    
    save_answered(answered)
    
    output_path = os.path.join(DATA_DIR, "quora_answers.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(answers, f, ensure_ascii=False, indent=2)
    
    print(f"\nGenerated {len(answers)} answers → {output_path}")

if __name__ == "__main__":
    generate_answers_from_file()
