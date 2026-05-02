import json
import os
import sys
import re
import time
import asyncio
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'core'))
from config import DATA_DIR, APP_NAME, APP_LINK, LOGS_DIR
from grok_browser_delegate import GrokBrowserDelegate


def make_prompt(type_name, count):
    return f"""Create {count} short TikTok video scripts for an Arabic+English language learning app called "{APP_NAME}".

Category: {type_name}

Return ONLY a valid JSON array with no extra text, no markdown, no thinking. Format:

[{{"id":1,"type":"{type_name}","hook_en":"English hook line","hook_ar":"Arabic hook","items":[{{"en":"English word","ar":"Arabic word","pronunciation":"romanized"}}],"cta_en":"Download {APP_NAME}!","cta_ar":"حمل {APP_NAME}!","hashtags":["#learnarabic","#arabic"]}}]

Rules: 3-5 items per script, include Arabic script AND romanized pronunciation, make hooks attention-grabbing."""


async def call_grok_browser(prompt, max_tokens=3000):
    """Call Grok API using browser delegate (no API key needed!)"""
    grok = GrokBrowserDelegate(headless=True)  # Hidden browser for production
    try:
        await grok.setup()
        logged_in = await grok.login_if_needed()

        if not logged_in:
            raise ValueError("Failed to login to Grok")

        # Send the prompt to Grok
        response = await grok.ask_question(prompt)

        if not response or not response.strip():
            raise ValueError("Empty response from Grok")

        return response
    except Exception as e:
        raise ValueError(f"Grok browser error: {str(e)}")
    finally:
        await grok.close()


def extract_json(text):
    """Extract JSON from text response"""
    text = text.replace("```json", "").replace("```", "").strip()
    for attempt in range(3):
        try:
            json_start = text.find("[")
            json_end = text.rfind("]") + 1
            if json_start != -1 and json_end > json_start:
                sub = text[json_start:json_end]
                depth = 0
                cut = len(sub)
                for ci, ch in enumerate(sub):
                    if ch == "[": depth += 1
                    elif ch == "]": depth -= 1
                    if depth == 0 and ci > 0:
                        cut = ci + 1
                        break
                sub = sub[:cut]
                result = json.loads(sub)
                if isinstance(result, list):
                    result = [r for r in result if isinstance(r, dict) and "hook_en" in r]
                    if result:
                        return result
            single_start = text.find("{")
            single_end = text.rfind("}") + 1
            if single_start != -1 and single_end > single_start:
                obj = json.loads(text[single_start:single_end])
                if isinstance(obj, dict) and "hook_en" in obj:
                    return [obj]
        except json.JSONDecodeError:
            if attempt == 0:
                text = re.sub(r'//.*?\n', '', text)
                text = re.sub(r'/\*.*?\*/', '', text, flags=re.DOTALL)
                text = re.sub(r',\s*([}\]])', r'\1', text)
                continue
            elif attempt == 1:
                text = re.sub(r'[\x00-\x1f]', '', text)
                text = text.replace("'", '"')
                try:
                    json_start = text.find("[")
                    json_end = text.rfind("]") + 1
                    if json_start != -1:
                        result = json.loads(text[json_start:json_end])
                        if isinstance(result, list):
                            result = [r for r in result if isinstance(r, dict) and "hook_en" in r]
                            if result:
                                return result
                except:
                    pass
    raise ValueError("Could not parse JSON from response")


