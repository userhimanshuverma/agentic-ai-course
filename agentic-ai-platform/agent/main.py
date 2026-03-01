#!/usr/bin/env python3
"""
Agentic AI Platform - Main Entry Point

Usage:
    python main.py --goal "Your goal here"
    python main.py --api          # Run API server
    python main.py --mcp-server   # Run MCP server
"""

import argparse
import sys
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agentic_ai.agent.core import agent
from agentic_ai.api.server import run_api
from agentic_ai.mcp_server.server import run_server as run_mcp_server
from agentic_ai.utils.logger import logger


def print_banner():
    """Print welcome banner."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           🤖 Agentic AI Platform (MCP-enabled)               ║
║                                                              ║
║   Plan → Execute → Reflect with Local LLM (Mistral/Ollama)   ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)


def run_cli_goal(goal: str, detail: bool = False):
    """Run a goal from CLI."""
    print_banner()
    print(f"\n🎯 Goal: {goal}\n")
    print("=" * 60)
    
    try:
        # Run the goal
        report = agent.run_goal(goal)
        
        print("\n" + "=" * 60)
        print("\n📊 EXECUTION REPORT")
        print("=" * 60)
        
        print(f"\n✅ Success: {report.success}")
        print(f"⏱️  Execution Time: {report.total_execution_time_ms:.0f}ms")
        print(f"📋 Steps Executed: {len(report.results)}")
        
        successful = sum(1 for r in report.results if r.success)
        print(f"✓ Successful: {successful}")
        print(f"✗ Failed: {len(report.results) - successful}")
        
        print(f"\n📝 Summary:")
        print(f"   {report.reflection.summary}")
        
        if report.reflection.lessons_learned:
            print(f"\n💡 Lessons Learned:")
            for lesson in report.reflection.lessons_learned:
                print(f"   • {lesson}")
        
        if detail:
            print("\n" + "=" * 60)
            print("📋 DETAILED RESULTS")
            print("=" * 60)
            
            print("\n📍 Plan:")
            for step in report.plan.steps:
                print(f"   {step.step_number}. {step.description}")
                if step.tool_call:
                    tool_name = step.tool_call.tool_name if hasattr(step.tool_call, 'tool_name') else step.tool_call.get('tool_name', 'unknown')
                    print(f"      Tool: {tool_name}")
            
            print("\n📍 Step Results:")
            for result in report.results:
                status = "✓" if result.success else "✗"
                print(f"   {status} Step {result.step_number}: {result.execution_time_ms:.0f}ms")
                if result.output:
                    print(f"      Output: {str(result.output)[:100]}")
                if result.error:
                    print(f"      Error: {result.error}")
        
        print("\n" + "=" * 60)
        
        # Save report to file
        # Generate a goal_id from the goal if not present
        import hashlib
        goal_id = hashlib.md5(report.goal.encode()).hexdigest()[:8]
        output_file = f"execution_report_{goal_id}.json"
        with open(output_file, 'w') as f:
            json.dump(report.model_dump(), f, indent=2, default=str)
        print(f"\n💾 Full report saved to: {output_file}")
        
        return 0 if report.success else 1
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        logger.error(f"CLI execution failed: {str(e)}")
        return 1


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Agentic AI Platform - MCP-enabled Agent with Local LLM"
    )
    
    parser.add_argument(
        "--goal",
        type=str,
        help="Goal to execute"
    )
    
    parser.add_argument(
        "--api",
        action="store_true",
        help="Run API server"
    )
    
    parser.add_argument(
        "--mcp-server",
        action="store_true",
        help="Run MCP server"
    )
    
    parser.add_argument(
        "--detail",
        action="store_true",
        help="Show detailed output"
    )
    
    parser.add_argument(
        "--health",
        action="store_true",
        help="Check system health"
    )
    
    args = parser.parse_args()
    
    # Health check
    if args.health:
        health = agent.health_check()
        print("\n🏥 System Health Check")
        print("=" * 40)
        print(f"Status: {health['status']}")
        print(f"LLM Available: {'✓' if health['llm_available'] else '✗'}")
        print(f"Memory Available: {'✓' if health['memory_available'] else '✗'}")
        print("")
        
        if not health['llm_available']:
            print("⚠️  LLM not available. Make sure Ollama is running:")
            print("   1. Install Ollama: https://ollama.ai")
            print("   2. Pull Mistral: ollama pull mistral")
            print("   3. Start Ollama: ollama serve")
        
        return 0
    
    # Run API server
    if args.api:
        print_banner()
        print("\n🚀 Starting API server...")
        print("   API docs: http://localhost:8000/docs\n")
        run_api()
        return 0
    
    # Run MCP server
    if args.mcp_server:
        print("\n🔌 Starting MCP server...")
        run_mcp_server()
        return 0
    
    # Run goal
    if args.goal:
        return run_cli_goal(args.goal, args.detail)
    
    # Interactive mode
    print_banner()
    print("\n💡 Usage:")
    print("   python main.py --goal 'Your goal here'")
    print("   python main.py --api")
    print("   python main.py --mcp-server")
    print("   python main.py --health")
    print("")
    
    # Try interactive
    try:
        goal = input("Enter your goal (or press Ctrl+C to exit): ")
        if goal.strip():
            return run_cli_goal(goal, args.detail)
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
