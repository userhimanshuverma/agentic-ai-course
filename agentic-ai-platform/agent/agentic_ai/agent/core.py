"""
Core Agent - Main agent orchestrator.
"""

import time
import uuid
from typing import Dict, Any, List, Optional

from .planner import planner
from .executor import executor
from .reflector import reflector
from .memory import memory_manager
from .llm import llm_manager
from ..utils.schema import ExecutionReport, Plan, StepResult, Reflection
from ..utils.logger import logger


class Agent:
    """
    Main agent class that orchestrates planning, execution, and reflection.
    
    The agent follows a Plan → Execute → Reflect loop:
    1. Plan: Break down goal into steps
    2. Execute: Run each step using available tools
    3. Reflect: Analyze results and learn
    """
    
    def __init__(self):
        self.planner = planner
        self.executor = executor
        self.reflector = reflector
        self.memory = memory_manager
        self.llm = llm_manager
        self.running = False
    
    def run_goal(self, goal: str, goal_id: str = None) -> ExecutionReport:
        """
        Execute a goal through the full agent loop.
        
        Args:
            goal: The goal to achieve
            goal_id: Optional goal identifier (generated if not provided)
        
        Returns:
            ExecutionReport with full execution details
        """
        start_time = time.time()
        goal_id = goal_id or str(uuid.uuid4())
        
        logger.log_goal_start(goal, goal_id)
        
        # Store goal in memory
        self.memory.add_goal(goal, goal_id)
        
        try:
            # Step 1: Plan
            plan = self._plan(goal, goal_id)
            
            # Step 2: Execute
            results = self._execute_plan(plan, goal_id)
            
            # Step 3: Reflect
            reflection = self._reflect(goal, plan, results, goal_id)
            
            # Calculate total time
            total_time = (time.time() - start_time) * 1000
            
            # Create report
            report = ExecutionReport(
                goal=goal,
                success=reflection.success,
                plan=plan,
                results=results,
                reflection=reflection,
                total_execution_time_ms=total_time
            )
            
            # Store reflection
            self.memory.add_reflection(reflection.dict(), goal_id)
            
            logger.log_goal_complete(goal_id, reflection.success, total_time)
            
            # Persist memory
            self.memory.persist()
            
            return report
            
        except Exception as e:
            logger.error(f"Goal execution failed: {str(e)}", goal_id=goal_id)
            
            total_time = (time.time() - start_time) * 1000
            
            return ExecutionReport(
                goal=goal,
                success=False,
                plan=Plan(goal=goal, steps=[], estimated_steps=0),
                results=[],
                reflection=Reflection(
                    success=False,
                    summary=f"Execution failed: {str(e)}",
                    lessons_learned=["Execution error occurred"],
                    improvements=["Check error logs"]
                ),
                total_execution_time_ms=total_time
            )
    
    def _plan(self, goal: str, goal_id: str) -> Plan:
        """Create execution plan."""
        logger.info(f"Creating plan for goal: {goal}", goal_id=goal_id)
        return self.planner.create_plan(goal, goal_id)
    
    def _execute_plan(self, plan: Plan, goal_id: str) -> List[StepResult]:
        """Execute all plan steps."""
        results = []
        
        for step in plan.steps:
            # Execute step
            result = self.executor.execute_step(step, goal_id)
            results.append(result)
            
            # Store in memory
            self.memory.add_step_result(goal_id, step.step_number, result.dict())
            
            # If step failed, we could replan here
            if not result.success:
                logger.warning(
                    f"Step {step.step_number} failed, continuing...",
                    goal_id=goal_id
                )
        
        return results
    
    def _reflect(
        self,
        goal: str,
        plan: Plan,
        results: List[StepResult],
        goal_id: str
    ) -> Reflection:
        """Reflect on execution results."""
        logger.info("Reflecting on execution", goal_id=goal_id)
        return self.reflector.reflect(goal, plan, results, goal_id)
    
    def get_memory_context(self, goal_id: str) -> Dict[str, Any]:
        """Get memory context for a goal."""
        return self.memory.get_context_for_goal(goal_id)
    
    def health_check(self) -> Dict[str, Any]:
        """Check agent health."""
        return {
            "status": "healthy",
            "llm_available": self.llm.check_model_available(),
            "memory_available": self.memory.long_term.collection is not None
        }


# Global agent instance
agent = Agent()
