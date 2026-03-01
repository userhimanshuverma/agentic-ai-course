"""
JSON Schema definitions for structured LLM outputs.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Schema for a tool call."""
    tool_name: str = Field(..., description="Name of the tool to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class PlanStep(BaseModel):
    """Schema for a single step in a plan."""
    step_number: int = Field(..., description="Step sequence number")
    description: str = Field(..., description="What this step does")
    tool_call: Optional[ToolCall] = Field(None, description="Tool to use for this step")
    expected_output: str = Field(..., description="Expected result from this step")


class Plan(BaseModel):
    """Schema for an execution plan."""
    goal: str = Field(..., description="The original goal")
    steps: List[PlanStep] = Field(..., description="List of steps to achieve the goal")
    estimated_steps: int = Field(..., description="Total number of steps")


class StepResult(BaseModel):
    """Schema for step execution result."""
    step_number: int = Field(..., description="Step that was executed")
    success: bool = Field(..., description="Whether the step succeeded")
    output: Any = Field(..., description="Step output")
    error: Optional[str] = Field(None, description="Error message if failed")
    execution_time_ms: float = Field(..., description="Time taken to execute")


class Reflection(BaseModel):
    """Schema for reflection on execution."""
    success: bool = Field(..., description="Whether the overall goal was achieved")
    summary: str = Field(..., description="Summary of what was accomplished")
    lessons_learned: List[str] = Field(default_factory=list, description="Key insights")
    improvements: List[str] = Field(default_factory=list, description="Suggested improvements")


class ExecutionReport(BaseModel):
    """Schema for final execution report."""
    goal: str = Field(..., description="Original goal")
    success: bool = Field(..., description="Whether goal was achieved")
    plan: Plan = Field(..., description="The execution plan")
    results: List[StepResult] = Field(..., description="Results of each step")
    reflection: Reflection = Field(..., description="Reflection on execution")
    total_execution_time_ms: float = Field(..., description="Total time taken")


class ToolDefinition(BaseModel):
    """Schema for tool definition (MCP compatible)."""
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="What the tool does")
    input_schema: Dict[str, Any] = Field(..., description="JSON schema for inputs")


class MCPToolResponse(BaseModel):
    """Schema for MCP tool response."""
    content: List[Dict[str, Any]] = Field(..., description="Response content")
    isError: bool = Field(False, description="Whether an error occurred")


# JSON schemas for LLM prompting
PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "goal": {"type": "string"},
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step_number": {"type": "integer"},
                    "description": {"type": "string"},
                    "tool_call": {
                        "type": "object",
                        "properties": {
                            "tool_name": {"type": "string"},
                            "arguments": {"type": "object"}
                        }
                    },
                    "expected_output": {"type": "string"}
                },
                "required": ["step_number", "description", "expected_output"]
            }
        },
        "estimated_steps": {"type": "integer"}
    },
    "required": ["goal", "steps", "estimated_steps"]
}


REFLECTION_SCHEMA = {
    "type": "object",
    "properties": {
        "success": {"type": "boolean"},
        "summary": {"type": "string"},
        "lessons_learned": {"type": "array", "items": {"type": "string"}},
        "improvements": {"type": "array", "items": {"type": "string"}}
    },
    "required": ["success", "summary"]
}
