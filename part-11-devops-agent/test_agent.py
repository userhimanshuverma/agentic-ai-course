"""Simple tests for DevOps Agent"""

from tools import SystemMonitor
from reasoning import AIReasoner
from config import Config
from agent import DevOpsAgent


def test_tools():
    """Test monitoring tools"""
    print("\n1. Testing Tools")
    m = SystemMonitor()
    
    cpu = m.get_cpu_metrics()
    print(f"   CPU: {cpu.percent}%")
    
    mem = m.get_memory_metrics()
    print(f"   Memory: {mem.percent}%")
    
    disk = m.get_disk_metrics()
    print(f"   Disk: {disk.percent}%")
    
    print("   ✅ Tools working")


def test_ai():
    """Test AI reasoning"""
    print("\n2. Testing AI Reasoning")
    ai = AIReasoner()
    
    metrics = {
        "cpu": {"percent": 85, "status": "warning"},
        "memory": {"percent": 60, "status": "normal"}
    }
    
    result = ai.analyze(metrics, "Check system")
    print(f"   Action: {result.action}")
    print(f"   Tool: {result.tool_to_use}")
    print("   ✅ AI responding")


def test_agent():
    """Test full agent"""
    print("\n3. Testing Agent")
    config = Config(max_steps=2)
    agent = DevOpsAgent(config)
    
    result = agent.run("Check CPU")
    print(f"   Steps: {result['steps']}")
    print(f"   Complete: {result['complete']}")
    print("   ✅ Agent working")


def main():
    print("=" * 50)
    print("🧪 DevOps Agent Tests")
    print("=" * 50)
    
    try:
        test_tools()
        test_ai()
        test_agent()
        print("\n" + "=" * 50)
        print("🎉 All tests passed!")
        print("=" * 50)
    except Exception as e:
        print(f"\n❌ Test failed: {e}")


if __name__ == "__main__":
    main()
