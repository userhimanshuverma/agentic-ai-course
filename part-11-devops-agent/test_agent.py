"""
Part 11: DevOps Monitoring Agent - Test Suite
=============================================

Comprehensive tests for all agent functionality.
Run with: python test_agent.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from tools import SystemMonitor, CPUMetrics, MemoryMetrics, DiskMetrics
from reasoning import MistralReasoner, ReasoningMode, ReasoningResult
from config import AgentConfig
from agent import DevOpsAgent, StepStatus


class TestResult:
    """Test result container"""
    def __init__(self, name, passed, message=""):
        self.name = name
        self.passed = passed
        self.message = message


class DevOpsAgentTester:
    """Test suite for DevOps Monitoring Agent"""
    
    def __init__(self):
        self.results = []
        self.total = 0
        self.passed = 0
    
    def run_test(self, name, test_func):
        """Run a single test"""
        self.total += 1
        print(f"\n{'─' * 50}")
        print(f"🧪 Testing: {name}")
        print('─' * 50)
        
        try:
            result = test_func()
            self.results.append(result)
            if result.passed:
                self.passed += 1
                print(f"✅ PASS: {result.message}")
            else:
                print(f"❌ FAIL: {result.message}")
        except Exception as e:
            result = TestResult(name, False, f"Exception: {str(e)}")
            self.results.append(result)
            print(f"❌ FAIL: {str(e)}")
    
    def test_1_cpu_metrics(self):
        """Test CPU metrics collection"""
        monitor = SystemMonitor()
        cpu = monitor.get_cpu_metrics(interval=0.1)
        
        assert isinstance(cpu.percent, (int, float)), "CPU percent should be numeric"
        assert cpu.percent >= 0, "CPU percent should be non-negative"
        assert cpu.core_count > 0, "Should have at least 1 core"
        assert cpu.status in ['normal', 'warning', 'critical', 'error'], "Invalid status"
        
        return TestResult("CPU Metrics", True, f"CPU: {cpu.percent}% ({cpu.status})")
    
    def test_2_memory_metrics(self):
        """Test memory metrics collection"""
        monitor = SystemMonitor()
        mem = monitor.get_memory_metrics()
        
        assert mem.total_gb > 0, "Total memory should be positive"
        assert mem.used_gb >= 0, "Used memory should be non-negative"
        assert mem.percent >= 0 and mem.percent <= 100, "Percent should be 0-100"
        assert mem.status in ['normal', 'warning', 'critical', 'error'], "Invalid status"
        
        return TestResult("Memory Metrics", True, f"Memory: {mem.percent}% ({mem.status})")
    
    def test_3_disk_metrics(self):
        """Test disk metrics collection"""
        monitor = SystemMonitor()
        disk = monitor.get_disk_metrics()
        
        assert disk.total_gb > 0, "Total disk should be positive"
        assert disk.free_gb >= 0, "Free space should be non-negative"
        assert disk.percent >= 0 and disk.percent <= 100, "Percent should be 0-100"
        
        return TestResult("Disk Metrics", True, f"Disk: {disk.percent}% used")
    
    def test_4_all_metrics(self):
        """Test getting all metrics at once"""
        monitor = SystemMonitor()
        all_metrics = monitor.get_all_metrics()
        
        assert 'cpu' in all_metrics, "Should have CPU metrics"
        assert 'memory' in all_metrics, "Should have memory metrics"
        assert 'disk' in all_metrics, "Should have disk metrics"
        assert 'network' in all_metrics, "Should have network metrics"
        assert 'processes' in all_metrics, "Should have process metrics"
        
        return TestResult("All Metrics", True, "All 5 metric types collected")
    
    def test_5_process_metrics(self):
        """Test process metrics collection"""
        monitor = SystemMonitor()
        processes = monitor.get_process_metrics(top_n=3)
        
        assert isinstance(processes, list), "Should return a list"
        assert len(processes) <= 3, "Should respect top_n limit"
        
        if processes:
            assert 'pid' in processes[0], "Process should have PID"
            assert 'name' in processes[0], "Process should have name"
            assert 'cpu_percent' in processes[0], "Process should have CPU %"
        
        return TestResult("Process Metrics", True, f"{len(processes)} processes collected")
    
    def test_6_reasoning_mock(self):
        """Test mock reasoning engine"""
        reasoner = MistralReasoner(mode=ReasoningMode.MOCK)
        
        metrics = {
            'cpu': {'percent': 85, 'status': 'warning'},
            'memory': {'percent': 60, 'status': 'normal'}
        }
        
        result = reasoner.analyze_metrics(metrics, "Check system health")
        
        assert isinstance(result, ReasoningResult), "Should return ReasoningResult"
        assert result.action, "Should have an action"
        assert result.tool_to_use, "Should specify a tool"
        assert 0 <= result.confidence <= 1, "Confidence should be 0-1"
        
        return TestResult("Mock Reasoning", True, f"Action: {result.action}")
    
    def test_7_reasoning_suggestions(self):
        """Test fix suggestions"""
        reasoner = MistralReasoner(mode=ReasoningMode.MOCK)
        suggestions = reasoner.suggest_fix("cpu", 85, 70)
        
        assert isinstance(suggestions, list), "Should return a list"
        assert len(suggestions) > 0, "Should have suggestions"
        
        return TestResult("Fix Suggestions", True, f"{len(suggestions)} suggestions")
    
    def test_8_agent_initialization(self):
        """Test agent initialization"""
        agent = DevOpsAgent()
        
        assert agent.config is not None, "Should have config"
        assert agent.monitor is not None, "Should have monitor"
        assert agent.reasoner is not None, "Should have reasoner"
        
        return TestResult("Agent Init", True, "Agent initialized successfully")
    
    def test_9_agent_config(self):
        """Test agent with custom config"""
        config = AgentConfig(max_steps=5, reasoning_mode="mock")
        agent = DevOpsAgent(config=config)
        
        assert agent.config.max_steps == 5, "Max steps not applied"
        assert agent.config.reasoning_mode == "mock", "Reasoning mode not applied"
        
        return TestResult("Custom Config", True, "Custom config applied")
    
    def test_10_agent_run(self):
        """Test agent execution"""
        config = AgentConfig(max_steps=3, reasoning_mode="mock")
        agent = DevOpsAgent(config=config)
        
        result = agent.run("Check system health")
        
        assert 'goal' in result, "Should have goal"
        assert 'execution_summary' in result, "Should have execution summary"
        assert 'steps' in result, "Should have steps"
        assert len(result['steps']) >= 1, "Should have at least 1 step"
        
        return TestResult("Agent Run", True, f"{len(result['steps'])} steps executed")
    
    def test_11_step_status(self):
        """Test step status tracking"""
        config = AgentConfig(max_steps=2, reasoning_mode="mock")
        agent = DevOpsAgent(config=config)
        
        result = agent.run("Check CPU")
        
        for step in result['steps']:
            assert step['status'] in ['pending', 'running', 'success', 'failed', 'retrying', 'timeout'], \
                f"Invalid status: {step['status']}"
        
        return TestResult("Step Status", True, "All steps have valid status")
    
    def test_12_metrics_tracking(self):
        """Test execution metrics"""
        config = AgentConfig(max_steps=2, reasoning_mode="mock")
        agent = DevOpsAgent(config=config)
        
        result = agent.run("Check system")
        
        metrics = result['execution_summary']
        assert 'total_steps' in metrics, "Should track total steps"
        assert 'successful_steps' in metrics, "Should track successful steps"
        assert 'success_rate_percent' in metrics, "Should have success rate"
        
        return TestResult("Metrics Tracking", True, 
                         f"Success rate: {metrics['success_rate_percent']}%")
    
    def test_13_safety_limits(self):
        """Test safety limits in report"""
        config = AgentConfig(max_steps=5, max_time_seconds=60, reasoning_mode="mock")
        agent = DevOpsAgent(config=config)
        
        result = agent.run("Check system")
        
        limits = result['safety_limits']
        assert limits['max_steps'] == 5, "Max steps not in report"
        assert limits['max_time_seconds'] == 60, "Max time not in report"
        
        return TestResult("Safety Limits", True, "All limits reported")
    
    def test_14_conclusion(self):
        """Test conclusion generation"""
        config = AgentConfig(max_steps=2, reasoning_mode="mock")
        agent = DevOpsAgent(config=config)
        
        result = agent.run("Check system health")
        
        assert 'conclusion' in result, "Should have conclusion"
        assert len(result['conclusion']) > 0, "Conclusion should not be empty"
        
        return TestResult("Conclusion", True, "Conclusion generated")
    
    def run_all_tests(self):
        """Run all tests"""
        print("\n" + "=" * 60)
        print("🚀 DEVOPS MONITORING AGENT - TEST SUITE")
        print("=" * 60)
        
        # Run all tests
        self.run_test("1. CPU Metrics", self.test_1_cpu_metrics)
        self.run_test("2. Memory Metrics", self.test_2_memory_metrics)
        self.run_test("3. Disk Metrics", self.test_3_disk_metrics)
        self.run_test("4. All Metrics", self.test_4_all_metrics)
        self.run_test("5. Process Metrics", self.test_5_process_metrics)
        self.run_test("6. Mock Reasoning", self.test_6_reasoning_mock)
        self.run_test("7. Fix Suggestions", self.test_7_reasoning_suggestions)
        self.run_test("8. Agent Initialization", self.test_8_agent_initialization)
        self.run_test("9. Custom Config", self.test_9_agent_config)
        self.run_test("10. Agent Run", self.test_10_agent_run)
        self.run_test("11. Step Status", self.test_11_step_status)
        self.run_test("12. Metrics Tracking", self.test_12_metrics_tracking)
        self.run_test("13. Safety Limits", self.test_13_safety_limits)
        self.run_test("14. Conclusion", self.test_14_conclusion)
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 TEST SUMMARY")
        print("=" * 60)
        print(f"Total Tests: {self.total}")
        print(f"✅ Passed: {self.passed}")
        print(f"❌ Failed: {self.total - self.passed}")
        print(f"Success Rate: {(self.passed / self.total * 100):.1f}%")
        
        failed = [r for r in self.results if not r.passed]
        if failed:
            print("\n❌ FAILED TESTS:")
            for r in failed:
                print(f"  - {r.name}: {r.message}")
        
        print("=" * 60)
        
        return self.passed == self.total


def main():
    tester = DevOpsAgentTester()
    all_passed = tester.run_all_tests()
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {tester.total - tester.passed} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
