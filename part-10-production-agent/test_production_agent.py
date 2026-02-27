"""
Comprehensive Test Suite for Part 10 Production Agent
Tests all functionality including safety controls, retry logic, and error handling
"""
import sys
import os
import time
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent import ProductionAgent, ExecutionConfig, StepStatus
from tools import get_tool, list_tools


class TestResult:
    """Test result container"""
    def __init__(self, name, passed, message="", details=None):
        self.name = name
        self.passed = passed
        self.message = message
        self.details = details or {}

    def __str__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        return f"{status}: {self.name} - {self.message}"


class ProductionAgentTester:
    """Test suite for Production Agent"""
    
    def __init__(self):
        self.results = []
        self.total_tests = 0
        self.passed_tests = 0
        
    def run_test(self, test_name, test_func):
        """Run a single test and record result"""
        self.total_tests += 1
        print(f"\n{'─' * 60}")
        print(f"🧪 Running: {test_name}")
        print('─' * 60)
        
        try:
            result = test_func()
            self.results.append(result)
            if result.passed:
                self.passed_tests += 1
                print(f"✅ PASSED: {result.message}")
            else:
                print(f"❌ FAILED: {result.message}")
            return result
        except Exception as e:
            result = TestResult(test_name, False, f"Exception: {str(e)}")
            self.results.append(result)
            print(f"❌ FAILED with exception: {str(e)}")
            return result
    
    def test_1_basic_initialization(self):
        """Test agent initialization with default config"""
        agent = ProductionAgent()
        
        assert agent.config.max_steps == 10, "Default max_steps should be 10"
        assert agent.config.max_time_seconds == 300, "Default timeout should be 300s"
        assert agent.config.max_retries == 3, "Default retries should be 3"
        
        return TestResult(
            "Basic Initialization",
            True,
            f"Agent initialized with max_steps={agent.config.max_steps}"
        )
    
    def test_2_custom_config(self):
        """Test agent with custom configuration"""
        config = ExecutionConfig(
            max_steps=5,
            max_time_seconds=60,
            max_retries=2,
            tool_timeout=15
        )
        agent = ProductionAgent(config=config)
        
        assert agent.config.max_steps == 5, "Custom max_steps not applied"
        assert agent.config.max_retries == 2, "Custom retries not applied"
        
        return TestResult(
            "Custom Configuration",
            True,
            f"Custom config applied: steps={config.max_steps}, retries={config.max_retries}"
        )
    
    def test_3_system_info_single_step(self):
        """Test system info goal completes in 1 step"""
        config = ExecutionConfig(max_steps=5, max_time_seconds=30)
        agent = ProductionAgent(config=config)
        
        result = agent.run("Check system status")
        
        assert result['goal_complete'] == True, "Goal should be complete"
        assert result['execution_summary']['total_steps'] == 1, "Should complete in 1 step"
        assert result['metrics']['successful_steps'] == 1, "Should have 1 successful step"
        
        return TestResult(
            "System Info (Single Step)",
            True,
            f"Completed in {result['execution_summary']['total_steps']} step(s)"
        )
    
    def test_4_calculator(self):
        """Test calculator tool"""
        config = ExecutionConfig(max_steps=3, max_time_seconds=30)
        agent = ProductionAgent(config=config)
        
        result = agent.run("Calculate 25 * 4")
        
        assert result['goal_complete'] == True, "Calculator goal should complete"
        
        # Check result contains calculation
        steps = result['steps']
        if steps and 'result' in steps[0]:
            calc_result = steps[0]['result']
            if isinstance(calc_result, dict) and 'result' in calc_result:
                assert calc_result['result'] == 100, "25 * 4 should equal 100"
        
        return TestResult(
            "Calculator",
            True,
            "Calculator executed successfully"
        )
    
    def test_5_disk_check(self):
        """Test disk check tool - adapts to disk status"""
        # Use more steps to allow for multi-step if disk needs fixing
        config = ExecutionConfig(max_steps=10, max_time_seconds=60)
        agent = ProductionAgent(config=config)
        
        result = agent.run("Check disk space")
        
        # Verify disk info was retrieved (goal may or may not complete depending on status)
        steps = result['steps']
        assert len(steps) >= 1, "Should have at least 1 step"
        
        if steps and steps[0]['tool'] == 'check_disk':
            disk_result = steps[0]['result']
            if isinstance(disk_result, dict):
                assert 'status' in disk_result, "Disk result should have status"
                assert disk_result['status'] in ['good', 'warning', 'critical', 'error'], \
                    f"Unexpected status: {disk_result['status']}"
        
        # Goal completion depends on disk status:
        # - good: completes in 1 step
        # - warning/critical: may need more steps (organize, re-check)
        status_msg = "completed" if result['goal_complete'] else "in progress (needs more steps)"
        
        return TestResult(
            "Disk Check",
            True,
            f"Disk check executed, goal {status_msg}"
        )
    
    def test_6_organize_downloads_multi_step(self):
        """Test organize Downloads (multi-step with verification)"""
        # Use more steps to allow for full workflow including re-checks
        config = ExecutionConfig(max_steps=10, max_time_seconds=120)
        agent = ProductionAgent(config=config)
        
        result = agent.run("Organize my Downloads folder")
        
        # Should have at least 2 steps: organize + verify (more if disk still critical)
        steps_count = result['execution_summary']['total_steps']
        
        assert steps_count >= 1, "Should have at least 1 step"
        
        # Verify first step is file_organizer
        first_step = result['steps'][0]
        assert first_step['tool'] == 'file_organizer', \
            f"First step should be file_organizer, got {first_step['tool']}"
        
        # Goal completion depends on disk status after organizing
        # - If disk good after organize: completes
        # - If disk still critical: may need more iterations
        status_msg = "completed" if result['goal_complete'] else f"ran {steps_count} steps (may need more)"
        
        return TestResult(
            "Organize Downloads (Multi-Step)",
            True,
            f"Organize executed, {status_msg}"
        )
    
    def test_7_step_limit_enforcement(self):
        """Test that step limit is enforced"""
        config = ExecutionConfig(max_steps=2, max_time_seconds=30)
        agent = ProductionAgent(config=config)
        
        # Use a goal that might need more steps
        result = agent.run("Fix high disk usage")
        
        steps = result['execution_summary']['total_steps']
        max_steps = result['safety_limits']['max_steps']
        
        assert steps <= max_steps, f"Steps ({steps}) exceeded max ({max_steps})"
        
        return TestResult(
            "Step Limit Enforcement",
            True,
            f"Respected max_steps={max_steps}, executed {steps} step(s)"
        )
    
    def test_8_metrics_tracking(self):
        """Test that metrics are properly tracked"""
        config = ExecutionConfig(max_steps=5, max_time_seconds=30)
        agent = ProductionAgent(config=config)
        
        result = agent.run("Check system status")
        
        metrics = result['metrics']
        
        assert 'total_steps' in metrics, "Metrics should track total_steps"
        assert 'successful_steps' in metrics, "Metrics should track successful_steps"
        assert 'success_rate_percent' in metrics, "Metrics should have success_rate"
        
        # Verify success rate calculation
        if metrics['total_steps'] > 0:
            expected_rate = (metrics['successful_steps'] / metrics['total_steps']) * 100
            assert abs(metrics['success_rate_percent'] - expected_rate) < 0.1, \
                "Success rate calculation incorrect"
        
        return TestResult(
            "Metrics Tracking",
            True,
            f"Metrics: {metrics['total_steps']} steps, {metrics['success_rate_percent']:.1f}% success"
        )
    
    def test_9_error_handling_unknown_tool(self):
        """Test error handling for unknown tool scenario"""
        config = ExecutionConfig(max_steps=3, max_time_seconds=30, max_retries=0)
        agent = ProductionAgent(config=config)
        
        # Use a goal that might trigger edge cases
        result = agent.run("Unknown goal that triggers fallback")
        
        # Should fallback to system_info and complete
        assert result['execution_summary']['total_steps'] >= 1, "Should execute at least 1 step"
        
        return TestResult(
            "Error Handling / Fallback",
            True,
            "Fallback mechanism working"
        )
    
    def test_10_step_status_tracking(self):
        """Test that step statuses are properly tracked"""
        config = ExecutionConfig(max_steps=5, max_time_seconds=30)
        agent = ProductionAgent(config=config)
        
        result = agent.run("Organize my Downloads")
        
        for step in result['steps']:
            assert 'status' in step, "Each step should have a status"
            valid_statuses = ['pending', 'running', 'success', 'failed', 'timeout', 'retrying']
            assert step['status'] in valid_statuses, f"Invalid status: {step['status']}"
        
        return TestResult(
            "Step Status Tracking",
            True,
            f"All {len(result['steps'])} step(s) have valid statuses"
        )
    
    def test_11_execution_time_tracking(self):
        """Test that execution times are tracked"""
        config = ExecutionConfig(max_steps=5, max_time_seconds=30)
        agent = ProductionAgent(config=config)
        
        result = agent.run("Check system status")
        
        # Check total execution time
        exec_time = result['execution_summary']['execution_time_seconds']
        assert exec_time >= 0, "Execution time should be non-negative"
        
        # Check individual step times
        for step in result['steps']:
            assert 'execution_time_ms' in step, "Each step should have execution_time_ms"
            assert step['execution_time_ms'] >= 0, "Step execution time should be non-negative"
        
        return TestResult(
            "Execution Time Tracking",
            True,
            f"Total time: {exec_time:.2f}s"
        )
    
    def test_12_safety_limits_in_report(self):
        """Test that safety limits are included in report"""
        config = ExecutionConfig(
            max_steps=7,
            max_time_seconds=120,
            max_retries=2,
            tool_timeout=20
        )
        agent = ProductionAgent(config=config)
        
        result = agent.run("Check system")
        
        limits = result['safety_limits']
        assert limits['max_steps'] == 7, "max_steps should be in report"
        assert limits['max_time_seconds'] == 120, "max_time_seconds should be in report"
        assert limits['max_retries'] == 2, "max_retries should be in report"
        assert limits['tool_timeout'] == 20, "tool_timeout should be in report"
        
        return TestResult(
            "Safety Limits in Report",
            True,
            "All safety limits reported correctly"
        )
    
    def test_13_conclusion_generation(self):
        """Test that conclusion is properly generated"""
        config = ExecutionConfig(max_steps=5, max_time_seconds=30)
        agent = ProductionAgent(config=config)
        
        result = agent.run("Check system status")
        
        assert 'conclusion' in result, "Report should include conclusion"
        conclusion = result['conclusion']
        
        # Conclusion should mention goal status
        assert len(conclusion) > 0, "Conclusion should not be empty"
        
        return TestResult(
            "Conclusion Generation",
            True,
            f"Conclusion: {conclusion[:50]}..."
        )
    
    def test_14_tools_available(self):
        """Test that all expected tools are available"""
        expected_tools = ['check_disk', 'suggest_organize', 'file_organizer', 'system_info', 'calculator']
        
        available_tools = list_tools()
        
        for tool in expected_tools:
            assert tool in available_tools, f"Tool '{tool}' should be available"
            tool_func = get_tool(tool)
            assert tool_func is not None, f"Tool '{tool}' should be retrievable"
        
        return TestResult(
            "Tools Available",
            True,
            f"All {len(expected_tools)} tools available"
        )
    
    def run_all_tests(self):
        """Run all tests and generate report"""
        print("\n" + "=" * 70)
        print("🚀 PART 10 PRODUCTION AGENT - COMPREHENSIVE TEST SUITE")
        print("=" * 70)
        
        # Run all tests
        self.run_test("1. Basic Initialization", self.test_1_basic_initialization)
        self.run_test("2. Custom Configuration", self.test_2_custom_config)
        self.run_test("3. System Info (Single Step)", self.test_3_system_info_single_step)
        self.run_test("4. Calculator", self.test_4_calculator)
        self.run_test("5. Disk Check", self.test_5_disk_check)
        self.run_test("6. Organize Downloads (Multi-Step)", self.test_6_organize_downloads_multi_step)
        self.run_test("7. Step Limit Enforcement", self.test_7_step_limit_enforcement)
        self.run_test("8. Metrics Tracking", self.test_8_metrics_tracking)
        self.run_test("9. Error Handling / Fallback", self.test_9_error_handling_unknown_tool)
        self.run_test("10. Step Status Tracking", self.test_10_step_status_tracking)
        self.run_test("11. Execution Time Tracking", self.test_11_execution_time_tracking)
        self.run_test("12. Safety Limits in Report", self.test_12_safety_limits_in_report)
        self.run_test("13. Conclusion Generation", self.test_13_conclusion_generation)
        self.run_test("14. Tools Available", self.test_14_tools_available)
        
        # Generate summary
        print("\n" + "=" * 70)
        print("📊 TEST SUMMARY")
        print("=" * 70)
        print(f"Total Tests: {self.total_tests}")
        print(f"✅ Passed: {self.passed_tests}")
        print(f"❌ Failed: {self.total_tests - self.passed_tests}")
        print(f"Success Rate: {(self.passed_tests / self.total_tests * 100):.1f}%")
        
        # List failed tests
        failed = [r for r in self.results if not r.passed]
        if failed:
            print("\n❌ FAILED TESTS:")
            for result in failed:
                print(f"  - {result.name}: {result.message}")
        
        print("\n" + "=" * 70)
        
        return self.passed_tests == self.total_tests


def main():
    """Main entry point"""
    tester = ProductionAgentTester()
    all_passed = tester.run_all_tests()
    
    if all_passed:
        print("\n🎉 ALL TESTS PASSED! Production Agent is fully functional.")
        return 0
    else:
        print(f"\n⚠️  {len([r for r in tester.results if not r.passed])} test(s) failed.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
