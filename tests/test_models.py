import sys; sys.path.insert(0,'C:/langapp-automation')
from config import FIREWORKS_API_KEY, FIREWORKS_BASE_URL, APP_NAME
from openai import OpenAI
import json, time

client = OpenAI(api_key=FIREWORKS_API_KEY, base_url=FIREWORKS_BASE_URL)

models = [
    "accounts/fireworks/models/glm-5p1",
    "accounts/fireworks/models/minimax-m2p7",
]

prompt = f'Generate 3 TikTok ideas for "{APP_NAME}" (Arabic+English learning app with dialects). Type: fact - Arabic words in English. Output ONLY a JSON array (no thinking, no markdown): [{{"id":1,"type":"fact","hook_en":"hook","hook_ar":"arabic","items":[{{"en":"word","ar":"كلمة","pronunciation":"kalima"}}],"cta_en":"Try {APP_NAME}!","cta_ar":"جرب {APP_NAME}!","hashtags":["#learnarabic"]}}]. 3 items each. ONLY JSON.'

for model in models:
    print(f"\n--- {model} ---")
    t0 = time.time()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role":"user","content":prompt}],
            max_tokens=2000,
            temperature=0.7
        )
        dt = time.time() - t0
        raw = resp.choices[0].message.content or ""
        print(f"Time: {dt:.1f}s, Length: {len(raw)}")
        js = raw.find("[")
        je = raw.rfind("]") + 1
        if js != -1 and je > js:
            data = json.loads(raw[js:je])
            print(f"Parsed {len(data)} scenarios OK")
        else:
            print(f"No JSON array. Preview: {raw[:200]}")
    except Exception as e:
        dt = time.time() - t0
        print(f"Error after {dt:.1f}s: {e}")
