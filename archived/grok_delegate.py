#!/usr/bin/env python3
"""
Grok Task Delegation Tool
Allows Claude to delegate tasks to Grok AI
"""

import os
from dotenv import load_dotenv
from openai import OpenAI
from typing import Optional

load_dotenv()

class GrokDelegate:
    """Delegate tasks to Grok"""

    def __init__(self):
        self.api_key = os.getenv("GROK_API_KEY")
        self.base_url = os.getenv("GROK_BASE_URL", "https://api.x.ai/v1")
        self.model = os.getenv("GROK_MODEL", "grok")

        if not self.api_key or self.api_key == "your_grok_api_key_here":
            raise ValueError("GROK_API_KEY not set in .env")

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def write_documentation(self, topic: str, requirements: str) -> str:
        """Delegate documentation writing to Grok"""
        prompt = f"""You are a documentation expert. Write clear, well-structured documentation.

TOPIC: {topic}

REQUIREMENTS:
{requirements}

Write comprehensive documentation that is:
- Clear and easy to follow
- Well-structured with sections
- Includes examples where relevant
- Uses markdown formatting
- Professional but friendly tone"""

        return self._call_grok(prompt)

    def write_design_brief(self, component: str, requirements: str) -> str:
        """Delegate design brief to Grok"""
        prompt = f"""You are a UI/UX designer. Create a design brief for a component.

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

        return self._call_grok(prompt)

    def generate_utility_code(self, description: str, specifications: str) -> str:
        """Delegate utility code generation to Grok"""
        prompt = f"""You are a Python developer. Write a utility function.

DESCRIPTION: {description}

SPECIFICATIONS:
{specifications}

Requirements:
- Clean, readable code
- Proper error handling
- Type hints
- Docstring
- No external dependencies (unless specified)
- Python 3.8+ compatible"""

        return self._call_grok(prompt)

    def create_examples(self, topic: str, count: int = 3) -> str:
        """Delegate example creation to Grok"""
        prompt = f"""Create {count} clear, practical examples for:

TOPIC: {topic}

Requirements:
- Each example should be self-contained
- Include explanation
- Show common use cases
- Highlight best practices
- Include code where relevant"""

        return self._call_grok(prompt)

    def write_troubleshooting(self, problem_area: str, common_issues: str) -> str:
        """Delegate troubleshooting guide to Grok"""
        prompt = f"""You are a technical support expert. Create a troubleshooting guide.

AREA: {problem_area}

COMMON ISSUES:
{common_issues}

For each issue, provide:
- Clear description
- Symptoms to look for
- Step-by-step solution
- Prevention tips
- When to get help

Format as FAQ with markdown."""

        return self._call_grok(prompt)

    def _call_grok(self, prompt: str, max_tokens: int = 2000) -> str:
        """Make API call to Grok"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error calling Grok: {e}"

    def delegate(self, task_type: str, **kwargs) -> str:
        """Generic task delegation"""

        tasks = {
            "documentation": self.write_documentation,
            "design": self.write_design_brief,
            "utility": self.generate_utility_code,
            "examples": self.create_examples,
            "troubleshooting": self.write_troubleshooting,
        }

        if task_type not in tasks:
            return f"Unknown task type: {task_type}. Available: {', '.join(tasks.keys())}"

        handler = tasks[task_type]
        return handler(**kwargs)


# Example usage
if __name__ == "__main__":
    try:
        grok = GrokDelegate()
        print("✅ Grok Delegate initialized successfully!")
        print()
        print("Available delegation methods:")
        print("  • write_documentation(topic, requirements)")
        print("  • write_design_brief(component, requirements)")
        print("  • generate_utility_code(description, specifications)")
        print("  • create_examples(topic, count)")
        print("  • write_troubleshooting(problem_area, common_issues)")
        print()

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure GROK_API_KEY is set in .env")
