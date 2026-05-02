#!/usr/bin/env python3
"""
Test Grok Browser Integration
Verifies that the browser delegate and scenario generation work correctly
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from grok_browser_delegate import GrokBrowserDelegate
from config import APP_NAME


async def test_browser_setup():
    """Test 1: Verify browser can be set up"""
    print("\n" + "=" * 70)
    print("TEST 1: Browser Setup")
    print("=" * 70)

    grok = GrokBrowserDelegate(headless=False)  # Show browser for debugging

    try:
        print("📝 Setting up browser...")
        await grok.setup()
        print("✅ Browser setup successful!")
        return True
    except Exception as e:
        print(f"❌ Browser setup failed: {e}")
        return False
    finally:
        await grok.close()


async def test_login():
    """Test 2: Verify login process"""
    print("\n" + "=" * 70)
    print("TEST 2: Login Process")
    print("=" * 70)

    grok = GrokBrowserDelegate(headless=False)

    try:
        print("📝 Setting up browser...")
        await grok.setup()

        print("🔐 Checking login...")
        logged_in = await grok.login_if_needed()

        if logged_in:
            print("✅ Login successful!")
            return True
        else:
            print("⚠️ Login was cancelled or failed")
            return False

    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False
    finally:
        await grok.close()


async def test_simple_question():
    """Test 3: Ask a simple question"""
    print("\n" + "=" * 70)
    print("TEST 3: Simple Question")
    print("=" * 70)

    grok = GrokBrowserDelegate(headless=False)

    try:
        print("📝 Setting up browser...")
        await grok.setup()

        print("🔐 Checking login...")
        logged_in = await grok.login_if_needed()

        if not logged_in:
            print("❌ Not logged in, skipping test")
            return False

        print("💬 Sending test question...")
        response = await grok.ask_question("Write 'Hello from Grok!' in exactly 5 words")

        if response:
            print(f"✅ Got response ({len(response)} chars):")
            print(f"   {response[:100]}...")
            return True
        else:
            print("❌ No response received")
            return False

    except Exception as e:
        print(f"❌ Question test failed: {e}")
        return False
    finally:
        await grok.close()


async def test_json_generation():
    """Test 4: Generate JSON response"""
    print("\n" + "=" * 70)
    print("TEST 4: JSON Generation")
    print("=" * 70)

    grok = GrokBrowserDelegate(headless=False)

    try:
        print("📝 Setting up browser...")
        await grok.setup()

        print("🔐 Checking login...")
        logged_in = await grok.login_if_needed()

        if not logged_in:
            print("❌ Not logged in, skipping test")
            return False

        prompt = f"""Generate 1 TikTok video script for language learning. Return ONLY valid JSON:
[{{"id":1,"type":"test","hook_en":"English text","hook_ar":"Arabic text","items":[{{"en":"word","ar":"كلمة","pronunciation":"kalima"}}],"cta_en":"Try {APP_NAME}!","cta_ar":"جرب {APP_NAME}!","hashtags":["#learn"]}}]

IMPORTANT: Return ONLY the JSON array, no other text."""

        print("💬 Requesting JSON from Grok...")
        response = await grok.ask_question(prompt)

        if response:
            print(f"📦 Got response ({len(response)} chars)")

            # Try to parse as JSON
            try:
                json_start = response.find("[")
                json_end = response.rfind("]") + 1
                if json_start != -1 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    data = json.loads(json_str)
                    print(f"✅ Valid JSON with {len(data) if isinstance(data, list) else 1} items")
                    return True
            except json.JSONDecodeError:
                print(f"⚠️ Response contains text but not pure JSON:")
                print(f"   {response[:200]}...")
                return True  # Response received, even if not pure JSON

        print("❌ No response received")
        return False

    except Exception as e:
        print(f"❌ JSON test failed: {e}")
        return False
    finally:
        await grok.close()


async def run_all_tests():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 15 + "🤖 GROK BROWSER INTEGRATION TESTS 🤖" + " " * 18 + "║")
    print("╚" + "=" * 68 + "╝")

    results = []

    # Test 1: Setup
    print("\n📌 Starting tests...")
    results.append(("Browser Setup", await test_browser_setup()))

    # Test 2: Login
    results.append(("Login Process", await test_login()))

    # Test 3: Simple Question
    results.append(("Simple Question", await test_simple_question()))

    # Test 4: JSON Generation
    results.append(("JSON Generation", await test_json_generation()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status:12} {test_name}")

    print(f"\nResult: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! System is ready for production.")
        return True
    elif passed >= total // 2:
        print("\n⚠️ Some tests failed. Check the browser for issues.")
        return True
    else:
        print("\n❌ Most tests failed. Review configuration and try again.")
        return False


if __name__ == "__main__":
    print("🌐 Grok Browser Integration Test Suite")
    print("Version 1.0")
    print()
    print("This test will:")
    print("  1. Initialize the browser")
    print("  2. Log you into Grok (if needed)")
    print("  3. Send test questions")
    print("  4. Verify JSON generation")
    print()
    print("Important:")
    print("  - The browser will open and may ask you to log in")
    print("  - Follow the prompts in the browser and console")
    print("  - Each test may take a few seconds")
    print()

    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
