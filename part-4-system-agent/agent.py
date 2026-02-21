import requests
import json
import re
import shutil
import subprocess
import platform

MODEL = "mistral"


# -----------------------------
# 🧮 TOOL: Calculator Function
# -----------------------------
def calculator_tool(expression: str):
    """
    Safely evaluate basic math expressions.
    """
    try:
        # Allow only safe characters (digits, operators, parentheses, spaces)
        if not re.match(r'^[0-9+\-*/().\s]+$', expression):
            return "Invalid characters in expression."

        result = eval(expression)
        return result
    except Exception as e:
        return f"Error calculating expression: {str(e)}"


# -----------------------------
# 💻 TOOL: System Info Function
# -----------------------------
def system_tool(command_type: str):
    """
    Execute safe system commands.
    Supported: disk_usage, memory_info, os_info
    """
    try:
        if command_type == "disk_usage":
            # Get disk usage statistics
            total, used, free = shutil.disk_usage("/")
            return {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "percent_used": round((used / total) * 100, 2)
            }

        elif command_type == "memory_info":
            # Get memory info using platform-specific commands
            system = platform.system()
            if system == "Windows":
                result = subprocess.run(
                    ["wmic", "OS", "get", "TotalVisibleMemorySize,FreePhysicalMemory", "/Value"],
                    capture_output=True, text=True, timeout=10
                )
                return {"memory_info": result.stdout.strip()}
            else:
                result = subprocess.run(
                    ["free", "-h"],
                    capture_output=True, text=True, timeout=10
                )
                return {"memory_info": result.stdout.strip()}

        elif command_type == "os_info":
            return {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }

        else:
            return f"Unknown command: {command_type}"

    except Exception as e:
        return f"Error executing system command: {str(e)}"


# -----------------------------
# 🤖 AGENT: Decide Action
# -----------------------------
def system_agent(goal: str):
    """
    Agent decides whether to:
    - Use calculator tool
    - Use system tool
    - Or generate planning steps
    """
    goal_lower = goal.lower()

    # Detect system-related queries
    system_keywords = ["disk", "memory", "cpu", "system", "os", "platform", "storage", "space"]
    if any(keyword in goal_lower for keyword in system_keywords):
        print("\n🧠 Agent detected a system query.")

        # Determine which system command to run
        if "disk" in goal_lower or "storage" in goal_lower or "space" in goal_lower:
            print("🔧 Checking disk usage...\n")
            result = system_tool("disk_usage")
            return {
                "goal": goal,
                "action": "system_tool",
                "command": "disk_usage",
                "result": result
            }

        elif "memory" in goal_lower or "ram" in goal_lower:
            print("🔧 Checking memory info...\n")
            result = system_tool("memory_info")
            return {
                "goal": goal,
                "action": "system_tool",
                "command": "memory_info",
                "result": result
            }

        elif "os" in goal_lower or "platform" in goal_lower or "system info" in goal_lower:
            print("🔧 Getting OS info...\n")
            result = system_tool("os_info")
            return {
                "goal": goal,
                "action": "system_tool",
                "command": "os_info",
                "result": result
            }

    # Detect math problems
    if re.search(r'[0-9]', goal) and re.search(r'[\+\-\*/]', goal):
        print("\n🧠 Agent detected a math problem.")
        print("🔧 Extracting math expression...\n")

        # Extract valid math characters only
        expression = re.findall(r'[0-9+\-*/().]+', goal)
        expression = "".join(expression)

        print(f"📌 Clean Expression: {expression}")
        print("🔧 Calling calculator tool...\n")

        result = calculator_tool(expression)

        return {
            "goal": goal,
            "action": "calculator_tool",
            "expression": expression,
            "result": result
        }

    # Default to planning
    print("\n🧠 Agent detected a planning task.")
    print("📝 Generating structured plan...\n")

    return planning_agent(goal)


# -----------------------------
# 🧠 PLANNING AGENT (Fallback)
# -----------------------------
def planning_agent(goal):
    prompt = f"""
You are a planning AI agent.

Your job:
1. Take a user goal.
2. Break it into clear, ordered, actionable steps.
3. ALWAYS return valid JSON.
4. Do not return anything except JSON.

The JSON format must be:

{{
  "goal": "<original goal>",
  "steps": [
    "Step 1",
    "Step 2",
    "Step 3"
  ]
}}

User Goal:
{goal}
"""

    response = requests.post(
        "http://localhost:11434/api/generate",
        json={
            "model": MODEL,
            "prompt": prompt,
            "stream": False
        }
    )

    result = response.json()
    raw_output = result["response"].strip()

    try:
        structured_output = json.loads(raw_output)
        return structured_output
    except json.JSONDecodeError:
        print("⚠ Model did not return valid JSON. Raw output:\n")
        print(raw_output)
        return None


# -----------------------------
# 🚀 MAIN
# -----------------------------
if __name__ == "__main__":
    print("=" * 50)
    print("🤖 System Agent - Type 'exit' to quit")
    print("=" * 50)
    print("\nI can help you with:")
    print("  • Math calculations (e.g., 'What is 25 * 4?')")
    print("  • System info (e.g., 'Check disk usage')")
    print("  • Planning tasks (e.g., 'Plan a server setup')")
    print()

    while True:
        goal = input("\nEnter your goal: ")

        if goal.lower() in ['exit', 'quit', 'bye']:
            print("\n👋 Goodbye!")
            break

        if not goal.strip():
            continue

        response = system_agent(goal)

        print("\n=== AGENT OUTPUT ===\n")
        print(json.dumps(response, indent=2))
