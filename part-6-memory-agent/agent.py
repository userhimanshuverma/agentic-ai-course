"""
Memory Agent - Agent with short-term conversation memory
"""
import requests
import json
import re
from memory import ConversationMemory
from tools import get_tool, list_tools

MODEL = "mistral"
MEMORY = ConversationMemory(max_history=10)


def detect_tool(goal: str):
    """
    Detect which tool to use based on user input.
    Returns tuple of (tool_name, parameters)
    """
    goal_lower = goal.lower()

    # Check for file organization requests
    if any(word in goal_lower for word in ["organize", "sort files", "clean folder"]):
        # Try to extract folder path
        patterns = [
            r'(?:in|from|at)\s+["\']?([^"\']+)["\']?',
            r'(?:folder|directory|path)\s+["\']?([^"\']+)["\']?',
            r'(?:downloads|desktop|documents)',
        ]

        for pattern in patterns:
            match = re.search(pattern, goal_lower)
            if match:
                path = match.group(1) if match.groups() else match.group(0)
                if path in ['downloads', 'desktop', 'documents']:
                    path = f"~/{path.capitalize()}"
                return "file_organizer", {"folder_path": path}

        # Default to Downloads if no path specified
        return "file_organizer", {"folder_path": "~/Downloads"}

    # Check for system info requests
    if any(word in goal_lower for word in ["disk", "storage", "space", "usage"]):
        return "system", {"command_type": "disk_usage"}

    if any(word in goal_lower for word in ["os", "operating system", "platform"]):
        return "system", {"command_type": "os_info"}

    # Check for list directory requests
    if any(word in goal_lower for word in ["list", "show files", "what's in", "what is in"]):
        # Try to extract path
        match = re.search(r'(?:in|from|at)\s+["\']?([^"\']+)["\']?', goal_lower)
        if match:
            path = match.group(1)
            return "list_directory", {"path": path}
        return "list_directory", {"path": "."}

    # Check for calculator
    if re.search(r'[0-9]', goal) and re.search(r'[\+\-\*/]', goal):
        expression = re.findall(r'[0-9+\-*/().]+', goal)
        expression = "".join(expression)
        return "calculator", {"expression": expression}

    return None, None


def memory_agent(goal: str):
    """
    Main agent with memory.
    Uses conversation history for context.
    """
    global MEMORY

    # Add user message to memory
    MEMORY.add_user_message(goal)

    # Check for memory-related commands
    if goal.lower() in ["clear memory", "forget everything", "reset memory"]:
        MEMORY.clear()
        response = {"message": "Memory cleared. Starting fresh conversation."}
        MEMORY.add_assistant_message(json.dumps(response))
        return response

    if goal.lower() in ["show memory", "what do you remember", "conversation history"]:
        history = MEMORY.get_context_string()
        response = {
            "message": "Here's what I remember:",
            "memory": history if history else "Nothing yet."
        }
        MEMORY.add_assistant_message(json.dumps(response))
        return response

    # Detect if we need a tool
    tool_name, tool_params = detect_tool(goal)

    if tool_name:
        print(f"\n🔧 Using tool: {tool_name}")
        tool = get_tool(tool_name)

        if tool:
            result = tool(**tool_params)
            response = {
                "goal": goal,
                "action": tool_name,
                "parameters": tool_params,
                "result": result
            }
            MEMORY.add_assistant_message(json.dumps(response))
            return response

    # No tool detected - use LLM with memory context
    print("\n🧠 Using LLM with memory context...")

    # Build prompt with memory
    context = MEMORY.get_context_string()

    prompt = f"""You are a helpful AI assistant with memory.

You can remember the conversation history and use it to answer follow-up questions.

Previous conversation:
{context if context else "No previous conversation."}

Current user request: {goal}

Respond naturally, referencing previous context if relevant.
Keep responses concise and helpful.
"""

    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            }
        )

        result = response.json()
        answer = result["response"].strip()

        response_obj = {
            "goal": goal,
            "action": "llm_response",
            "response": answer
        }

        MEMORY.add_assistant_message(answer)
        return response_obj

    except Exception as e:
        error_response = {
            "error": f"Failed to get LLM response: {str(e)}"
        }
        MEMORY.add_assistant_message(json.dumps(error_response))
        return error_response


def main():
    """Main interactive loop."""
    print("=" * 60)
    print("🧠 Memory Agent - I remember our conversation!")
    print("=" * 60)
    print("\nAvailable commands:")
    print("  • 'show memory' - See what I remember")
    print("  • 'clear memory' - Forget everything")
    print("  • 'exit' - Quit")
    print("\nI can also:")
    print(f"  • Use tools: {', '.join(list_tools())}")
    print("  • Answer questions with context")
    print()

    while True:
        try:
            goal = input("\nYou: ").strip()

            if goal.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye!")
                break

            if not goal:
                continue

            response = memory_agent(goal)

            print("\nAgent:")
            print(json.dumps(response, indent=2))

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
