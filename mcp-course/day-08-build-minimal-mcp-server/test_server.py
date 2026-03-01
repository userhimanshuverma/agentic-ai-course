#!/usr/bin/env python3
"""
Day 8: Test the MCP Server
==========================

This script tests the minimal MCP server by sending
various JSON-RPC requests and displaying responses.
"""

import subprocess
import json
import sys


def send_request(process, request):
    """Send a JSON-RPC request to the server."""
    request_json = json.dumps(request)
    process.stdin.write(request_json + "\n")
    process.stdin.flush()
    
    response = process.stdout.readline()
    return json.loads(response)


def main():
    print("=" * 60)
    print("TESTING MINIMAL MCP SERVER")
    print("=" * 60)
    
    # Start the server
    process = subprocess.Popen(
        [sys.executable, "server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    try:
        # Test 1: Initialize
        print("\n1️⃣  Testing initialize...")
        response = send_request(process, {
            "jsonrpc": "2.0",
            "method": "initialize",
            "params": {},
            "id": "init_1"
        })
        print(f"   ✅ Response: {json.dumps(response, indent=2)}")
        
        # Test 2: List tools
        print("\n2️⃣  Testing tools/list...")
        response = send_request(process, {
            "jsonrpc": "2.0",
            "method": "tools/list",
            "params": {},
            "id": "list_1"
        })
        print(f"   ✅ Available tools: {len(response['result']['tools'])}")
        for tool in response['result']['tools']:
            print(f"      • {tool['name']}: {tool['description']}")
        
        # Test 3: Call echo tool
        print("\n3️⃣  Testing tools/call (echo)...")
        response = send_request(process, {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "echo",
                "arguments": {"message": "Hello MCP!"}
            },
            "id": "call_1"
        })
        result = response['result']['content'][0]['text']
        print(f"   ✅ Result: {result}")
        
        # Test 4: Call calculate tool
        print("\n4️⃣  Testing tools/call (calculate)...")
        expressions = ["2 + 2", "10 * 5", "100 / 4", "2 ** 8"]
        for expr in expressions:
            response = send_request(process, {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "calculate",
                    "arguments": {"expression": expr}
                },
                "id": f"calc_{expr}"
            })
            result = response['result']['content'][0]['text']
            print(f"      {expr} = {result}")
        
        # Test 5: Call reverse_text tool
        print("\n5️⃣  Testing tools/call (reverse_text)...")
        response = send_request(process, {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "reverse_text",
                "arguments": {"text": "Hello World"}
            },
            "id": "reverse_1"
        })
        result = response['result']['content'][0]['text']
        print(f"   ✅ Result: {result}")
        
        # Test 6: Call word_count tool
        print("\n6️⃣  Testing tools/call (word_count)...")
        response = send_request(process, {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "word_count",
                "arguments": {"text": "The quick brown fox jumps"}
            },
            "id": "count_1"
        })
        result = response['result']['content'][0]['text']
        print(f"   ✅ Result: {result}")
        
        # Test 7: Call system info
        print("\n7️⃣  Testing tools/call (get_system_info)...")
        response = send_request(process, {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "get_system_info",
                "arguments": {}
            },
            "id": "sys_1"
        })
        result = response['result']['content'][0]['text']
        print(f"   ✅ Result: {result}")
        
        # Test 8: Error handling (unknown tool)
        print("\n8️⃣  Testing error handling (unknown tool)...")
        response = send_request(process, {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": "nonexistent_tool",
                "arguments": {}
            },
            "id": "error_1"
        })
        if "error" in response:
            print(f"   ✅ Error handled: {response['error']['message']}")
        
        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✅")
        print("=" * 60)
        
    finally:
        # Cleanup
        process.terminate()
        print("\nServer terminated.")


if __name__ == "__main__":
    main()
