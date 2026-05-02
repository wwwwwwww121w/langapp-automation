#!/usr/bin/env python3
"""
Test script to verify Grok API integration
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("=" * 80)
print("🤖 GROK API INTEGRATION TEST")
print("=" * 80)
print()

# Step 1: Check if GROK_API_KEY exists
print("📝 STEP 1: Checking GROK_API_KEY...")
grok_key = os.getenv("GROK_API_KEY", "")
if grok_key and grok_key != "your_grok_api_key_here":
    print(f"✅ GROK_API_KEY found!")
    print(f"   Key: {grok_key[:20]}...{grok_key[-10:]}")
else:
    print("❌ GROK_API_KEY not set or invalid!")
    sys.exit(1)

print()

# Step 2: Check imports
print("📝 STEP 2: Checking Python dependencies...")
try:
    from openai import OpenAI
    print("✅ OpenAI library imported successfully")
except ImportError as e:
    print(f"❌ Failed to import OpenAI: {e}")
    print("   Run: pip install openai")
    sys.exit(1)

print()

# Step 3: Test Grok API connection
print("📝 STEP 3: Testing Grok API connection...")
try:
    client = OpenAI(
        api_key=grok_key,
        base_url="https://api.x.ai/v1"
    )
    print("✅ Grok client initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize Grok client: {e}")
    sys.exit(1)

print()

# Step 4: Make a test API call
print("📝 STEP 4: Making test API call to Grok...")
try:
    # Try different model names
    models_to_try = ["grok", "grok-2", "grok-vision"]
    response = None

    for model in models_to_try:
        try:
            print(f"   Trying model: {model}...")
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "user", "content": "Say 'Hello from Grok!' and nothing else"}
                ],
                max_tokens=50,
                temperature=0.7
            )
            print(f"   ✅ Model '{model}' works!")
            break
        except Exception as model_error:
            if model == models_to_try[-1]:
                raise Exception(f"No working models found. Tried: {models_to_try}")
            continue

    message = response.choices[0].message.content
    print("✅ API call successful!")
    print(f"   Response: {message}")

except Exception as e:
    print(f"❌ API call failed: {e}")
    sys.exit(1)

print()

# Step 5: Test scenario generation
print("📝 STEP 5: Testing scenario generation...")
try:
    prompt = """Create 1 TikTok video script for an Arabic+English language learning app.

Return ONLY a valid JSON array with no extra text:

[{"id":1,"type":"fact","hook_en":"Did you know?","hook_ar":"هل تعلم؟","items":[{"en":"word","ar":"كلمة","pronunciation":"kalima"}],"cta_en":"Learn more!","cta_ar":"تعلم المزيد!","hashtags":["#arabic"]}]
"""

    response = client.chat.completions.create(
        model="grok",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=500,
        temperature=0.7
    )

    result = response.choices[0].message.content
    print("✅ Scenario generation test successful!")
    print(f"   Response preview: {result[:100]}...")

except Exception as e:
    print(f"❌ Scenario generation failed: {e}")
    sys.exit(1)

print()
print("=" * 80)
print("🎉 ALL TESTS PASSED! Grok API is working correctly!")
print("=" * 80)
print()
print("Next steps:")
print("1. Run: python scripts/01_generate_scenarios_grok.py")
print("2. Check logs at: logs/scenario_gen_grok.log")
print("3. Start bot: start_bot_v2.bat")
print()
