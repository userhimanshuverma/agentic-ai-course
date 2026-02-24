"""
Long-Term Memory Agent - Persistent memory with semantic search
"""
import requests
import json
import re
from memory import LongTermMemory, HybridMemory
from memory_short import ConversationMemory
from tools import get_tool, list_tools

MODEL = "mistral"

# Initialize hybrid memory (short-term + long-term)
MEMORY = HybridMemory(
    short_term_limit=10,
    long_term_file="memory_store.json"
)


def detect_tool(goal: str):
    """Detect which tool to use based on user input."""
    goal_lower = goal.lower()

    if any(word in goal_lower for word in ["organize", "sort files", "clean folder"]):
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
        return "file_organizer", {"folder_path": "~/Downloads"}

    if any(word in goal_lower for word in ["disk", "storage", "space", "usage"]):
        return "system", {"command_type": "disk_usage"}

    if any(word in goal_lower for word in ["os", "operating system", "platform"]):
        return "system", {"command_type": "os_info"}

    if any(word in goal_lower for word in ["list", "show files", "what's in", "what is in"]):
        match = re.search(r'(?:in|from|at)\s+["\']?([^"\']+)["\']?', goal_lower)
        if match:
            path = match.group(1)
            return "list_directory", {"path": path}
        return "list_directory", {"path": "."}

    if re.search(r'[0-9]', goal) and re.search(r'[\+\-\*/]', goal):
        expression = re.findall(r'[0-9+\-*/().]+', goal)
        expression = "".join(expression)
        return "calculator", {"expression": expression}

    return None, None


def long_term_memory_agent(goal: str):
    """
    Main agent with long-term memory.
    Uses hybrid memory (short-term + long-term) for context.
    """
    global MEMORY

    # Check for memory commands
    if goal.lower() in ["clear memory", "forget everything", "reset memory"]:
        MEMORY.clear_all()
        return {"message": "All memory cleared. Starting fresh."}

    if goal.lower() in ["clear short term", "forget conversation"]:
        MEMORY.clear_short_term()
        return {"message": "Short-term memory cleared. Long-term memories preserved."}

    if goal.lower() in ["show memory", "what do you remember"]:
        stats = MEMORY.long_term.get_stats()
        short_term = MEMORY.short_term.get_context_string()
        return {
            "message": "Memory Status",
            "long_term_stats": stats,
            "short_term_conversation": short_term if short_term else "No recent conversation."
        }

    if goal.lower().startswith("search memory"):
        query = goal.replace("search memory", "").strip()
        results = MEMORY.long_term.search(query)
        return {
            "message": f"Found {len(results)} relevant memories",
            "query": query,
            "memories": results
        }

    if goal.lower() == "list all memories":
        all_memories = MEMORY.long_term.get_all()
        return {
            "message": f"Total memories: {len(all_memories)}",
            "memories": [{"id": m["id"], "content": m["content"], "type": m["type"]} for m in all_memories]
        }

    # Add user message to memory
    MEMORY.short_term.add_user_message(goal)

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
            MEMORY.add_interaction(goal, json.dumps(response), store_long_term=True)
            return response

    # No tool detected - use LLM with memory context
    print("\n🧠 Using LLM with long-term memory...")

    # Get context from both memories
    context = MEMORY.get_context(query=goal)

    # Format long-term memories for prompt
    long_term_context = ""
    if context['long_term']:
        long_term_context = "\nRelevant past information:\n"
        for mem in context['long_term']:
            long_term_context += f"- {mem['content']} (relevance: {mem['similarity']})\n"

    prompt = f"""You are a helpful AI assistant with long-term memory.

You can remember information from previous conversations and use it to answer questions.

Recent conversation:
{context['short_term'] if context['short_term'] else "No recent conversation."}
{long_term_context}
Current user request: {goal}

Respond naturally, using relevant past information if helpful.
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

        # Store interaction in memory
        MEMORY.add_interaction(goal, answer, store_long_term=True)

        return response_obj

    except Exception as e:
        return {"error": f"Failed to get LLM response: {str(e)}"}


def main():
    """Main interactive loop."""
    print("=" * 60)
    print("🧠 Long-Term Memory Agent")
    print("=" * 60)
    print("\nI remember things across sessions!")
    print("\nMemory commands:")
    print("  • 'show memory' - See all memory status")
    print("  • 'search memory <query>' - Search long-term memories")
    print("  • 'list all memories' - List all stored memories")
    print("  • 'clear memory' - Clear all memories")
    print("  • 'clear short term' - Clear only conversation")
    print("\nI can also:")
    print(f"  • Use tools: {', '.join(list_tools())}")
    print("  • Remember facts, preferences, and context")
    print()

    while True:
        try:
            goal = input("\nYou: ").strip()

            if goal.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye! Memories saved.")
                break

            if not goal:
                continue

            response = long_term_memory_agent(goal)

            print("\nAgent:")
            print(json.dumps(response, indent=2))

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye! Memories saved.")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
