"""
Production-Grade Autonomous Agent
Goal-Driven • Safe • Self-Healing • Observable

Features:
- Retry logic with exponential backoff
- Timeout control for all operations
- Comprehensive error handling
- Execution logging
- Step and time limits
- Recovery strategies
"""
import json
import time
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
from tools import get_tool, list_tools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of a reasoning step."""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    TIMEOUT = "timeout"


class ExecutionError(Exception):
    """Custom exception for execution errors."""
    pass


@dataclass
class ExecutionConfig:
    """Configuration for safe execution."""
    max_steps: int = 10
    max_time_seconds: int = 300  # 5 minutes
    max_retries: int = 3
    retry_delay_base: float = 1.0  # Base delay for exponential backoff
    tool_timeout: int = 30  # Timeout for individual tool calls
    log_level: str = "INFO"


@dataclass
class ReasoningStep:
    """Represents a single step in the reasoning process."""
    step_number: int
    action: str
    tool: Optional[str] = None
    params: Dict = field(default_factory=dict)
    result: Any = None
    status: StepStatus = StepStatus.PENDING
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: float = 0.0
    retry_count: int = 0
    error_message: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "step": self.step_number,
            "action": self.action,
            "tool": self.tool,
            "params": self.params,
            "result": self.result,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "execution_time_ms": self.execution_time_ms,
            "retry_count": self.retry_count,
            "error_message": self.error_message
        }


@dataclass
class ExecutionMetrics:
    """Metrics for execution monitoring."""
    total_steps: int = 0
    successful_steps: int = 0
    failed_steps: int = 0
    retried_steps: int = 0
    total_execution_time_ms: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None

    @property
    def success_rate(self) -> float:
        if self.total_steps == 0:
            return 0.0
        return (self.successful_steps / self.total_steps) * 100

    def to_dict(self) -> dict:
        return {
            "total_steps": self.total_steps,
            "successful_steps": self.successful_steps,
            "failed_steps": self.failed_steps,
            "retried_steps": self.retried_steps,
            "success_rate_percent": round(self.success_rate, 2),
            "total_execution_time_ms": round(self.total_execution_time_ms, 2),
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None
        }


class ProductionAgent:
    """
    Production-grade autonomous agent with safety controls.
    
    Features:
    - Goal-driven autonomy (loop until goal complete)
    - Safety controls (step limits, timeouts, retries)
    - Multi-step reasoning with recovery
    - Comprehensive logging and metrics
    """

    def __init__(self, config: Optional[ExecutionConfig] = None):
        self.config = config or ExecutionConfig()
        self.steps: List[ReasoningStep] = []
        self.goal: Optional[str] = None
        self.goal_complete = False
        self.metrics = ExecutionMetrics()
        self._setup_logging()

    def _setup_logging(self):
        """Configure logging level."""
        logger.setLevel(getattr(logging, self.config.log_level.upper()))

    def _check_timeout(self) -> bool:
        """Check if execution has exceeded time limit."""
        if self.metrics.start_time is None:
            return False
        
        elapsed = (datetime.now() - self.metrics.start_time).total_seconds()
        return elapsed > self.config.max_time_seconds

    def _execute_with_timeout(self, tool: Callable, params: Dict, timeout: int) -> Any:
        """
        Execute a tool with timeout protection.
        
        Note: This is a simplified timeout. For production,
        use concurrent.futures or multiprocessing for true timeout.
        """
        import signal
        
        def timeout_handler(signum, frame):
            raise TimeoutError(f"Tool execution exceeded {timeout} seconds")

        # Set timeout (Unix only - Windows needs different approach)
        try:
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(timeout)
        except AttributeError:
            # Windows doesn't support SIGALRM, use simple timing
            start = time.time()
            result = tool(**params)
            elapsed = time.time() - start
            if elapsed > timeout:
                raise TimeoutError(f"Tool execution exceeded {timeout} seconds")
            return result

        try:
            result = tool(**params)
            signal.alarm(0)  # Cancel timeout
            return result
        except TimeoutError:
            raise
        except Exception as e:
            signal.alarm(0)  # Cancel timeout
            raise e

    def _execute_with_retry(self, step: ReasoningStep) -> Any:
        """
        Execute a step with retry logic and exponential backoff.
        """
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            step.retry_count = attempt
            
            if attempt > 0:
                step.status = StepStatus.RETRYING
                # Exponential backoff: 1s, 2s, 4s...
                delay = self.config.retry_delay_base * (2 ** (attempt - 1))
                logger.info(f"Retrying step {step.step_number} (attempt {attempt + 1}/{self.config.max_retries + 1}) after {delay}s delay")
                time.sleep(delay)
            
            try:
                step.status = StepStatus.RUNNING
                start_time = time.time()
                
                # Get and execute tool
                tool = get_tool(step.tool)
                if tool is None:
                    raise ExecutionError(f"Tool '{step.tool}' not found")
                
                # Execute with timeout
                result = self._execute_with_timeout(
                    tool, 
                    step.params, 
                    self.config.tool_timeout
                )
                
                step.execution_time_ms = (time.time() - start_time) * 1000
                step.status = StepStatus.SUCCESS
                
                logger.info(f"Step {step.step_number} succeeded in {step.execution_time_ms:.2f}ms")
                return result
                
            except TimeoutError as e:
                last_exception = e
                step.status = StepStatus.TIMEOUT
                step.error_message = f"Timeout: {str(e)}"
                logger.warning(f"Step {step.step_number} timed out (attempt {attempt + 1})")
                
            except Exception as e:
                last_exception = e
                step.status = StepStatus.FAILED
                step.error_message = str(e)
                logger.error(f"Step {step.step_number} failed (attempt {attempt + 1}): {str(e)}")
        
        # All retries exhausted
        raise ExecutionError(f"Step failed after {self.config.max_retries + 1} attempts: {last_exception}")

    def plan(self, goal: str, previous_results: List[dict] = None) -> ReasoningStep:
        """
        Plan the next step based on goal and previous results.
        Enhanced with error recovery logic.
        """
        step_number = len(self.steps) + 1
        goal_lower = goal.lower()
        
        # Check if previous step failed and needs recovery
        if previous_results and len(previous_results) > 0:
            last_result = previous_results[-1]
            
            # Recovery: If last tool failed, try alternative approach
            if last_result.get("status") in ["failed", "timeout"]:
                logger.info(f"Planning recovery for failed step {step_number - 1}")
                return self._plan_recovery(step_number, last_result)
            
            # Continue normal flow based on last successful result
            return self._plan_continuation(step_number, goal, last_result)
        
        # Initial planning
        return self._plan_initial(step_number, goal_lower)

    def _plan_recovery(self, step_number: int, last_result: dict) -> ReasoningStep:
        """Plan a recovery step after failure."""
        failed_tool = last_result.get("tool")
        
        # Recovery strategies
        if failed_tool == "file_organizer":
            return ReasoningStep(
                step_number=step_number,
                action="Recovery: Try organizing with alternative folder",
                tool="suggest_organize",
                params={}
            )
        elif failed_tool == "check_disk":
            return ReasoningStep(
                step_number=step_number,
                action="Recovery: Try system info instead of disk check",
                tool="system_info",
                params={}
            )
        else:
            return ReasoningStep(
                step_number=step_number,
                action="Recovery: Gather basic system info",
                tool="system_info",
                params={}
            )

    def _plan_continuation(self, step_number: int, goal: str, last_result: dict) -> ReasoningStep:
        """Plan continuation based on last successful result."""
        last_tool = last_result.get("tool")
        result_data = last_result.get("result", {})
        
        # Disk check flow
        if last_tool == "check_disk":
            status = result_data.get("status")
            if status in ["warning", "critical"]:
                return ReasoningStep(
                    step_number=step_number,
                    action=f"Disk status is {status}. Identify large folders to organize.",
                    tool="suggest_organize",
                    params={}
                )
            else:
                return ReasoningStep(
                    step_number=step_number,
                    action="Disk is healthy. Goal achieved.",
                    tool=None,
                    params={}
                )
        
        # After suggesting folders, organize the largest
        if last_tool == "suggest_organize":
            suggestions = result_data.get("suggestions", [])
            if suggestions:
                target = suggestions[0]
                return ReasoningStep(
                    step_number=step_number,
                    action=f"Organize files in {target['folder']} ({target['size_mb']} MB)",
                    tool="file_organizer",
                    params={"folder_path": target["path"]}
                )
            else:
                return ReasoningStep(
                    step_number=step_number,
                    action="No large folders found. Checking disk status.",
                    tool="check_disk",
                    params={}
                )
        
        # After organizing, verify with disk check
        if last_tool == "file_organizer":
            return ReasoningStep(
                step_number=step_number,
                action="Files organized. Re-checking disk usage to verify improvement.",
                tool="check_disk",
                params={}
            )
        
        # Default: goal complete
        return ReasoningStep(
            step_number=step_number,
            action="Goal achieved. No further action needed.",
            tool=None,
            params={}
        )

    def _plan_initial(self, step_number: int, goal_lower: str) -> ReasoningStep:
        """Plan initial step based on goal keywords."""
        import re
        
        # Disk-related goals
        if any(word in goal_lower for word in ["disk", "space", "storage", "full", "cleanup"]):
            return ReasoningStep(
                step_number=step_number,
                action="Check current disk usage to assess the situation.",
                tool="check_disk",
                params={}
            )
        
        # Organization goals
        elif any(word in goal_lower for word in ["organize", "clean", "sort", "tidy"]):
            match = re.search(r'(?:in|at|folder)\s+([\w/\\~]+)', goal_lower)
            folder = match.group(1) if match else "~/Downloads"
            return ReasoningStep(
                step_number=step_number,
                action=f"Organize files in {folder} by type.",
                tool="file_organizer",
                params={"folder_path": folder}
            )
        
        # System info goals
        elif any(word in goal_lower for word in ["system", "info", "status", "about"]):
            return ReasoningStep(
                step_number=step_number,
                action="Gather system information.",
                tool="system_info",
                params={}
            )
        
        # Math goals
        elif any(word in goal_lower for word in ["calculate", "compute", "math"]):
            expression = re.findall(r'[0-9+\-*/().]+', goal_lower)
            if expression:
                expr = "".join(expression)
                return ReasoningStep(
                    step_number=step_number,
                    action=f"Calculate: {expr}",
                    tool="calculator",
                    params={"expression": expr}
                )
        
        # Default fallback
        return ReasoningStep(
            step_number=step_number,
            action="Gather basic system information to understand context.",
            tool="system_info",
            params={}
        )

    def act(self, step: ReasoningStep) -> dict:
        """
        Execute the planned step with retry and timeout protection.
        """
        if step.tool is None:
            # No tool needed, just a conclusion
            step.status = StepStatus.SUCCESS
            step.result = {"message": "Goal achieved", "complete": True}
            logger.info(f"Step {step.step_number}: Goal conclusion reached")
            return step.result
        
        try:
            result = self._execute_with_retry(step)
            step.result = result
            return result
        except ExecutionError as e:
            step.result = {"error": str(e), "complete": False}
            logger.error(f"Step {step.step_number} failed permanently: {str(e)}")
            return step.result

    def observe(self, step: ReasoningStep) -> bool:
        """
        Observe the result and determine if goal is complete.
        Enhanced with comprehensive completion detection.
        """
        result = step.result
        
        if result is None:
            return False
        
        # Check for explicit completion flag
        if isinstance(result, dict):
            if result.get("complete") is True:
                return True
            
            # Tool-specific completion logic
            if step.tool == "check_disk":
                status = result.get("status")
                # Complete if healthy (either initially or after fixes)
                if status == "good":
                    return True
                # Not complete if warning/critical (needs action)
                return False
            
            if step.tool == "file_organizer":
                # Complete if successful (will verify in next step)
                if "error" not in result:
                    return False  # Will re-check disk
                return True  # Failed, stop here
            
            if step.tool in ["system_info", "calculator"]:
                # One-time operations are complete after execution
                return True
            
            if step.tool == "suggest_organize":
                # Not complete - need to act on suggestions
                return False
        
        return False

    def run(self, goal: str) -> dict:
        """
        Run the production-grade autonomous reasoning loop.
        
        while not goal_complete and step < max_steps and not timeout:
            plan()
            act() with retry and timeout
            observe()
        """
        self.goal = goal
        self.steps = []
        self.goal_complete = False
        self.metrics = ExecutionMetrics()
        self.metrics.start_time = datetime.now()
        
        logger.info("=" * 60)
        logger.info("Production Agent Starting")
        logger.info("=" * 60)
        logger.info(f"Goal: {goal}")
        logger.info(f"Config: max_steps={self.config.max_steps}, max_time={self.config.max_time_seconds}s")
        
        print("\n" + "=" * 60)
        print("🚀 Production Autonomous Agent")
        print("=" * 60)
        print(f"\n🎯 Goal: {goal}")
        print(f"⚙️  Safety Limits: {self.config.max_steps} steps, {self.config.max_time_seconds}s timeout")
        print(f"🔧 Retry Policy: {self.config.max_retries} retries with exponential backoff")
        print("\n" + "─" * 60)
        
        previous_results = []
        
        for iteration in range(self.config.max_steps):
            # Check time limit
            if self._check_timeout():
                logger.warning(f"Execution timeout after {self.config.max_time_seconds}s")
                print(f"\n⏱️  TIMEOUT: Exceeded {self.config.max_time_seconds} seconds")
                break
            
            print(f"\n🔄 Step {iteration + 1}/{self.config.max_steps}")
            print("─" * 40)
            
            # PLAN
            print("🧠 PLANNING...")
            step = self.plan(goal, previous_results)
            self.steps.append(step)
            self.metrics.total_steps += 1
            print(f"   Action: {step.action}")
            if step.tool:
                print(f"   Tool: {step.tool}")
            
            # ACT
            print("⚡ EXECUTING...")
            result = self.act(step)
            
            # Update metrics
            if step.status == StepStatus.SUCCESS:
                self.metrics.successful_steps += 1
            else:
                self.metrics.failed_steps += 1
            
            if step.retry_count > 0:
                self.metrics.retried_steps += 1
            
            self.metrics.total_execution_time_ms += step.execution_time_ms
            
            # OBSERVE
            print("👁️  OBSERVING...")
            self.goal_complete = self.observe(step)
            
            previous_results.append({
                "step": step.step_number,
                "tool": step.tool,
                "result": result,
                "status": step.status.value
            })
            
            if self.goal_complete:
                print(f"\n✅ GOAL COMPLETE! Stopping after {step.step_number} steps.")
                logger.info(f"Goal complete after {step.step_number} steps")
                break
            
            print(f"   Continuing... (goal not yet complete)")
            time.sleep(0.3)  # Brief pause for readability
        
        else:
            print(f"\n⏹️  MAX STEPS REACHED: Stopping after {self.config.max_steps} iterations")
            logger.info(f"Max steps ({self.config.max_steps}) reached")
        
        self.metrics.end_time = datetime.now()
        
        return self._generate_report()

    def _generate_report(self) -> dict:
        """Generate comprehensive execution report."""
        report = {
            "goal": self.goal,
            "goal_complete": self.goal_complete,
            "execution_summary": {
                "total_steps": len(self.steps),
                "max_steps_allowed": self.config.max_steps,
                "execution_time_seconds": round(
                    (self.metrics.end_time - self.metrics.start_time).total_seconds(), 2
                ) if self.metrics.end_time else 0
            },
            "metrics": self.metrics.to_dict(),
            "steps": [step.to_dict() for step in self.steps],
            "safety_limits": {
                "max_steps": self.config.max_steps,
                "max_time_seconds": self.config.max_time_seconds,
                "max_retries": self.config.max_retries,
                "tool_timeout": self.config.tool_timeout
            },
            "conclusion": self._generate_conclusion()
        }
        
        logger.info("Execution Report Generated")
        logger.info(f"Goal Complete: {self.goal_complete}")
        logger.info(f"Success Rate: {self.metrics.success_rate:.1f}%")
        
        return report

    def _generate_conclusion(self) -> str:
        """Generate human-readable conclusion."""
        if self.goal_complete:
            return f"✅ Goal '{self.goal}' was successfully achieved in {len(self.steps)} steps."
        
        if len(self.steps) >= self.config.max_steps:
            return f"⏹️ Goal not achieved: reached maximum step limit ({self.config.max_steps})."
        
        if self._check_timeout():
            return f"⏱️ Goal not achieved: execution timed out after {self.config.max_time_seconds}s."
        
        failed_steps = [s for s in self.steps if s.status == StepStatus.FAILED]
        if failed_steps:
            return f"❌ Goal not achieved: {len(failed_steps)} step(s) failed after all retries."
        
        return "⚠️ Goal not achieved for unknown reason."


def main():
    """Main interactive loop."""
    print("\n" + "=" * 60)
    print("🚀 Production Autonomous Agent")
    print("=" * 60)
    print("\nFeatures:")
    print("  • Goal-driven autonomy (loop until complete)")
    print("  • Safety controls (step limits, timeouts)")
    print("  • Retry logic with exponential backoff")
    print("  • Comprehensive error handling")
    print("  • Execution logging")
    print("\nExample goals:")
    print("  • 'Fix high disk usage'")
    print("  • 'Organize my Downloads folder'")
    print("  • 'Check system status'")
    print("\nCommands:")
    print("  • 'exit' - Quit")
    print()
    
    # Create agent with production config
    config = ExecutionConfig(
        max_steps=10,
        max_time_seconds=300,
        max_retries=3,
        tool_timeout=30,
        log_level="INFO"
    )
    agent = ProductionAgent(config=config)
    
    while True:
        try:
            goal = input("\n🎯 Enter your goal: ").strip()
            
            if goal.lower() in ['exit', 'quit', 'bye']:
                print("\n👋 Goodbye!")
                break
            
            if not goal:
                continue
            
            result = agent.run(goal)
            
            # Display report
            print("\n" + "=" * 60)
            print("📊 EXECUTION REPORT")
            print("=" * 60)
            print(f"\nGoal: {result['goal']}")
            print(f"Complete: {'✅ Yes' if result['goal_complete'] else '❌ No'}")
            print(f"Steps: {result['execution_summary']['total_steps']}/{result['safety_limits']['max_steps']}")
            print(f"Time: {result['execution_summary']['execution_time_seconds']}s")
            print(f"Success Rate: {result['metrics']['success_rate_percent']}%")
            print(f"\nConclusion: {result['conclusion']}")
            
            print("\n📋 Step Details:")
            for step in result['steps']:
                status_icon = {
                    'success': '✓',
                    'failed': '✗',
                    'timeout': '⏱',
                    'retrying': '↻'
                }.get(step['status'], '?')
                retry_info = f" (retried {step['retry_count']}x)" if step['retry_count'] > 0 else ""
                print(f"\n  Step {step['step']}: [{status_icon}] {step['action']}{retry_info}")
                if step['tool']:
                    print(f"           Tool: {step['tool']} ({step['execution_time_ms']:.0f}ms)")
                if step['error_message']:
                    print(f"           Error: {step['error_message']}")
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            logger.exception("Unexpected error in main loop")
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
