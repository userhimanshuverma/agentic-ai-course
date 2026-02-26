"""
Autonomous Agent - Reasoning Loop Implementation
Plan → Act → Observe → Repeat until goal complete
"""
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from tools import get_tool, list_tools


class ReasoningStep:
    """Represents a single step in the reasoning process."""

    def __init__(self, step_number: int, action: str, tool: str = None, params: dict = None):
        self.step_number = step_number
        self.action = action  # Description of what to do
        self.tool = tool      # Tool to use (if any)
        self.params = params or {}  # Tool parameters
        self.result = None    # Result after execution
        self.status = "pending"  # pending, running, success, failed
        self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "step": self.step_number,
            "action": self.action,
            "tool": self.tool,
            "params": self.params,
            "result": self.result,
            "status": self.status,
            "timestamp": self.timestamp
        }


class AutonomousAgent:
    """
    Agent that uses a reasoning loop:
    Plan → Act → Observe → Repeat until goal complete
    """

    def __init__(self, max_steps: int = 5):
        self.max_steps = max_steps
        self.steps: List[ReasoningStep] = []
        self.goal = None
        self.goal_complete = False

    def plan(self, goal: str, previous_results: List[dict] = None) -> ReasoningStep:
        """
        Plan the next step based on goal and previous results.
        In a full implementation, this would use an LLM.
        For now, we use simple logic.
        """
        step_number = len(self.steps) + 1

        # Simple goal-based planning logic
        goal_lower = goal.lower()

        # Check if we have previous results to guide next step
        if previous_results:
            last_result = previous_results[-1]

            # If last step was checking disk and it showed warning/critical
            if last_result.get("tool") == "check_disk":
                disk_status = last_result.get("result", {}).get("status", "")
                if disk_status in ["warning", "critical"]:
                    return ReasoningStep(
                        step_number=step_number,
                        action="Disk space is low. Identify large folders to organize.",
                        tool="suggest_organize",
                        params={}
                    )
                else:
                    return ReasoningStep(
                        step_number=step_number,
                        action="Disk space is healthy. Goal achieved.",
                        tool=None,
                        params={}
                    )

            # If last step suggested folders, now organize them
            if last_result.get("tool") == "suggest_organize":
                suggestions = last_result.get("result", {}).get("suggestions", [])
                if suggestions:
                    target = suggestions[0]["path"]  # Organize largest folder
                    return ReasoningStep(
                        step_number=step_number,
                        action=f"Organizing files in {suggestions[0]['folder']} to free space.",
                        tool="file_organizer",
                        params={"folder_path": target}
                    )
                else:
                    return ReasoningStep(
                        step_number=step_number,
                        action="No large folders found. Checking for other issues.",
                        tool="check_disk",
                        params={}
                    )

            # After organizing, re-check disk
            if last_result.get("tool") == "file_organizer":
                return ReasoningStep(
                    step_number=step_number,
                    action="Files organized. Re-checking disk usage to verify improvement.",
                    tool="check_disk",
                    params={}
                )

        # Initial planning based on goal keywords
        if any(word in goal_lower for word in ["disk", "space", "storage", "full"]):
            return ReasoningStep(
                step_number=step_number,
                action="Check current disk usage to assess the situation.",
                tool="check_disk",
                params={}
            )

        elif any(word in goal_lower for word in ["organize", "clean", "sort"]):
            # Extract folder path or use default
            import re
            match = re.search(r'(?:in|at|folder)\s+([\w/\\~]+)', goal_lower)
            folder = match.group(1) if match else "~/Downloads"
            return ReasoningStep(
                step_number=step_number,
                action=f"Organize files in {folder} by type.",
                tool="file_organizer",
                params={"folder_path": folder}
            )

        elif any(word in goal_lower for word in ["system", "info", "about"]):
            return ReasoningStep(
                step_number=step_number,
                action="Gather system information.",
                tool="system_info",
                params={}
            )

        elif any(word in goal_lower for word in ["calculate", "math", "compute"]):
            import re
            # Extract expression
            expression = re.findall(r'[0-9+\-*/().]+', goal)
            if expression:
                expr = "".join(expression)
                return ReasoningStep(
                    step_number=step_number,
                    action=f"Calculate: {expr}",
                    tool="calculator",
                    params={"expression": expr}
                )

        # Default: try to use system info
        return ReasoningStep(
            step_number=step_number,
            action="Gather basic system information to understand context.",
            tool="system_info",
            params={}
        )

    def act(self, step: ReasoningStep) -> dict:
        """
        Execute the planned step using appropriate tool.
        """
        step.status = "running"
        print(f"\n🔧 Step {step.step_number}: {step.action}")

        if step.tool is None:
            # No tool needed, just a conclusion
            step.status = "success"
            step.result = {"message": "Goal achieved", "complete": True}
            print(f"   ✓ {step.result['message']}")
            return step.result

        tool = get_tool(step.tool)
        if tool is None:
            step.status = "failed"
            step.result = {"error": f"Tool '{step.tool}' not found"}
            print(f"   ✗ Error: {step.result['error']}")
            return step.result

        try:
            result = tool(**step.params)
            step.result = result
            step.status = "success"
            print(f"   ✓ Success")
            if isinstance(result, dict):
                # Print key results
                if "message" in result:
                    print(f"   📋 {result['message']}")
                if "status" in result:
                    print(f"   📊 Status: {result['status']}")
            return result
        except Exception as e:
            step.status = "failed"
            step.result = {"error": str(e)}
            print(f"   ✗ Failed: {str(e)}")
            return step.result

    def observe(self, step: ReasoningStep) -> bool:
        """
        Observe the result and determine if goal is complete.
        Returns True if goal is complete, False otherwise.
        """
        result = step.result

        if result is None:
            return False

        # Check if result indicates completion
        if isinstance(result, dict):
            # Explicit completion flag
            if result.get("complete") is True:
                return True

            # For disk check - if healthy after fixes
            if step.tool == "check_disk":
                status = result.get("status")
                # If we've done multiple steps and disk is now good
                if len(self.steps) > 1 and status == "good":
                    return True
                # If disk was never bad (initial check was good)
                if len(self.steps) == 1 and status == "good":
                    return True

            # For file organizer - always complete after organizing
            if step.tool == "file_organizer":
                if "error" not in result:
                    # Will re-check in next iteration
                    return False

            # For system info - complete after gathering info
            if step.tool == "system_info":
                # One-time info gathering is complete
                return True

            # For calculator - complete after calculation
            if step.tool == "calculator":
                # One-time calculation is complete
                return True

        return False

    def run(self, goal: str) -> dict:
        """
        Run the autonomous reasoning loop.
        Plan → Act → Observe → Repeat
        """
        self.goal = goal
        self.steps = []
        self.goal_complete = False

        print("=" * 60)
        print("🤖 Autonomous Agent - Reasoning Loop")
        print("=" * 60)
        print(f"\n🎯 Goal: {goal}")
        print(f"\n📋 Starting reasoning loop (max {self.max_steps} steps)...\n")

        previous_results = []

        for iteration in range(self.max_steps):
            print(f"\n{'─' * 50}")
            print(f"🔄 Iteration {iteration + 1}/{self.max_steps}")
            print('─' * 50)

            # PLAN: Decide next step
            print("\n🧠 PLANNING...")
            step = self.plan(goal, previous_results)
            self.steps.append(step)

            # ACT: Execute the step
            result = self.act(step)
            previous_results.append({
                "step": step.step_number,
                "tool": step.tool,
                "result": result
            })

            # OBSERVE: Check if goal is complete
            print("\n👁️ OBSERVING...")
            self.goal_complete = self.observe(step)

            if self.goal_complete:
                print(f"\n✅ Goal complete! Stopping after {step.step_number} steps.")
                break

            # Small delay for readability
            time.sleep(0.5)

        else:
            print(f"\n⏹️ Max steps ({self.max_steps}) reached. Stopping.")

        return self._generate_report()

    def _generate_report(self) -> dict:
        """Generate final execution report."""
        return {
            "goal": self.goal,
            "goal_complete": self.goal_complete,
            "total_steps": len(self.steps),
            "max_steps": self.max_steps,
            "execution_time": datetime.now().isoformat(),
            "steps": [step.to_dict() for step in self.steps],
            "summary": self._generate_summary()
        }

    def _generate_summary(self) -> str:
        """Generate human-readable summary."""
        if not self.steps:
            return "No steps executed."

        successful = sum(1 for s in self.steps if s.status == "success")
        failed = sum(1 for s in self.steps if s.status == "failed")

        summary = f"Executed {len(self.steps)} steps. "
        summary += f"Successful: {successful}, Failed: {failed}. "

        if self.goal_complete:
            summary += "Goal was achieved."
        else:
            summary += "Goal was not fully achieved."

        return summary


