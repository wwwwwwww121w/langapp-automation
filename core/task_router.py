#!/usr/bin/env python3
"""
Task Router - Intelligent task delegation system
Routes tasks between Claude (main architect) and Grok (assistant)
"""

from enum import Enum
from dataclasses import dataclass
from typing import Literal

class TaskComplexity(Enum):
    """Task complexity levels"""
    SIMPLE = "simple"          # For Grok: design, utilities, simple code
    MEDIUM = "medium"          # Mixed approach
    COMPLEX = "complex"        # For Claude: architecture, core logic

class TaskCategory(Enum):
    """Task categories"""
    DESIGN = "design"                      # UI/UX design → GROK
    DOCUMENTATION = "documentation"        # README, guides → GROK
    SIMPLE_CODE = "simple_code"           # Utilities, helpers → GROK
    CONFIG = "configuration"               # Config files → GROK
    ARCHITECTURE = "architecture"          # System design → CLAUDE
    CORE_LOGIC = "core_logic"             # Business logic → CLAUDE
    INTEGRATION = "integration"            # API integration → CLAUDE
    TESTING = "testing"                    # Critical tests → CLAUDE
    OPTIMIZATION = "optimization"          # Performance tuning → CLAUDE
    SECURITY = "security"                  # Security features → CLAUDE

@dataclass
class Task:
    """Task definition"""
    title: str
    description: str
    category: TaskCategory
    complexity: TaskComplexity
    priority: Literal["low", "medium", "high", "critical"]

    @property
    def assigned_to(self) -> str:
        """Determine who should do this task"""

        # CRITICAL → Always Claude
        if self.priority == "critical":
            return "CLAUDE"

        # Core tasks → Claude
        core_categories = {
            TaskCategory.ARCHITECTURE,
            TaskCategory.CORE_LOGIC,
            TaskCategory.INTEGRATION,
            TaskCategory.SECURITY
        }
        if self.category in core_categories:
            return "CLAUDE"

        # Simple tasks → Grok
        simple_categories = {
            TaskCategory.DESIGN,
            TaskCategory.DOCUMENTATION,
            TaskCategory.SIMPLE_CODE,
            TaskCategory.CONFIG
        }
        if self.category in simple_categories and self.complexity == TaskComplexity.SIMPLE:
            return "GROK"

        # Medium complexity with appropriate category → Grok
        if self.complexity == TaskComplexity.SIMPLE:
            return "GROK"

        # Everything else → Claude
        return "CLAUDE"

    def __str__(self) -> str:
        assignee = self.assigned_to
        emoji = "🤖" if assignee == "GROK" else "👨‍💻"
        return f"{emoji} [{assignee}] {self.title}"


# Example tasks
TASKS = [
    Task(
        title="Design bot UI buttons",
        description="Create inline keyboard buttons for Telegram bot",
        category=TaskCategory.DESIGN,
        complexity=TaskComplexity.SIMPLE,
        priority="medium"
    ),
    Task(
        title="Write README documentation",
        description="Create comprehensive setup guide",
        category=TaskCategory.DOCUMENTATION,
        complexity=TaskComplexity.SIMPLE,
        priority="low"
    ),
    Task(
        title="Create helper utility functions",
        description="Utils for file operations and data validation",
        category=TaskCategory.SIMPLE_CODE,
        complexity=TaskComplexity.SIMPLE,
        priority="medium"
    ),
    Task(
        title="Design video generation pipeline architecture",
        description="Plan multi-stage video generation system",
        category=TaskCategory.ARCHITECTURE,
        complexity=TaskComplexity.COMPLEX,
        priority="critical"
    ),
    Task(
        title="Implement Grok API integration",
        description="Core logic for Grok API calls and processing",
        category=TaskCategory.CORE_LOGIC,
        complexity=TaskComplexity.COMPLEX,
        priority="critical"
    ),
    Task(
        title="Add error handling and validation",
        description="Critical error handling for API calls",
        category=TaskCategory.SECURITY,
        complexity=TaskComplexity.COMPLEX,
        priority="critical"
    ),
    Task(
        title="Create config file structure",
        description="Setup .env and config.py files",
        category=TaskCategory.CONFIG,
        complexity=TaskComplexity.SIMPLE,
        priority="high"
    ),
]


def print_task_routing():
    """Print task routing analysis"""
    print("=" * 80)
    print("📋 TASK ROUTING SYSTEM")
    print("=" * 80)
    print()

    claude_tasks = []
    grok_tasks = []

    for task in TASKS:
        if task.assigned_to == "CLAUDE":
            claude_tasks.append(task)
        else:
            grok_tasks.append(task)

    print(f"👨‍💻 CLAUDE (Main Architect) - {len(claude_tasks)} tasks:")
    print("-" * 80)
    for task in claude_tasks:
        print(f"  ✓ {task.title}")
        print(f"    └─ {task.description}")
        print(f"    └─ [{task.category.value}] [{task.complexity.value}] [{task.priority}]")
        print()

    print()
    print(f"🤖 GROK (Assistant) - {len(grok_tasks)} tasks:")
    print("-" * 80)
    for task in grok_tasks:
        print(f"  ✓ {task.title}")
        print(f"    └─ {task.description}")
        print(f"    └─ [{task.category.value}] [{task.complexity.value}] [{task.priority}]")
        print()

    print()
    print("=" * 80)
    print(f"SUMMARY: Claude {len(claude_tasks)} | Grok {len(grok_tasks)}")
    print("=" * 80)


if __name__ == "__main__":
    print_task_routing()