async def generate_scenarios_async():
    """Generate scenarios using Grok browser delegate"""
    log_path = os.path.join(LOGS_DIR, "scenario_gen_grok.log")
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"\n[{datetime.datetime.now()}] Starting Grok scenario generation (4 batches) - BROWSER MODE\n")

    all_scenarios = []
    types = ["fact", "dialect", "mistake", "phrase"]
    type_labels = {
        "fact": "You didnt know this - Arabic origin of English words",
        "dialect": "Dialect vs Fusha - same phrase in MSA, Egyptian, Lebanese, Moroccan",
        "mistake": "Common mistake - errors Arabic speakers make in English or vice versa",
        "phrase": "Phrase of the day - useful everyday phrase in Arabic and English"
    }
    batch_size = 5  # Generate 5 scenarios per batch (total 20)

    for i, t in enumerate(types):
        print(f"  Batch {i+1}/4: {t}...")
        with open(log_path, "a", encoding="utf-8") as log:
            log.write(f"[{datetime.datetime.now()}] Batch {i+1}: {t}\n")
        try:
            prompt = make_prompt(type_labels[t], batch_size)
            print(f"    📝 Sending to Grok...")
            raw = await call_grok_browser(prompt, max_tokens=3000)

            try:
                scenarios = extract_json(raw)
            except ValueError:
                print(f"    ⚠️ JSON parse failed, retrying in 30s...")
                with open(log_path, "a", encoding="utf-8") as log:
                    log.write(f"[{datetime.datetime.now()}] JSON parse failed, retrying...\n")
                await asyncio.sleep(30)

                prompt = f"List {batch_size} Arabic+English language facts for TikTok. Return JSON array: [{{\"id\":N,\"type\":\"{t}\",\"hook_en\":\"hook\",\"hook_ar\":\"hook_ar\",\"items\":[{{\"en\":\"en\",\"ar\":\"ar\",\"pronunciation\":\"pron\"}}],\"cta_en\":\"Try {APP_NAME}!\",\"cta_ar\":\"جرب {APP_NAME}!\",\"hashtags\":[\"#learnarabic\"]}}]. ONLY valid JSON."
                raw = await call_grok_browser(prompt, max_tokens=2000)
                scenarios = extract_json(raw)

            await asyncio.sleep(20)

            if isinstance(scenarios, str):
                scenarios = [{"id": 0, "type": t, "hook_en": scenarios[:80], "hook_ar": "", "items": [], "cta_en": f"Try {APP_NAME}!", "cta_ar": "", "hashtags": ["#learnarabic"]}]
            if isinstance(scenarios, dict):
                scenarios = [scenarios]

            for j, s in enumerate(scenarios):
                if not isinstance(s, dict):
                    continue
                s["id"] = i * batch_size + j + 1
                s["type"] = t

            all_scenarios.extend(scenarios)
            print(f"    ✅ Got {len(scenarios)} scenarios")
            with open(log_path, "a", encoding="utf-8") as log:
                log.write(f"[{datetime.datetime.now()}] Batch {i+1} done: {len(scenarios)} scenarios\n")
        except Exception as e:
            print(f"    ❌ Error in batch {i+1}: {e}")
            with open(log_path, "a", encoding="utf-8") as log:
                log.write(f"[{datetime.datetime.now()}] Batch {i+1} ERROR: {e}\n")

    if not all_scenarios:
        print("❌ No scenarios generated!")
        return None

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(DATA_DIR, f"scenarios_{timestamp}.json")
    latest_path = os.path.join(DATA_DIR, "scenarios_latest.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_scenarios, f, ensure_ascii=False, indent=2)
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(all_scenarios, f, ensure_ascii=False, indent=2)

    with open(log_path, "a", encoding="utf-8") as log:
        log.write(f"[{datetime.datetime.now()}] TOTAL: {len(all_scenarios)} scenarios\n")
        log.write(f"[{datetime.datetime.now()}] Saved to {output_path}\n")

    print(f"\n✅ Generated {len(all_scenarios)} scenarios total -> {output_path}")
    return all_scenarios


def generate_scenarios():
    """Wrapper to run async code from sync context"""
    return asyncio.run(generate_scenarios_async())


if __name__ == "__main__":
    try:
        print("🚀 LinguaStart Scenario Generator (Grok Browser Mode)")
        print("=" * 60)
        generate_scenarios()
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