def main():
    """Main interactive loop."""
    print("=" * 60)
    print("🤖 Autonomous Agent with Reasoning Loop")
    print("=" * 60)
    print("\nThis agent uses: Plan → Act → Observe → Repeat")
    print("It takes multiple steps to achieve goals.")
    print("\nExample goals:")
    print("  • 'Fix high disk usage'")
    print("  • 'Organize my Downloads folder'")
    print("  • 'Check system status'")
    print("\nCommands:")
    print("  • 'exit' - Quit")
    print()

    agent = AutonomousAgent(max_steps=5)

    while True:
        try:
            goal = input("\n🎯 Enter your goal: ").strip()

            if goal.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye!")
                break

            if not goal:
                continue

            result = agent.run(goal)

            print("\n" + "=" * 60)
            print("📊 FINAL REPORT")
            print("=" * 60)
            print(f"\nGoal: {result['goal']}")
            print(f"Complete: {'✅ Yes' if result['goal_complete'] else '❌ No'}")
            print(f"Steps taken: {result['total_steps']}")
            print(f"\nSummary: {result['summary']}")

            print("\n📋 Step-by-step execution:")
            for step in result['steps']:
                status_icon = "✓" if step['status'] == "success" else "✗"
                print(f"\n  Step {step['step']}: [{status_icon}] {step['action']}")
                if step['tool']:
                    print(f"           Tool: {step['tool']}")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
