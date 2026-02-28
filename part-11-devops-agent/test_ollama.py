"""
Test Ollama Connection for DevOps Monitoring Agent
===================================================

This script tests if Ollama is running and can generate responses.
"""

import requests
import json
import sys


def test_ollama_connection(url="http://localhost:11434"):
    """Test if Ollama is running"""
    print("\n" + "=" * 60)
    print("Testing Ollama Connection")
    print(f"URL: {url}")
    print("=" * 60)
    
    try:
        # Check if Ollama is running
        response = requests.get(f"{url}/api/tags", timeout=5)
        if response.status_code == 200:
            data = response.json()
            models = data.get("models", [])
            print(f"✅ Ollama is running!")
            print(f"   Available models: {len(models)}")
            for model in models:
                print(f"   - {model.get('name', 'unknown')}")
            return True
        else:
            print(f"❌ Ollama returned status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"❌ Cannot connect to Ollama at {url}")
        print("   Make sure Ollama is running: ollama serve")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_mistral_generation(url="http://localhost:11434"):
    """Test Mistral model generation"""
    print("\n" + "=" * 60)
    print("Testing Mistral Generation")
    print("=" * 60)
    
    prompt = """You are a DevOps monitoring assistant.

Given these system metrics:
- CPU: 85%
- Memory: 60%
- Disk: 70%

Respond in JSON format:
{
    "action": "Brief action description",
    "reasoning": "Why this action",
    "tool_to_use": "tool_name",
    "confidence": 0.8,
    "is_complete": false
}"""
    
    payload = {
        "model": "mistral",
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 200
        }
    }
    
    try:
        print("Sending request to Mistral...")
        response = requests.post(
            f"{url}/api/generate",
            json=payload,
            timeout=60
        )
        response.raise_for_status()
        
        result = response.json()
        generated_text = result.get("response", "")
        
        print("✅ Generation successful!")
        print(f"\n📝 Response:\n{generated_text[:500]}...")
        
        # Try to parse JSON
        try:
            if "{" in generated_text and "}" in generated_text:
                json_start = generated_text.find("{")
                json_end = generated_text.rfind("}") + 1
                json_str = generated_text[json_start:json_end]
                data = json.loads(json_str)
                print(f"\n✅ JSON parsing successful!")
                print(f"   Action: {data.get('action', 'N/A')}")
                print(f"   Tool: {data.get('tool_to_use', 'N/A')}")
        except json.JSONDecodeError:
            print("\n⚠️  Response is not valid JSON")
        
        return True
        
    except Exception as e:
        print(f"❌ Generation failed: {e}")
        return False


def test_with_agent():
    """Test using the agent with Ollama"""
    print("\n" + "=" * 60)
    print("Testing Agent with Ollama")
    print("=" * 60)
    
    try:
        from agent import DevOpsAgent
        from config import AgentConfig
        
        config = AgentConfig(
            reasoning_mode="ollama",
            max_steps=2
        )
        
        agent = DevOpsAgent(config)
        
        print(f"Reasoner mode: {agent.reasoner.mode.value}")
        
        if agent.reasoner.mode.value == "mock":
            print("⚠️  Agent fell back to MOCK mode (Ollama not available)")
            return False
        
        print("✅ Agent initialized with Ollama!")
        
        # Run a quick test
        print("\nRunning test goal...")
        result = agent.run("Check CPU usage")
        
        print(f"\n✅ Test complete!")
        print(f"   Steps: {result['execution_summary']['total_steps']}")
        print(f"   Success rate: {result['execution_summary']['success_rate_percent']}%")
        
        return True
        
    except Exception as e:
        print(f"❌ Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 OLLAMA CONNECTION TEST SUITE")
    print("=" * 60)
    
    # Get Ollama URL from environment or use default
    import os
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    
    results = []
    
    # Test 1: Connection
    results.append(("Connection", test_ollama_connection(ollama_url)))
    
    # Test 2: Generation (only if connection worked)
    if results[0][1]:
        results.append(("Generation", test_mistral_generation(ollama_url)))
        results.append(("Agent Integration", test_with_agent()))
    else:
        print("\n⚠️  Skipping generation and agent tests (Ollama not connected)")
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYou can now use Ollama with the DevOps Agent:")
        print("  from config import AgentConfig")
        print("  config = AgentConfig(reasoning_mode='ollama')")
        print("  agent = DevOpsAgent(config)")
        return 0
    else:
        print("\n⚠️  Some tests failed")
        print("\nTroubleshooting:")
        print("  1. Make sure Ollama is running: ollama serve")
        print("  2. Check if Mistral is installed: ollama list")
        print("  3. Install Mistral if needed: ollama pull mistral")
        print("\nYou can still use MOCK mode:")
        print("  config = AgentConfig(reasoning_mode='mock')")
        return 1


if __name__ == "__main__":
    sys.exit(main())
