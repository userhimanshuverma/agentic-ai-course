"""
Executor - Executes plan steps.
"""

import time
from typing import Dict, Any, Optional

from ..mcp_server.registry import registry
from ..utils.schema import PlanStep, StepResult
from ..utils.logger import logger


class Executor:
    """Executes plan steps using available tools."""
    
    def __init__(self):
        self.execution_count = 0
    
    def execute_step(
        self,
        step: PlanStep,
        goal_id: str
    ) -> StepResult:
        """
        Execute a single plan step.
        
        Args:
            step: The step to execute
            goal_id: Goal identifier
        
        Returns:
            StepResult with execution details
        """
        start_time = time.time()
        
        logger.log_step_start(goal_id, step.step_number, step.description)
        
        try:
            # Check if step has a tool call
            if step.tool_call:
                result = self._execute_tool_call(step.tool_call, goal_id, step.step_number)
            else:
                # No tool call, just mark as completed
                result = {
                    "output": f"Step completed: {step.description}",
                    "success": True
                }
            
            execution_time = (time.time() - start_time) * 1000
            
            step_result = StepResult(
                step_number=step.step_number,
                success=result.get("success", True),
                output=result.get("output"),
                error=result.get("error"),
                execution_time_ms=execution_time
            )
            
            logger.log_step_complete(
                goal_id,
                step.step_number,
                step_result.success,
                execution_time
            )
            
            return step_result
            
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            
            logger.error(
                f"Step {step.step_number} failed: {str(e)}",
                goal_id=goal_id,
                step_number=step.step_number
            )
            
            return StepResult(
                step_number=step.step_number,
                success=False,
                output=None,
                error=str(e),
                execution_time_ms=execution_time
            )
    
    def _execute_tool_call(
        self,
        tool_call: Any,
        goal_id: str,
        step_number: int
    ) -> Dict[str, Any]:
        """Execute a tool call."""
        # Handle both dict and Pydantic model
        if hasattr(tool_call, 'dict'):
            tool_call = tool_call.dict()
        elif hasattr(tool_call, 'tool_name'):
            tool_call = {
                'tool_name': tool_call.tool_name,
                'arguments': tool_call.arguments
            }
        
        tool_name = tool_call.get("tool_name") if isinstance(tool_call, dict) else getattr(tool_call, 'tool_name', None)
        arguments = tool_call.get("arguments", {}) if isinstance(tool_call, dict) else getattr(tool_call, 'arguments', {})
        
        logger.log_tool_call(goal_id, step_number, tool_name, arguments)
        
        # Execute tool through registry
        result = registry.execute(tool_name, arguments)
        
        is_error = result.get("isError", False)
        content = result.get("content", [])
        
        # Extract text from content
        output = ""
        if content and len(content) > 0:
            output = content[0].get("text", "")
        
        logger.log_tool_result(
            goal_id,
            step_number,
            tool_name,
            not is_error,
            output[:200] if output else None
        )
        
        if is_error:
            return {
                "success": False,
                "output": None,
                "error": output
            }
        
        return {
            "success": True,
            "output": output,
            "error": None
        }


# Global executor instance
executor = Executor()
