#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

print("🤖 GROK API TEST\n" + "="*50)

# Check API Key
api_key = os.getenv("GROK_API_KEY", "")
print(f"\n1️⃣  API Key: {api_key[:20]}...{api_key[-10:]}")

# Initialize client
print("2️⃣  Initializing Grok client...")
client = OpenAI(
    api_key=api_key,
    base_url="https://api.x.ai/v1"
)
print("   ✅ Client ready!")

# Test API call
print("3️⃣  Testing API call...")
try:
    response = client.chat.completions.create(
        model="grok",
        messages=[{"role": "user", "content": "Say hello!"}],
        max_tokens=50
    )
    print("   ✅ API call successful!")
    print(f"   Response: {response.choices[0].message.content}\n")
except Exception as e:
    print(f"   ❌ Error: {e}\n")
    exit(1)

print("="*50)
print("✅ ALL TESTS PASSED!")
print("Grok API is working correctly 🎉\n")
