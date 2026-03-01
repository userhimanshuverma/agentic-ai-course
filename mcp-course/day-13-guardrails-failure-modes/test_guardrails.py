#!/usr/bin/env python3
"""
Day 13: Test Guardrails
=======================

Tests all guardrail mechanisms.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "day-09-build-mcp-client"))
from client import MCPClient


def test_input_validation(client):
    """Test dangerous input blocking."""
    print("\n🛡️  Testing Input Validation...")
    
    try:
        result = client.call_tool("calculate", {"expression": "__import__('os').system('ls')"})
        print(f"   ❌ FAIL: Dangerous code executed!")
    except Exception as e:
        print(f"   ✅ PASS: Dangerous code blocked")
    
    result = client.call_tool("calculate", {"expression": "2 + 2"})
    print(f"   ✅ PASS: Safe code works: {result}")


def test_timeout(client):
    """Test timeout protection."""
    print("\n⏱️  Testing Timeout Protection...")
    
    try:
        result = client.call_tool("slow_operation", {"delay": 5})
        print(f"   ❌ FAIL: Should have timed out!")
    except Exception as e:
        print(f"   ✅ PASS: Timeout works")


def test_rate_limit(client):
    """Test rate limiting."""
    print("\n🚦 Testing Rate Limiting...")
    
    success = 0
    limited = 0
    
    for i in range(15):
        try:
            client.call_tool("calculate", {"expression": f"{i} + 1"})
            success += 1
        except Exception as e:
            if "Rate limit" in str(e):
                limited += 1
    
    print(f"   Success: {success}, Rate Limited: {limited}")
    if limited > 0:
        print(f"   ✅ PASS: Rate limiting works!")


def main():
    print("=" * 70)
    print("GUARDRAILS TESTING")
    print("=" * 70)
    
    server_path = os.path.join(os.path.dirname(__file__), "server.py")
    client = MCPClient(["python", server_path])
    
    try:
        client.connect()
        
        test_input_validation(client)
        test_timeout(client)
        test_rate_limit(client)
        
    finally:
        client.disconnect()
    
    print("\n" + "=" * 70)
    print("Testing complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
