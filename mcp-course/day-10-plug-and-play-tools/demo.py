#!/usr/bin/env python3
"""
Day 10: Plug-and-Play Tools Demo
================================

Demonstrates how new tools are automatically discovered.
"""

import sys
import os

# Add parent directory to path for client import
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "day-09-build-mcp-client"))

from client import MCPClient


def main():
    print("=" * 70)
    print("PLUG-AND-PLAY TOOLS DEMO")
    print("=" * 70)
    
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    client = MCPClient(["python", server_path])
    
    try:
        print("\n1️⃣  Connecting to server...")
        client.connect()
        
        print("\n2️⃣  All available tools (auto-discovered):")
        print("-" * 70)
        for tool in client.list_tools():
            print(f"   • {tool['name']}: {tool['description']}")
        
        # Calculator tools
        print("\n3️⃣  Calculator tools:")
        print("-" * 70)
        
        result = client.call_tool("add", {"a": 10, "b": 5})
        print(f"   10 + 5 = {result}")
        
        result = client.call_tool("multiply", {"a": 7, "b": 8})
        print(f"   7 * 8 = {result}")
        
        result = client.call_tool("power", {"a": 2, "b": 10})
        print(f"   2^10 = {result}")
        
        # String tools
        print("\n4️⃣  String tools:")
        print("-" * 70)
        
        result = client.call_tool("uppercase", {"text": "hello world"})
        print(f"   uppercase('hello world') = {result}")
        
        result = client.call_tool("title_case", {"text": "hello world"})
        print(f"   title_case('hello world') = {result}")
        
        result = client.call_tool("count_chars", {"text": "The quick brown fox"})
        print(f"   count_chars('The quick brown fox') = {result}")
        
        # List tools
        print("\n5️⃣  List tools:")
        print("-" * 70)
        
        result = client.call_tool("sort_list", {"items": ["cherry", "apple", "banana"]})
        print(f"   sort(['cherry', 'apple', 'banana']) = {result}")
        
        result = client.call_tool("unique_items", {"items": ["a", "b", "a", "c", "b"]})
        print(f"   unique(['a', 'b', 'a', 'c', 'b']) = {result}")
        
        # Date/Time tools
        print("\n6️⃣  Date/Time tools:")
        print("-" * 70)
        
        result = client.call_tool("get_date", {})
        print(f"   Current date: {result}")
        
        result = client.call_tool("get_time", {})
        print(f"   Current time: {result}")
        
    finally:
        client.disconnect()
    
    print("\n" + "=" * 70)
    print("Demo complete!")
    print("=" * 70)
    print("""
🎯 To add a new tool:

   1. Open server.py
   2. Add a new function with @register_tool decorator:
   
      @register_tool("my_tool", "Description")
      def my_tool(param1, param2):
          return result
   
   3. Restart the server
   4. Client automatically discovers it!

✨ No client changes needed!
""")


if __name__ == "__main__":
    main()
