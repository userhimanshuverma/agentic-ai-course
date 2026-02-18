import requests
import json

MODEL = "mistral"

def planning_agent(goal):
    prompt = f"""
You are a planning AI agent.

Your job:
1. Take a user goal.
2. Break it into clear, ordered, actionable steps.
3. Return the steps as a numbered list only.

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
    return result["response"]

if __name__ == "__main__":
    goal = input("Enter your goal: ")
    plan = planning_agent(goal)
    print("\nGenerated Plan:\n")
    print(plan)