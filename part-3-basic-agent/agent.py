import requests
import json
import re

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
# 🤖 AGENT: Decide Action
# -----------------------------
def tool_agent(goal: str):
    """
    Agent decides whether to:
    - Use calculator tool
    - Or generate planning steps
    """

    # Detect possible math
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

    else:
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
    goal = input("Enter your goal: ")

    response = tool_agent(goal)

    print("\n=== AGENT OUTPUT ===\n")
    print(json.dumps(response, indent=2))