"""
DevOps Monitoring Agent
=======================

Simple agent that monitors system health using AI.
- Collects system metrics (CPU, memory, disk, etc.)
- Uses Mistral via Ollama for AI reasoning
- Suggests actions based on metrics
"""

import time
from datetime import datetime
from typing import Dict, Any
from dataclasses import dataclass

from tools import SystemMonitor
from reasoning import AIReasoner
from config import Config


@dataclass
class Step:
    """Execution step"""
    number: int
    action: str
    tool: str
    result: Any
    status: str


class DevOpsAgent:
    """
    Simple DevOps monitoring agent.
    
    Usage:
        agent = DevOpsAgent()
        result = agent.run("Check system health")
    """
    
    def __init__(self, config: Config = None):
        """Initialize agent"""
        self.config = config or Config()
        self.monitor = SystemMonitor()
        self.reasoner = AIReasoner(self.config.ollama_url)
        self.steps = []
        self.start_time = None
    
    def run(self, goal: str) -> Dict[str, Any]:
        """
        Run the agent with a goal.
        
        Args:
            goal: What to monitor (e.g., "Check CPU")
        
        Returns:
            Execution report
        """
        self.steps = []
        self.start_time = datetime.now()
        goal_complete = False
        
        print(f"\n🎯 Goal: {goal}")
        print(f"⚙️  Max steps: {self.config.max_steps}")
        print("─" * 50)
        
        for step_num in range(1, self.config.max_steps + 1):
            # Check timeout
            if self._timeout():
                print("⏱️  Timeout!")
                break
            
            # Execute step
            step = self._execute_step(step_num, goal)
            self.steps.append(step)
            
            if step.status == "complete":
                goal_complete = True
                print(f"\n✅ Goal complete!")
                break
        else:
            print(f"\n⏹️  Max steps ({self.config.max_steps}) reached")
        
        return self._report(goal, goal_complete)
    
    def _execute_step(self, num: int, goal: str) -> Step:
        """Execute one step"""
        print(f"\n🔄 Step {num}")
        
        # Get metrics
        metrics = self.monitor.get_all_metrics()
        
        # Ask AI what to do
        ai_result = self.reasoner.analyze(metrics, goal)
        
        print(f"🧠 Action: {ai_result.action}")
        print(f"🔧 Tool: {ai_result.tool_to_use}")
        
        # Execute tool
        result = self._run_tool(ai_result.tool_to_use)
        
        # Show result
        self._show_result(ai_result.tool_to_use, result)
        
        status = "complete" if ai_result.is_complete else "continue"
        print(f"📊 Status: {status}")
        
        return Step(num, ai_result.action, ai_result.tool_to_use, result, status)
    
    def _run_tool(self, tool_name: str) -> Any:
        """Run a monitoring tool"""
        tools = {
            "get_cpu_metrics": self.monitor.get_cpu_metrics,
            "get_memory_metrics": self.monitor.get_memory_metrics,
            "get_disk_metrics": self.monitor.get_disk_metrics,
            "get_network_metrics": self.monitor.get_network_metrics,
            "get_process_metrics": lambda: self.monitor.get_process_metrics(10),
            "get_all_metrics": self.monitor.get_all_metrics,
        }
        
        tool = tools.get(tool_name, self.monitor.get_all_metrics)
        return tool()
    
    def _show_result(self, tool_name: str, result: Any):
        """Display tool result to user"""
        if tool_name == "get_process_metrics":
            print("\n📋 Top Processes:")
            print("-" * 40)
            print(f"{'Name':<20} {'CPU %':<10} {'Memory %':<10}")
            print("-" * 40)
            for proc in result:
                print(f"{proc['name']:<20} {proc['cpu_percent']:<10.1f} {proc['memory_percent']:<10.1f}")
        elif tool_name == "get_cpu_metrics":
            print(f"\n📊 CPU Usage: {result.percent}% ({result.status})")
        elif tool_name == "get_memory_metrics":
            print(f"\n📊 Memory: {result.used_gb:.1f} GB / {result.total_gb:.1f} GB ({result.percent}%)")
        elif tool_name == "get_disk_metrics":
            print(f"\n📊 Disk: {result.used_gb:.1f} GB / {result.total_gb:.1f} GB ({result.percent}%)")
        elif tool_name == "get_all_metrics":
            print(f"\n📊 System Overview:")
            print(f"   CPU: {result['cpu'].percent}%")
            print(f"   Memory: {result['memory'].percent}%")
            print(f"   Disk: {result['disk'].percent}%")
    
    def _timeout(self) -> bool:
        """Check if timed out"""
        if not self.start_time:
            return False
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed > self.config.max_time
    
    def _report(self, goal: str, complete: bool) -> Dict[str, Any]:
        """Generate execution report"""
        elapsed = (datetime.now() - self.start_time).total_seconds()
        
        report = {
            "goal": goal,
            "complete": complete,
            "steps": len(self.steps),
            "time_seconds": round(elapsed, 1),
            "actions": [s.action for s in self.steps]
        }
        
        print("\n" + "=" * 50)
        print("📊 REPORT")
        print("=" * 50)
        print(f"Goal: {goal}")
        print(f"Complete: {'Yes' if complete else 'No'}")
        print(f"Steps: {report['steps']}")
        print(f"Time: {report['time_seconds']}s")
        print("=" * 50)
        
        return report


def main():
    """Main entry point"""
    print("=" * 50)
    print("🖥️  DevOps Monitoring Agent")
    print("=" * 50)
    print("\nGoals: 'Check CPU', 'Check memory', 'Check disk', etc.")
    
    goal = input("\nEnter goal: ").strip()
    if not goal:
        goal = "Check system health"
    
    agent = DevOpsAgent()
    agent.run(goal)


if __name__ == "__main__":
    main()
