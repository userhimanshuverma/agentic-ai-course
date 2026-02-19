import requests
import json

MODEL = "mistral"

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


if __name__ == "__main__":
    goal = input("Enter your goal: ")
    plan = planning_agent(goal)

    if plan:
        print("\nStructured Plan:\n")
        print(json.dumps(plan, indent=2))