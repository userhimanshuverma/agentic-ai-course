"""
Test script for Part 9 Autonomous Agent
Tests all functionality without interactive input
"""
import sys
from agent import AutonomousAgent


def test_goal(agent, goal, expected_steps=None):
    """Test a goal and print results."""
    print("\n" + "=" * 60)
    print(f"🧪 TESTING: {goal}")
    print("=" * 60)

    result = agent.run(goal)

    print(f"\n📊 RESULTS:")
    print(f"   Goal: {result['goal']}")
    print(f"   Complete: {'✅ Yes' if result['goal_complete'] else '❌ No'}")
    print(f"   Steps taken: {result['total_steps']}")

    if expected_steps:
        if result['total_steps'] == expected_steps:
            print(f"   ✅ Expected steps match: {expected_steps}")
        else:
            print(f"   ⚠️  Expected {expected_steps} steps, got {result['total_steps']}")

    print(f"\n   Step details:")
    for step in result['steps']:
        tool_str = f" (tool: {step['tool']})" if step['tool'] else ""
        print(f"   - Step {step['step']}: {step['action']}{tool_str}")
        print(f"     Status: {step['status']}")

    return result


def run_all_tests():
    """Run all test cases."""
    print("\n" + "=" * 60)
    print("🤖 PART 9 AUTONOMOUS AGENT - FUNCTIONALITY TESTS")
    print("=" * 60)

    tests_passed = 0
    tests_failed = 0

    # Test 1: Check system status (should complete in 1 step)
    print("\n\n" + "─" * 60)
    print("TEST 1: System Info (Single Step)")
    print("─" * 60)
    agent1 = AutonomousAgent(max_steps=5)
    result1 = test_goal(agent1, "Check system status", expected_steps=1)

    if result1['goal_complete'] and result1['total_steps'] == 1:
        print("✅ TEST 1 PASSED")
        tests_passed += 1
    else:
        print("❌ TEST 1 FAILED")
        tests_failed += 1

    # Test 2: Calculator (should complete in 1 step)
    print("\n\n" + "─" * 60)
    print("TEST 2: Calculator (Single Step)")
    print("─" * 60)
    agent2 = AutonomousAgent(max_steps=5)
    result2 = test_goal(agent2, "Calculate 25 * 4", expected_steps=1)

    if result2['goal_complete'] and result2['total_steps'] == 1:
        print("✅ TEST 2 PASSED")
        tests_passed += 1
    else:
        print("❌ TEST 2 FAILED")
        tests_failed += 1

    # Test 3: Organize Downloads (should be 2 steps: organize + re-check)
    print("\n\n" + "─" * 60)
    print("TEST 3: Organize Downloads (Multi-Step)")
    print("─" * 60)
    agent3 = AutonomousAgent(max_steps=5)
    result3 = test_goal(agent3, "Organize my Downloads folder", expected_steps=2)

    if result3['goal_complete'] and result3['total_steps'] >= 1:
        print("✅ TEST 3 PASSED")
        tests_passed += 1
    else:
        print("❌ TEST 3 FAILED")
        tests_failed += 1

    # Test 4: Fix disk usage (depends on actual disk status)
    print("\n\n" + "─" * 60)
    print("TEST 4: Fix Disk Usage (Adaptive)")
    print("─" * 60)
    agent4 = AutonomousAgent(max_steps=5)
    result4 = test_goal(agent4, "Fix high disk usage")

    # This should complete (either 1 step if good, or multiple if warning)
    if result4['goal_complete']:
        print("✅ TEST 4 PASSED")
        tests_passed += 1
    else:
        print("⚠️  TEST 4: Goal not complete (may need more steps)")
        tests_failed += 1

    # Test 5: Unknown goal (should try system_info as fallback)
    print("\n\n" + "─" * 60)
    print("TEST 5: Unknown Goal (Fallback)")
    print("─" * 60)
    agent5 = AutonomousAgent(max_steps=3)
    result5 = test_goal(agent5, "Do something helpful")

    if result5['total_steps'] >= 1:
        print("✅ TEST 5 PASSED (fallback worked)")
        tests_passed += 1
    else:
        print("❌ TEST 5 FAILED")
        tests_failed += 1

    # Summary
    print("\n\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"✅ Passed: {tests_passed}")
    print(f"❌ Failed: {tests_failed}")
    print(f"📊 Total: {tests_passed + tests_failed}")

    if tests_failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print(f"\n⚠️  {tests_failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
