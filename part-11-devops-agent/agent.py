"""
Part 11: DevOps Monitoring Agent - Main Agent Module
====================================================

This is the main agent module that orchestrates the DevOps monitoring workflow.
It implements a goal-driven autonomous loop with:
- Safety controls (step limits, timeouts)
- Retry logic with exponential backoff
- AI-powered reasoning
- Comprehensive logging

Architecture:
    User Goal → Plan → Act → Observe → (loop until complete)
                    ↓
              Safety Layer (limits, retries, timeouts)
"""

import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

# Import our modules
from tools import SystemMonitor, get_monitor
from reasoning import MistralReasoner, ReasoningResult, ReasoningMode, get_reasoner
from config import AgentConfig, load_config


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('devops_agent.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of an execution step"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRYING = "retrying"
    TIMEOUT = "timeout"


@dataclass
class ExecutionStep:
    """Represents a single step in the execution"""
    step_number: int
    action: str
    reasoning: str
    tool: str
    parameters: Dict[str, Any]
    status: StepStatus = StepStatus.PENDING
    result: Any = None
    retry_count: int = 0
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None


@dataclass
class ExecutionMetrics:
    """Metrics for the entire execution"""
    total_steps: int = 0
    successful_steps: int = 0
    failed_steps: int = 0
    retried_steps: int = 0
    total_execution_time_ms: float = 0.0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    
    @property
    def success_rate_percent(self) -> float:
        if self.total_steps == 0:
            return 0.0
        return (self.successful_steps / self.total_steps) * 100


class DevOpsAgent:
    """
    DevOps Monitoring Agent with AI-powered reasoning.
    
    This agent monitors system health, detects anomalies, and suggests
    corrective actions using a goal-driven autonomous loop.
    
    Features:
    - Goal-driven autonomy (loop until goal achieved)
    - Safety controls (step limits, timeouts)
    - Retry logic with exponential backoff
    - AI-powered reasoning (Mistral)
    - Comprehensive metrics and logging
    
    Example:
        agent = DevOpsAgent()
        result = agent.run("Check system health")
        print(result['conclusion'])
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        """
        Initialize the DevOps Agent.
        
        Args:
            config: Agent configuration (uses defaults if None)
        """
        self.config = config or load_config()
        self.monitor = get_monitor()
        self.reasoner = get_reasoner(
            mode=self.config.reasoning_mode,
            api_token=self.config.hf_api_token
        )
        
        # Execution state
        self.steps: List[ExecutionStep] = []
        self.metrics = ExecutionMetrics()
        self.metrics_history: List[Dict[str, Any]] = []
        self.goal: str = ""
        self.goal_complete: bool = False
        self.start_time: Optional[datetime] = None
        
        # Setup logging level
        logging.getLogger().setLevel(getattr(logging, self.config.log_level.upper()))
        
        logger.info(f"DevOpsAgent initialized (mode: {self.config.reasoning_mode})")
    
    def run(self, goal: str) -> Dict[str, Any]:
        """
        Run the goal-driven autonomous monitoring loop.
        
        The loop continues until:
        1. Goal is achieved
        2. Max steps reached
        3. Timeout occurs
        
        Args:
            goal: The monitoring goal (e.g., "Check CPU usage")
        
        Returns:
            Dictionary with execution report
        
        Example:
            agent = DevOpsAgent()
            result = agent.run("Monitor system health")
            print(f"Complete: {result['goal_complete']}")
            print(f"Steps: {result['metrics']['total_steps']}")
        """
        self.goal = goal
        self.goal_complete = False
        self.steps = []
        self.metrics = ExecutionMetrics()
        self.metrics_history = []
        self.start_time = datetime.now()
        self.metrics.start_time = self.start_time
        
        logger.info("=" * 60)
        logger.info("DevOps Monitoring Agent Starting")
        logger.info("=" * 60)
        logger.info(f"Goal: {goal}")
        logger.info(f"Config: max_steps={self.config.max_steps}, timeout={self.config.max_time_seconds}s")
        
        # Print header
        print("\n" + "=" * 60)
        print("🖥️  DevOps Monitoring Agent")
        print("=" * 60)
        print(f"\n🎯 Goal: {goal}")
        print(f"⚙️  Safety Limits: {self.config.max_steps} steps, {self.config.max_time_seconds}s timeout")
        print(f"🧠 Reasoning: {self.config.reasoning_mode}")
        print("\n" + "─" * 60)
        
        # Main execution loop
        for step_number in range(1, self.config.max_steps + 1):
            # Check timeout
            if self._check_timeout():
                logger.warning(f"Execution timeout after {self.config.max_time_seconds}s")
                print(f"\n⏱️  TIMEOUT: Stopping after {self.config.max_time_seconds}s")
                break
            
            # Execute one step
            step = self._execute_step(step_number)
            self.steps.append(step)
            self.metrics.total_steps += 1
            
            # Update metrics
            if step.status == StepStatus.SUCCESS:
                self.metrics.successful_steps += 1
            elif step.status == StepStatus.FAILED:
                self.metrics.failed_steps += 1
            
            if step.retry_count > 0:
                self.metrics.retried_steps += 1
            
            # Check if goal is complete
            if self.goal_complete:
                logger.info(f"Goal complete after {step_number} steps")
                print(f"\n✅ GOAL COMPLETE! Stopping after {step_number} steps.")
                break
        
        else:
            # Loop completed without break (max steps reached)
            logger.info(f"Max steps ({self.config.max_steps}) reached")
            print(f"\n⏹️  MAX STEPS REACHED: Stopping after {self.config.max_steps} iterations")
        
        # Finalize metrics
        self.metrics.end_time = datetime.now()
        self.metrics.total_execution_time_ms = (
            self.metrics.end_time - self.start_time
        ).total_seconds() * 1000
        
        # Generate and return report
        return self._generate_report()
    
    def _execute_step(self, step_number: int) -> ExecutionStep:
        """
        Execute a single step: Plan → Act → Observe
        
        Args:
            step_number: Current step number
        
        Returns:
            ExecutionStep with results
        """
        print(f"\n🔄 Step {step_number}/{self.config.max_steps}")
        print("─" * 40)
        
        # === PLAN ===
        print("🧠 PLANNING...")
        
        # Collect current metrics
        current_metrics = self.monitor.get_all_metrics()
        self.metrics_history.append(current_metrics)
        
        # Get AI reasoning
        reasoning_result = self.reasoner.analyze_metrics(
            current_metrics,
            self.goal
        )
        
        step = ExecutionStep(
            step_number=step_number,
            action=reasoning_result.action,
            reasoning=reasoning_result.reasoning,
            tool=reasoning_result.tool_to_use,
            parameters=reasoning_result.parameters,
            status=StepStatus.PENDING
        )
        
        print(f"   Action: {step.action}")
        print(f"   Tool: {step.tool}")
        
        # === ACT ===
        print("⚡ EXECUTING...")
        step.status = StepStatus.RUNNING
        
        start_exec = time.time()
        
        # Execute with retry logic
        result = self._execute_with_retry(step)
        
        step.execution_time_ms = (time.time() - start_exec) * 1000
        step.result = result
        
        # === OBSERVE ===
        print("👁️  OBSERVING...")
        
        # Check if goal is complete
        self.goal_complete = reasoning_result.is_complete
        
        # Additional completion checks
        if step.tool == "get_all_metrics" and self._is_system_healthy(current_metrics):
            self.goal_complete = True
        
        if self.goal_complete:
            print("   ✅ Goal achieved!")
        else:
            print("   📝 Continuing...")
        
        return step
    
    def _execute_with_retry(self, step: ExecutionStep) -> Any:
        """
        Execute a tool with retry logic and exponential backoff.
        
        Args:
            step: The execution step
        
        Returns:
            Tool execution result
        """
        for attempt in range(self.config.max_retries + 1):
            step.retry_count = attempt
            
            try:
                # Execute the tool
                result = self._execute_tool(step.tool, step.parameters)
                
                step.status = StepStatus.SUCCESS
                print(f"   ✅ Success ({step.execution_time_ms:.0f}ms)")
                
                return result
                
            except Exception as e:
                step.error_message = str(e)
                logger.error(f"Step {step.step_number} attempt {attempt + 1} failed: {e}")
                
                if attempt < self.config.max_retries:
                    # Calculate backoff delay
                    delay = self.config.retry_delay_base * (2 ** attempt)
                    step.status = StepStatus.RETRYING
                    print(f"   ⚠️  Failed: {e}")
                    print(f"   ↻ Retrying in {delay}s... (attempt {attempt + 2}/{self.config.max_retries + 1})")
                    time.sleep(delay)
                else:
                    # All retries exhausted
                    step.status = StepStatus.FAILED
                    print(f"   ❌ Failed after {self.config.max_retries + 1} attempts")
                    return {"error": str(e)}
        
        return {"error": "Unexpected execution path"}
    
    def _execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """
        Execute a monitoring tool by name.
        
        Args:
            tool_name: Name of the tool to execute
            parameters: Tool parameters
        
        Returns:
            Tool execution result
        """
        # Tool dispatch
        if tool_name == "get_cpu_metrics":
            interval = parameters.get("interval", 0.5)
            return self.monitor.get_cpu_metrics(interval=interval)
        
        elif tool_name == "get_memory_metrics":
            return self.monitor.get_memory_metrics()
        
        elif tool_name == "get_disk_metrics":
            path = parameters.get("path", '/')
            return self.monitor.get_disk_metrics(path=path)
        
        elif tool_name == "get_network_metrics":
            return self.monitor.get_network_metrics()
        
        elif tool_name == "get_process_metrics":
            top_n = parameters.get("top_n", 5)
            return self.monitor.get_process_metrics(top_n=top_n)
        
        elif tool_name == "get_all_metrics":
            return self.monitor.get_all_metrics()
        
        elif tool_name == "detect_anomalies":
            return self.monitor.detect_anomalies(self.metrics_history)
        
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _check_timeout(self) -> bool:
        """Check if execution has exceeded time limit"""
        if self.start_time is None:
            return False
        
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return elapsed > self.config.max_time_seconds
    
    def _is_system_healthy(self, metrics: Dict[str, Any]) -> bool:
        """Check if all system metrics are in normal range"""
        try:
            cpu_status = metrics.get('cpu', {}).get('status', 'normal')
            mem_status = metrics.get('memory', {}).get('status', 'normal')
            disk_status = metrics.get('disk', {}).get('status', 'normal')
            
            return cpu_status == 'normal' and mem_status == 'normal' and disk_status == 'normal'
        except:
            return False
    
    def _generate_report(self) -> Dict[str, Any]:
        """Generate final execution report"""
        report = {
            'goal': self.goal,
            'goal_complete': self.goal_complete,
            'execution_summary': {
                'total_steps': self.metrics.total_steps,
                'successful_steps': self.metrics.successful_steps,
                'failed_steps': self.metrics.failed_steps,
                'retried_steps': self.metrics.retried_steps,
                'execution_time_seconds': round(self.metrics.total_execution_time_ms / 1000, 2),
                'success_rate_percent': round(self.metrics.success_rate_percent, 1)
            },
            'safety_limits': {
                'max_steps': self.config.max_steps,
                'max_time_seconds': self.config.max_time_seconds,
                'max_retries': self.config.max_retries,
                'tool_timeout': self.config.tool_timeout
            },
            'steps': [
                {
                    'step_number': s.step_number,
                    'action': s.action,
                    'tool': s.tool,
                    'status': s.status.value,
                    'retry_count': s.retry_count,
                    'execution_time_ms': round(s.execution_time_ms, 2),
                    'result': s.result if isinstance(s.result, dict) else str(s.result)[:200]
                }
                for s in self.steps
            ],
            'final_metrics': self.metrics_history[-1] if self.metrics_history else {},
            'conclusion': self._generate_conclusion()
        }
        
        logger.info("Execution Report Generated")
        logger.info(f"Goal Complete: {self.goal_complete}")
        logger.info(f"Success Rate: {self.metrics.success_rate_percent:.1f}%")
        
        # Print report
        print("\n" + "=" * 60)
        print("📊 EXECUTION REPORT")
        print("=" * 60)
        print(f"Goal: {self.goal}")
        print(f"Complete: {'✅ Yes' if self.goal_complete else '❌ No'}")
        print(f"Steps: {self.metrics.total_steps}/{self.config.max_steps}")
        print(f"Time: {report['execution_summary']['execution_time_seconds']:.1f}s")
        print(f"Success Rate: {self.metrics.success_rate_percent:.1f}%")
        print(f"\nConclusion: {report['conclusion']}")
        print("=" * 60)
        
        return report
    
    def _generate_conclusion(self) -> str:
        """Generate a human-readable conclusion"""
        if self.goal_complete:
            return f"✅ Goal '{self.goal}' was successfully achieved in {self.metrics.total_steps} steps."
        elif self.metrics.total_steps >= self.config.max_steps:
            return f"⏹️  Max steps ({self.config.max_steps}) reached. Goal may require more iterations or manual intervention."
        else:
            return f"⚠️  Execution stopped. Goal not yet complete after {self.metrics.total_steps} steps."


def main():
    """Main entry point for interactive usage"""
    print("\n" + "=" * 60)
    print("DevOps Monitoring Agent")
    print("=" * 60)
    
    # Get goal from user
    print("\nAvailable goals:")
    print("  - 'Check system health'")
    print("  - 'Monitor CPU usage'")
    print("  - 'Check memory status'")
    print("  - 'Monitor disk space'")
    print("  - 'Detect anomalies'")
    print("  - Or type your own...")
    
    goal = input("\n🎯 Enter your monitoring goal: ").strip()
    
    if not goal:
        goal = "Check system health"
        print(f"Using default goal: {goal}")
    
    # Create and run agent
    agent = DevOpsAgent()
    result = agent.run(goal)
    
    return result


if __name__ == "__main__":
    main()
