"""
Support Assistant Agent - Remembers you and your issues
"""
import re
import json
from datetime import datetime
from memory import SupportMemory
from tools import get_tool, list_tools


class SupportAssistant:
    """
    A support assistant that remembers users and their issues.
    """

    def __init__(self):
        self.memory = SupportMemory()
        self.user_name = None
        self._load_user()

    def _load_user(self):
        """Load user name from memory if available."""
        self.user_name = self.memory.get_user_name()

    def _get_greeting(self) -> str:
        """Generate personalized greeting."""
        if self.user_name:
            return f"Hello {self.user_name}! Welcome back. How can I help you today?"
        return "Hello! I'm your support assistant. What's your name?"

    def _extract_name(self, message: str) -> str:
        """Extract name from message."""
        patterns = [
            r"my name is\s+(\w+)",
            r"i am\s+(\w+)",
            r"call me\s+(\w+)",
            r"i'm\s+(\w+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1)
        return None

    def _detect_issue(self, message: str) -> dict:
        """Detect issue type from message."""
        message_lower = message.lower()

        # Issue categories
        categories = {
            "disk": ["disk", "space", "storage", "full", "cleanup", "drive"],
            "slow": ["slow", "lag", "freeze", "hang", "performance", "speed"],
            "network": ["network", "wifi", "internet", "connection", "online"],
            "memory": ["memory", "ram", "out of memory", "crash"],
            "software": ["app", "program", "software", "application", "install"],
            "hardware": ["hardware", "device", "driver", "screen", "keyboard"]
        }

        for category, keywords in categories.items():
            if any(kw in message_lower for kw in keywords):
                return {"category": category, "description": message}

        return {"category": "general", "description": message}

    def _is_question_about_past(self, message: str) -> bool:
        """Check if user is asking about past issues."""
        patterns = [
            r"what was my last",
            r"previous issue",
            r"past problem",
            r"remember.*issue",
            r"last time",
            r"before",
            r"earlier"
        ]
        message_lower = message.lower()
        return any(re.search(p, message_lower) for p in patterns)

    def process(self, message: str) -> dict:
        """
        Process user message and return response.
        """
        message_lower = message.lower().strip()

        # Check for memory commands
        if message_lower in ["clear memory", "forget everything"]:
            self.memory.clear_all()
            self.user_name = None
            return {
                "type": "system",
                "message": "All memory cleared. Starting fresh."
            }

        if message_lower in ["show memory", "memory status"]:
            stats = self.memory.get_stats()
            return {
                "type": "system",
                "message": "Memory Status",
                "data": stats
            }

        if message_lower == "list my issues":
            issues = self.memory.get_issues()
            return {
                "type": "system",
                "message": f"Found {len(issues)} issue(s)",
                "issues": issues
            }

        if message_lower.startswith("resolve "):
            # Try to resolve an issue by description
            issue_desc = message[8:].strip()
            issues = self.memory.search_issues(issue_desc)
            if issues:
                issue_id = issues[0]["id"]
                self.memory.resolve_issue(issue_id, "Resolved by user request")
                return {
                    "type": "system",
                    "message": f"Marked issue as resolved: {issues[0]['description'][:50]}..."
                }
            return {
                "type": "system",
                "message": "Could not find matching issue to resolve."
            }

        # Check if user is telling their name
        name = self._extract_name(message)
        if name and not self.user_name:
            self.memory.set_user_name(name)
            self.user_name = name
            response = f"Nice to meet you, {name}! I'll remember you. How can I help today?"
            self.memory.add_conversation(message, response)
            return {
                "type": "greeting",
                "message": response
            }

        # Check if asking about past issues
        if self._is_question_about_past(message):
            last_issue = self.memory.get_last_issue()
            if last_issue:
                response = f"Your last issue was about {last_issue['category']}: {last_issue['description']}"
                if last_issue['status'] == 'resolved':
                    response += " (This has been resolved)"
                else:
                    response += " (This is still open)"
            else:
                response = "I don't have any previous issues recorded for you."

            self.memory.add_conversation(message, response)
            return {
                "type": "memory_query",
                "message": response
            }

        # Detect and record new issue
        issue_info = self._detect_issue(message)

        # Check if it's actually an issue or just a question
        issue_keywords = ["problem", "issue", "error", "help", "fix", "trouble"]
        is_issue = any(kw in message_lower for kw in issue_keywords)

        if is_issue:
            issue_id = self.memory.add_issue(
                issue_description=issue_info["description"],
                category=issue_info["category"]
            )

            # Try to help with the issue
            response = self._help_with_issue(issue_info)

            self.memory.add_conversation(message, response)
            return {
                "type": "issue_logged",
                "issue_id": issue_id,
                "category": issue_info["category"],
                "message": response
            }

        # General conversation
        response = self._general_response(message)
        self.memory.add_conversation(message, response)
        return {
            "type": "general",
            "message": response
        }

    def _help_with_issue(self, issue_info: dict) -> str:
        """Generate help response for an issue."""
        category = issue_info["category"]
        user = self.user_name or "there"

        responses = {
            "disk": f"Hi {user}, I see you're having disk space issues. Let me check your disk and suggest solutions.",
            "slow": f"Hi {user}, performance issues can be frustrating. Let me help you troubleshoot.",
            "network": f"Hi {user}, network issues are common. Let's diagnose the problem.",
            "memory": f"Hi {user}, memory issues can cause crashes. Let me suggest some fixes.",
            "software": f"Hi {user}, software issues can often be resolved with updates or reinstallation.",
            "hardware": f"Hi {user}, hardware issues may need driver updates or physical checks."
        }

        base_response = responses.get(category, f"Hi {user}, I'll help you with that issue.")

        # Add tool suggestions
        if category == "disk":
            tool = get_tool("check_disk")
            if tool:
                result = tool()
                base_response += f"\n\nDisk Status: {result.get('message', '')}"
                if result.get('status') in ['warning', 'critical']:
                    base_response += "\n\nWould you like me to suggest folders to organize?"

        # Add common fixes
        fixes = get_tool("get_fixes")
        if fixes:
            common_fixes = fixes(category)
            base_response += f"\n\nCommon fixes for {category} issues:\n"
            for i, fix in enumerate(common_fixes[:3], 1):
                base_response += f"{i}. {fix}\n"

        return base_response.strip()

    def _general_response(self, message: str) -> str:
        """Generate general response."""
        user = self.user_name or "there"

        # Check for thanks
        if any(word in message.lower() for word in ["thanks", "thank you", "great", "awesome"]):
            return f"You're welcome, {user}! Let me know if you need anything else."

        # Check for goodbye
        if any(word in message.lower() for word in ["bye", "goodbye", "see you"]):
            return f"Goodbye, {user}! Feel free to come back anytime."

        return f"I understand, {user}. Tell me more about what you need help with."


def main():
    """Main interactive loop."""
    assistant = SupportAssistant()

    print("=" * 60)
    print("🎧 Support Assistant - I Remember You!")
    print("=" * 60)
    print("\nI can help you with:")
    print("  • Technical issues (disk, network, performance)")
    print("  • Remember your past problems")
    print("  • Suggest solutions based on your history")
    print("\nCommands:")
    print("  • 'show memory' - See what I remember about you")
    print("  • 'list my issues' - See all your past issues")
    print("  • 'resolve <issue>' - Mark an issue as resolved")
    print("  • 'clear memory' - Forget everything")
    print("  • 'exit' - Quit")
    print()

    # Initial greeting
    print(f"Assistant: {assistant._get_greeting()}")

    while True:
        try:
            user_input = input("\nYou: ").strip()

            if not user_input:
                continue

            if user_input.lower() in ['exit', 'quit', 'bye']:
                name = assistant.user_name or "friend"
                print(f"\nAssistant: Goodbye, {name}! Take care.")
                break

            response = assistant.process(user_input)

            print(f"\nAssistant: {response['message']}")

            # Show additional data if present
            if 'data' in response:
                print(f"\n[Memory Data]")
                print(json.dumps(response['data'], indent=2))

            if 'issues' in response:
                print(f"\n[Your Issues]")
                for issue in response['issues'][:5]:  # Show last 5
                    status_icon = "✓" if issue['status'] == 'resolved' else "○"
                    print(f"  {status_icon} [{issue['category'].upper()}] {issue['description'][:60]}...")

        except KeyboardInterrupt:
            print("\n\nAssistant: Goodbye!")
            break
        except Exception as e:
            print(f"\nError: {str(e)}")


if __name__ == "__main__":
    main()
