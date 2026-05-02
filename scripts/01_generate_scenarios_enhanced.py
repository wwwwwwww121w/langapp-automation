import json
import os
import sys
import re
import time
import datetime
import logging
from pathlib import Path
from typing import List, Dict

sys.path.append(str(Path(__file__).parent.parent))
from config import (
    FIREWORKS_API_KEY, FIREWORKS_BASE_URL, FIREWORKS_MODEL_QUALITY,
    DATA_DIR, APP_NAME, APP_LINK, LOGS_DIR
)
from modules.scenario_validator import ScenarioValidator

from openai import OpenAI

client = OpenAI(api_key=FIREWORKS_API_KEY, base_url=FIREWORKS_BASE_URL)

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOGS_DIR, "scenario_gen.log")),
        logging.StreamHandler()
    ]
)


def make_prompt(type_name: str, count: int) -> str:
    """Create prompt for scenario generation"""
    return f"""Create {count} short TikTok video scripts for an Arabic+English language learning app called "{APP_NAME}".

Category: {type_name}

Return ONLY a valid JSON array with no extra text, no markdown, no thinking. Format:

[{{"id":1,"type":"{type_name}","hook_en":"English hook line","hook_ar":"Arabic hook","items":[{{"en":"English word","ar":"Arabic word","pronunciation":"romanized"}}],"cta_en":"Download {APP_NAME}!","cta_ar":"حمل {APP_NAME}!","hashtags":["#learnarabic","#arabic"]}}]

Rules:
- 3-5 items per script
- Include Arabic script AND romanized pronunciation
- Make hooks attention-grabbing (10-15 words)
- Each item should be clear and educational
- CTAs must mention the app
- Include relevant hashtags"""


def call_fireworks(prompt: str, max_tokens: int = 3000, retries: int = 3) -> str:
    """Call Fireworks API with retry logic"""
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=FIREWORKS_MODEL_QUALITY,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=min(max_tokens, 4096),
                temperature=0.7
            )
            text = response.choices[0].message.content or ""
            if not text.strip():
                raise ValueError("Empty response from API")
            return text
        except Exception as e:
            logger.warning(f"API call attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                wait_time = 10 * (attempt + 1)
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                raise


def extract_json(text: str) -> List[Dict]:
    """Extract and parse JSON from response text"""
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
                    if ch == "[":
                        depth += 1
                    elif ch == "]":
                        depth -= 1
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


def process_batch(type_name: str, type_label: str, batch_size: int = 3, retries: int = 3) -> List[Dict]:
    """Process a batch of scenarios with retry logic"""
    logger.info(f"Processing batch: {type_name}")

    for attempt in range(retries):
        try:
            prompt = make_prompt(type_label, batch_size)
            raw = call_fireworks(prompt, max_tokens=3000, retries=2)

            try:
                scenarios = extract_json(raw)
            except ValueError as e:
                logger.warning(f"JSON parse failed: {e}, retrying...")
                time.sleep(15)
                prompt_fallback = f"""List {batch_size} Arabic+English language facts for TikTok. Return JSON array: [{{"id":N,"type":"{type_name}","hook_en":"hook","hook_ar":"hook_ar","items":[{{"en":"en","ar":"ar","pronunciation":"pron"}}],"cta_en":"Try {APP_NAME}!","cta_ar":"جرب {APP_NAME}!","hashtags":["#learnarabic"]}}]. ONLY valid JSON."""
                raw = call_fireworks(prompt_fallback, max_tokens=2000, retries=1)
                scenarios = extract_json(raw)

            if isinstance(scenarios, str):
                scenarios = [{
                    "id": 0,
                    "type": type_name,
                    "hook_en": scenarios[:80],
                    "hook_ar": "",
                    "items": [],
                    "cta_en": f"Try {APP_NAME}!",
                    "cta_ar": f"جرب {APP_NAME}!",
                    "hashtags": ["#learnarabic"]
                }]

            if isinstance(scenarios, dict):
                scenarios = [scenarios]

            for j, s in enumerate(scenarios):
                if not isinstance(s, dict):
                    continue
                s["type"] = type_name
                if "id" not in s:
                    s["id"] = int(datetime.datetime.now().timestamp() * 1000) + j

            valid_scenarios, invalid = ScenarioValidator.validate_scenarios(scenarios)

            if invalid:
                logger.warning(f"Found {len(invalid)} invalid scenarios, attempting to fix...")
                for item in invalid:
                    fixed = ScenarioValidator.fix_scenario(item["scenario"])
                    is_valid, _ = ScenarioValidator.validate_scenario(fixed)
                    if is_valid:
                        valid_scenarios.append(fixed)
                    else:
                        logger.error(f"Could not fix scenario: {item['errors']}")

            logger.info(f"Batch {type_name}: Got {len(valid_scenarios)} valid scenarios")
            time.sleep(10)
            return valid_scenarios

        except Exception as e:
            logger.error(f"Batch {type_name} attempt {attempt + 1}/{retries} failed: {e}")
            if attempt < retries - 1:
                wait_time = 30 * (attempt + 1)
                logger.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                logger.error(f"Failed to process batch {type_name} after {retries} attempts")
                return []

    return []


def generate_scenarios():
    """Main scenario generation function"""
    os.makedirs(LOGS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

    logger.info("=" * 50)
    logger.info(f"Starting scenario generation - {datetime.datetime.now()}")
    logger.info("=" * 50)

    all_scenarios = []
    types = ["fact", "dialect", "mistake", "phrase"]
    type_labels = {
        "fact": "You didnt know this - Arabic origin of English words",
        "dialect": "Dialect vs Fusha - same phrase in MSA, Egyptian, Lebanese, Moroccan",
        "mistake": "Common mistake - errors Arabic speakers make in English or vice versa",
        "phrase": "Phrase of the day - useful everyday phrase in Arabic and English"
    }
    batch_size = 3

    for i, t in enumerate(types):
        try:
            scenarios = process_batch(t, type_labels[t], batch_size, retries=3)
            all_scenarios.extend(scenarios)
        except Exception as e:
            logger.error(f"Fatal error processing batch {t}: {e}", exc_info=True)

    if not all_scenarios:
        logger.error("No scenarios generated!")
        return None

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(DATA_DIR, f"scenarios_{timestamp}.json")
    latest_path = os.path.join(DATA_DIR, "scenarios_latest.json")

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_scenarios, f, ensure_ascii=False, indent=2)
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(all_scenarios, f, ensure_ascii=False, indent=2)

    logger.info("=" * 50)
    logger.info(f"TOTAL: {len(all_scenarios)} scenarios generated")
    logger.info(f"Saved to {output_path}")
    logger.info("=" * 50)
    print(f"\n✓ Generated {len(all_scenarios)} scenarios -> {output_path}\n")

    return all_scenarios


if __name__ == "__main__":
    generate_scenarios()
