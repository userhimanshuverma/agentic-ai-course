"""
Planner - Creates execution plans for goals.
"""

from typing import Dict, Any, List

from .llm import llm_manager
from ..mcp_server.registry import registry
from ..utils.schema import Plan, PlanStep
from ..utils.logger import logger


class Planner:
    """Creates structured execution plans."""
    
    def __init__(self):
        self.llm = llm_manager
    
    def create_plan(self, goal: str, goal_id: str) -> Plan:
        """
        Create an execution plan for a goal.
        
        Args:
            goal: The goal to achieve
            goal_id: Unique identifier for this goal
        
        Returns:
            Plan object with steps
        """
        logger.log_plan_created(goal_id, 0)
        
        # Get available tools
        tools_description = registry.get_tool_descriptions()
        
        # Create plan using LLM
        try:
            plan_data = self.llm.create_plan(goal, tools_description)
            
            # Validate and construct plan
            steps = []
            for step_data in plan_data.get("steps", []):
                step = PlanStep(
                    step_number=step_data["step_number"],
                    description=step_data["description"],
                    tool_call=step_data.get("tool_call"),
                    expected_output=step_data["expected_output"]
                )
                steps.append(step)
            
            plan = Plan(
                goal=goal,
                steps=steps,
                estimated_steps=len(steps)
            )
            
            logger.log_plan_created(goal_id, len(steps))
            
            return plan
            
        except Exception as e:
            logger.error(f"Failed to create plan: {str(e)}")
            # Return a simple fallback plan
            return Plan(
                goal=goal,
                steps=[
                    PlanStep(
                        step_number=1,
                        description=f"Attempt to achieve goal: {goal}",
                        tool_call=None,
                        expected_output="Goal achieved"
                    )
                ],
                estimated_steps=1
            )
    
    def replan(
        self,
        goal: str,
        goal_id: str,
        current_plan: Plan,
        failed_step: int,
        error: str
    ) -> Plan:
        """
        Create a revised plan after a step failure.
        
        Args:
            goal: The original goal
            goal_id: Goal identifier
            current_plan: Current plan that failed
            failed_step: Step number that failed
            error: Error message
        
        Returns:
            Revised plan
        """
        logger.info(f"Replanning after step {failed_step} failure", goal_id=goal_id)
        
        # For now, just return the remaining steps
        remaining_steps = [
            step for step in current_plan.steps
            if step.step_number > failed_step
        ]
        
        # Renumber steps
        for i, step in enumerate(remaining_steps, 1):
            step.step_number = i
        
        return Plan(
            goal=goal,
            steps=remaining_steps,
            estimated_steps=len(remaining_steps)
        )


# Global planner instance
planner = Planner()
