#!/usr/bin/env python3
"""
Grok Browser-Based Delegate
Interact with Grok through your browser account (no API key needed)
Uses Playwright for browser automation
"""

import asyncio
import os
from pathlib import Path
from typing import Optional
from playwright.async_api import async_playwright, Browser, Page

class GrokBrowserDelegate:
    """Delegate tasks to Grok using your real account via browser"""

    def __init__(self, headless: bool = False):
        """
        Initialize Grok Browser Delegate

        Args:
            headless: If False, browser window will be visible (recommended)
        """
        self.headless = headless
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.user_data_dir = Path.home() / ".grok_browser"

    async def setup(self):
        """Setup browser and login"""
        print("🌐 Initializing browser...")

        playwright = await async_playwright().start()

        # Use your real browser profile (keeps you logged in)
        self.browser = await playwright.chromium.launch_persistent_context(
            user_data_dir=str(self.user_data_dir),
            headless=self.headless,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox"
            ]
        )

        self.page = self.browser.pages[0] if self.browser.pages else await self.browser.new_page()
        print("✅ Browser ready!")

    async def login_if_needed(self):
        """Check if logged in, if not - guide user to login"""
        print("🔐 Checking login status...")

        await self.page.goto("https://console.x.ai", wait_until="networkidle")

        # Check if we're already logged in
        try:
            await self.page.wait_for_selector('[data-testid="user-menu"]', timeout=3000)
            print("✅ Already logged in!")
            return True
        except:
            print("❌ Not logged in. Please log in in the browser window...")
            print("📋 Steps:")
            print("  1. Click 'Sign In' button")
            print("  2. Enter your credentials")
            print("  3. Complete login")
            print("  4. Press Enter when done...")

            input("Press Enter when you've logged in... ")

            # Verify login
            try:
                await self.page.wait_for_selector('[data-testid="user-menu"]', timeout=10000)
                print("✅ Login verified!")
                return True
            except:
                print("❌ Login failed")
                return False

    async def send_message(self, message: str, wait_for_response: bool = True) -> str:
        """
        Send a message through Grok chat interface

        Args:
            message: The message to send
            wait_for_response: Wait for response before returning

        Returns:
            Response from Grok
        """
        print(f"📝 Sending: {message[:50]}...")

        # Click on message input field
        input_selector = '[data-testid="message-input"]'
        try:
            await self.page.click(input_selector)
        except:
            # Try alternate selector
            input_selector = 'textarea'
            await self.page.click(input_selector)

        # Type message
        await self.page.fill(input_selector, message)

        # Send (Ctrl+Enter or Click send button)
        await self.page.keyboard.press("Control+Enter")

        if not wait_for_response:
            return "Message sent"

        # Wait for response
        print("⏳ Waiting for response...")
        await asyncio.sleep(2)  # Brief wait for response to appear

        # Get response text
        try:
            response_selector = '[data-testid="response-text"]'
            response = await self.page.text_content(response_selector)
            return response or "No response captured"
        except:
            return "Response sent (could not capture)"

    async def write_documentation(self, topic: str, requirements: str) -> str:
        """Delegate documentation writing"""
        prompt = f"""You are a documentation expert. Write clear documentation.

TOPIC: {topic}

REQUIREMENTS:
{requirements}

Write comprehensive documentation that is:
- Clear and easy to follow
- Well-structured with sections
- Includes examples where relevant
- Uses markdown formatting
- Professional but friendly tone"""

        return await self.send_message(prompt)

    async def write_design_brief(self, component: str, requirements: str) -> str:
        """Delegate design brief"""
        prompt = f"""You are a UI/UX designer. Create a design brief.

COMPONENT: {component}

REQUIREMENTS:
{requirements}

Provide:
- Component description
- Visual elements
- Layout suggestions
- Color scheme
- Typography
- Interactive states"""

        return await self.send_message(prompt)

    async def ask_question(self, question: str) -> str:
        """Ask Grok any question"""
        return await self.send_message(question)

    async def close(self):
        """Close browser"""
        if self.browser:
            await self.browser.close()
            print("🌐 Browser closed")


async def main():
    """Example usage"""

    # Create delegate
    grok = GrokBrowserDelegate(headless=False)  # headless=False shows the browser

    try:
        # Setup
        await grok.setup()

        # Login if needed
        logged_in = await grok.login_if_needed()
        if not logged_in:
            return

        # Example: Ask a question
        print("\n" + "="*80)
        print("🤖 SENDING TEST MESSAGE")
        print("="*80)

        response = await grok.ask_question("Say 'Hello from Grok!' in exactly 3 words")
        print(f"\n📤 Response:\n{response}")

        # Keep browser open to show the interaction
        print("\n✅ Browser will stay open. You can continue using it!")
        print("Press Ctrl+C to close...")

        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        print("\n\nClosing...")

    finally:
        await grok.close()


if __name__ == "__main__":
    print("="*80)
    print("🤖 GROK BROWSER-BASED DELEGATE")
    print("="*80)
    print()
    print("This tool uses your real browser to interact with Grok")
    print("No API key needed - uses your actual account!")
    print()
    print("Requirements:")
    print("  pip install playwright")
    print("  playwright install chromium")
    print()

    # Check if playwright is installed
    try:
        import playwright
        print("✅ Playwright is installed")
    except ImportError:
        print("❌ Playwright not installed")
        print("Run: pip install playwright")
        print("Then: playwright install chromium")
        exit(1)

    print()
    print("Starting in 3 seconds...")
    print()

    asyncio.run(main())
