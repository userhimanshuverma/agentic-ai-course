"""
Reflector - Analyzes execution results.
"""

from typing import Dict, Any, List

from .llm import llm_manager
from ..utils.schema import Plan, StepResult, Reflection
from ..utils.logger import logger


class Reflector:
    """Reflects on execution results and provides insights."""
    
    def __init__(self):
        self.llm = llm_manager
    
    def reflect(
        self,
        goal: str,
        plan: Plan,
        results: List[StepResult],
        goal_id: str
    ) -> Reflection:
        """
        Reflect on execution results.
        
        Args:
            goal: The original goal
            plan: The execution plan
            results: List of step results
            goal_id: Goal identifier
        
        Returns:
            Reflection with analysis
        """
        try:
            # Convert results to dict for LLM
            results_data = [
                {
                    "step_number": r.step_number,
                    "success": r.success,
                    "output": r.output,
                    "error": r.error
                }
                for r in results
            ]
            
            reflection_data = self.llm.reflect_on_execution(
                goal=goal,
                plan=plan.dict(),
                results=results_data
            )
            
            reflection = Reflection(
                success=reflection_data.get("success", False),
                summary=reflection_data.get("summary", ""),
                lessons_learned=reflection_data.get("lessons_learned", []),
                improvements=reflection_data.get("improvements", [])
            )
            
            return reflection
            
        except Exception as e:
            logger.error(f"Reflection failed: {str(e)}", goal_id=goal_id)
            
            # Calculate success rate
            success_count = sum(1 for r in results if r.success)
            success_rate = success_count / len(results) if results else 0
            
            return Reflection(
                success=success_rate >= 0.5,
                summary=f"Execution completed with {success_count}/{len(results)} steps successful",
                lessons_learned=["Reflection generation failed"],
                improvements=["Check LLM connection for better reflection"]
            )
    
    def quick_reflect(
        self,
        goal: str,
        results: List[StepResult]
    ) -> Dict[str, Any]:
        """
        Quick reflection without LLM.
        
        Args:
            goal: The original goal
            results: List of step results
        
        Returns:
            Simple reflection dict
        """
        success_count = sum(1 for r in results if r.success)
        total_count = len(results)
        success_rate = success_count / total_count if total_count else 0
        
        errors = [r.error for r in results if r.error]
        
        return {
            "success": success_rate >= 0.5,
            "success_rate": success_rate,
            "successful_steps": success_count,
            "total_steps": total_count,
            "errors": errors,
            "summary": f"Completed {success_count}/{total_count} steps successfully"
        }


# Global reflector instance
reflector = Reflector()
