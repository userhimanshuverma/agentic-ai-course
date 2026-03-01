"""
FastAPI Server - REST API for the agent.
"""

import json
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ..agent.core import agent
from ..utils.config import config
from ..utils.logger import logger


# Request/Response models
class GoalRequest(BaseModel):
    """Request model for goal execution."""
    goal: str = Field(..., description="The goal to achieve")
    goal_id: Optional[str] = Field(None, description="Optional goal identifier")


class GoalResponse(BaseModel):
    """Response model for goal execution."""
    goal_id: str
    success: bool
    summary: str
    execution_time_ms: float
    steps_executed: int
    steps_successful: int


class ExecutionDetailResponse(BaseModel):
    """Detailed execution response."""
    goal: str
    goal_id: str
    success: bool
    plan: Dict[str, Any]
    results: list
    reflection: Dict[str, Any]
    total_execution_time_ms: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    llm_available: bool
    memory_available: bool


# Create FastAPI app
app = FastAPI(
    title="Agentic AI Platform",
    description="MCP-enabled Agentic AI with local LLM",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "name": "Agentic AI Platform",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    health = agent.health_check()
    return HealthResponse(
        status=health["status"],
        timestamp=datetime.utcnow().isoformat(),
        llm_available=health["llm_available"],
        memory_available=health["memory_available"]
    )


@app.post("/goal", response_model=GoalResponse)
async def execute_goal(request: GoalRequest, background_tasks: BackgroundTasks):
    """
    Execute a goal.
    
    This endpoint accepts a goal, plans execution steps,
    executes them, and returns results.
    """
    try:
        # Run the goal
        report = agent.run_goal(request.goal, request.goal_id)
        
        # Count successful steps
        successful_steps = sum(1 for r in report.results if r.success)
        
        return GoalResponse(
            goal_id=request.goal_id or "unknown",
            success=report.success,
            summary=report.reflection.summary,
            execution_time_ms=report.total_execution_time_ms,
            steps_executed=len(report.results),
            steps_successful=successful_steps
        )
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/goal/detail", response_model=ExecutionDetailResponse)
async def execute_goal_detail(request: GoalRequest):
    """
    Execute a goal and return detailed results.
    
    Returns the full execution report including plan, results, and reflection.
    """
    try:
        report = agent.run_goal(request.goal, request.goal_id)
        
        return ExecutionDetailResponse(
            goal=report.goal,
            goal_id=request.goal_id or "unknown",
            success=report.success,
            plan=report.plan.dict(),
            results=[r.dict() for r in report.results],
            reflection=report.reflection.dict(),
            total_execution_time_ms=report.total_execution_time_ms
        )
        
    except Exception as e:
        logger.error(f"API error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/logs")
async def get_logs(lines: int = 100):
    """
    Get recent logs.
    
    Returns the last N lines from the log file.
    """
    try:
        from pathlib import Path
        
        log_path = Path(config.LOG_FILE)
        if not log_path.exists():
            return {"logs": []}
        
        with open(log_path, 'r') as f:
            all_lines = f.readlines()
            recent_lines = all_lines[-lines:] if len(all_lines) > lines else all_lines
            
            # Parse JSON lines
            logs = []
            for line in recent_lines:
                try:
                    logs.append(json.loads(line))
                except:
                    logs.append({"raw": line.strip()})
        
        return {"logs": logs}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/memory/{goal_id}")
async def get_memory(goal_id: str):
    """
    Get memory for a specific goal.
    
    Returns both short-term and long-term memory context.
    """
    try:
        context = agent.get_memory_context(goal_id)
        return context
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
async def list_tools():
    """
    List available tools.
    
    Returns all tools registered with the MCP server.
    """
    from ..mcp_server.registry import registry
    
    return {"tools": registry.list_tools()}


def run_api():
    """Run the FastAPI server."""
    import uvicorn
    
    uvicorn.run(
        app,
        host=config.API_HOST,
        port=config.API_PORT
    )


if __name__ == "__main__":
    run_api()
