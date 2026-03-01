#!/usr/bin/env python3
"""
Agentic AI Platform - Examples & Test Script

This script demonstrates all the capabilities of the Agentic AI Platform.
Run it to see how each component works.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from agentic_ai.mcp_server.tools import *
from agentic_ai.agent import agent


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def example_1_calculator():
    """Example 1: Calculator Tool"""
    print_section("Example 1: Calculator Tool")
    
    examples = [
        {"expression": "2 + 2"},
        {"expression": "10 * 5"},
        {"expression": "sqrt(144)"},
        {"expression": "2^10"},
        {"expression": "sin(0)"},
        {"expression": "pi * 5^2"},  # Area of circle
    ]
    
    for ex in examples:
        print(f"Input:  {ex['expression']}")
        result = calculator_tool.execute(ex)
        if result['isError']:
            print(f"Error:  {result['content'][0]['text']}")
        else:
            print(f"Output: {result['content'][0]['text']}")
        print()


def example_2_code_executor():
    """Example 2: Code Executor Tool"""
    print_section("Example 2: Code Executor Tool")
    
    examples = [
        "print('Hello, World!')",
        "x = 10; y = 20; print(f'Sum: {x + y}')",
        "for i in range(5): print(f'Number: {i}')",
        "import math; print(f'Pi: {math.pi}')",
    ]
    
    for code in examples:
        print(f"Code:\n{code}")
        result = code_executor_tool.execute({"code": code})
        print(f"Output:\n{result['content'][0]['text']}")
        print("-" * 50)


def example_3_file_tool():
    """Example 3: File Tool"""
    print_section("Example 3: File Tool")
    
    # Write a file
    print("1. Writing file...")
    result = file_tool.execute({
        "operation": "write",
        "filename": "example.txt",
        "content": "Hello from Agentic AI Platform!"
    })
    print(f"Result: {result['content'][0]['text']}")
    
    # Read the file
    print("\n2. Reading file...")
    result = file_tool.execute({
        "operation": "read",
        "filename": "example.txt"
    })
    print(f"Content: {result['content'][0]['text']}")
    
    # List files
    print("\n3. Listing files...")
    result = file_tool.execute({
        "operation": "list",
        "filename": "."
    })
    print(f"Files: {result['content'][0]['text']}")


def example_4_web_search():
    """Example 4: Web Search Tool"""
    print_section("Example 4: Web Search Tool (Mock)")
    
    queries = [
        "python programming",
        "machine learning",
        "docker containers",
    ]
    
    for query in queries:
        print(f"Query: {query}")
        result = web_search_tool.execute({"query": query, "num_results": 2})
        print(f"Results:\n{result['content'][0]['text']}")
        print("-" * 50)


def example_5_system_tool():
    """Example 5: System Tool"""
    print_section("Example 5: System Tool")
    
    info_types = ["platform", "cpu", "memory", "all"]
    
    for info_type in info_types:
        print(f"Info Type: {info_type}")
        result = system_tool.execute({"info_type": info_type})
        print(f"Output:\n{result['content'][0]['text']}")
        print("-" * 50)


def example_6_agent_execution():
    """Example 6: Full Agent Execution"""
    print_section("Example 6: Full Agent Execution")
    
    goals = [
        "Calculate 15 * 23",
        "Get system platform information",
    ]
    
    for goal in goals:
        print(f"\n🎯 Goal: {goal}")
        print("-" * 50)
        
        try:
            report = agent.run_goal(goal)
            
            print(f"✅ Success: {report.success}")
            print(f"⏱️  Time: {report.total_execution_time_ms:.0f}ms")
            print(f"📋 Steps: {len(report.results)}")
            
            for i, result in enumerate(report.results, 1):
                status = "✓" if result.success else "✗"
                print(f"  {status} Step {i}: {result.output}")
            
            print(f"\n📝 Summary: {report.reflection.summary}")
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")


def example_7_health_check():
    """Example 7: Health Check"""
    print_section("Example 7: Health Check")
    
    health = agent.health_check()
    print(f"Status: {health['status']}")
    print(f"LLM Available: {'✅' if health['llm_available'] else '❌'}")
    print(f"Memory Available: {'✅' if health['memory_available'] else '❌'}")


def example_8_list_all_tools():
    """Example 8: List All Available Tools"""
    print_section("Example 8: Available Tools")
    
    from agentic_ai.mcp_server.registry import registry
    
    tools = registry.list_tools()
    print(f"Total Tools: {len(tools)}\n")
    
    for tool in tools:
        print(f"🔧 {tool['name']}")
        print(f"   Description: {tool['description']}")
        print(f"   Schema: {json.dumps(tool['input_schema'], indent=2)}")
        print()


def run_all_examples():
    """Run all examples."""
    print("\n" + "=" * 70)
    print("  AGENTIC AI PLATFORM - EXAMPLES & TESTS")
    print("=" * 70)
    
    examples = [
        ("Calculator Tool", example_1_calculator),
        ("Code Executor", example_2_code_executor),
        ("File Tool", example_3_file_tool),
        ("Web Search", example_4_web_search),
        ("System Tool", example_5_system_tool),
        ("Health Check", example_7_health_check),
        ("List Tools", example_8_list_all_tools),
        ("Agent Execution", example_6_agent_execution),
    ]
    
    print("\nAvailable Examples:")
    for i, (name, _) in enumerate(examples, 1):
        print(f"  {i}. {name}")
    print(f"  0. Run All")
    print(f"  q. Quit")
    
    choice = input("\nSelect example (0-8, q): ").strip().lower()
    
    if choice == 'q':
        print("\nGoodbye!")
        return
    
    if choice == '0':
        for name, func in examples:
            try:
                func()
            except Exception as e:
                print(f"\n❌ Error in {name}: {str(e)}")
    elif choice.isdigit() and 1 <= int(choice) <= len(examples):
        try:
            examples[int(choice) - 1][1]()
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
    else:
        print("\nInvalid choice!")


if __name__ == "__main__":
    run_all_examples()
