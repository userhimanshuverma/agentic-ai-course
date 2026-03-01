"""
Structured logging module for Agentic AI Platform.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from .config import config


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add extra fields if present
        if hasattr(record, "agent_id"):
            log_data["agent_id"] = record.agent_id
        if hasattr(record, "goal_id"):
            log_data["goal_id"] = record.goal_id
        if hasattr(record, "tool_name"):
            log_data["tool_name"] = record.tool_name
        if hasattr(record, "step_number"):
            log_data["step_number"] = record.step_number
        if hasattr(record, "execution_time_ms"):
            log_data["execution_time_ms"] = record.execution_time_ms
        if hasattr(record, "extra_data"):
            log_data.update(record.extra_data)
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data)


class AgentLogger:
    """Structured logger for agent operations."""
    
    def __init__(self, name: str = "agentic_ai"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, config.LOG_LEVEL))
        
        # Clear existing handlers
        self.logger.handlers = []
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        
        if config.LOG_FORMAT == "json":
            console_handler.setFormatter(JSONFormatter())
        else:
            console_handler.setFormatter(
                logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
            )
        
        self.logger.addHandler(console_handler)
        
        # File handler
        if config.LOG_FILE:
            log_path = Path(config.LOG_FILE)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(config.LOG_FILE)
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(JSONFormatter())
            self.logger.addHandler(file_handler)
    
    def _log(self, level: int, message: str, **kwargs):
        """Internal log method with extra fields."""
        extra = {"extra_data": kwargs}
        self.logger.log(level, message, extra=extra)
    
    def debug(self, message: str, **kwargs):
        self._log(logging.DEBUG, message, **kwargs)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def critical(self, message: str, **kwargs):
        self._log(logging.CRITICAL, message, **kwargs)
    
    # Specialized logging methods
    def log_goal_start(self, goal: str, goal_id: str):
        """Log when a new goal is started."""
        self.info(
            f"Starting goal execution",
            goal=goal,
            goal_id=goal_id,
            event_type="goal_start"
        )
    
    def log_goal_complete(self, goal_id: str, success: bool, execution_time_ms: float):
        """Log when a goal is completed."""
        self.info(
            f"Goal execution {'succeeded' if success else 'failed'}",
            goal_id=goal_id,
            success=success,
            execution_time_ms=execution_time_ms,
            event_type="goal_complete"
        )
    
    def log_plan_created(self, goal_id: str, num_steps: int):
        """Log when a plan is created."""
        self.info(
            f"Plan created with {num_steps} steps",
            goal_id=goal_id,
            num_steps=num_steps,
            event_type="plan_created"
        )
    
    def log_step_start(self, goal_id: str, step_number: int, description: str):
        """Log when a step starts."""
        self.info(
            f"Starting step {step_number}: {description}",
            goal_id=goal_id,
            step_number=step_number,
            event_type="step_start"
        )
    
    def log_step_complete(self, goal_id: str, step_number: int, success: bool, execution_time_ms: float):
        """Log when a step completes."""
        self.info(
            f"Step {step_number} {'succeeded' if success else 'failed'}",
            goal_id=goal_id,
            step_number=step_number,
            success=success,
            execution_time_ms=execution_time_ms,
            event_type="step_complete"
        )
    
    def log_tool_call(self, goal_id: str, step_number: int, tool_name: str, arguments: Dict):
        """Log a tool call."""
        self.info(
            f"Calling tool: {tool_name}",
            goal_id=goal_id,
            step_number=step_number,
            tool_name=tool_name,
            arguments=arguments,
            event_type="tool_call"
        )
    
    def log_tool_result(self, goal_id: str, step_number: int, tool_name: str, success: bool, result: Any):
        """Log a tool result."""
        self.info(
            f"Tool {tool_name} {'succeeded' if success else 'failed'}",
            goal_id=goal_id,
            step_number=step_number,
            tool_name=tool_name,
            success=success,
            result_preview=str(result)[:200] if result else None,
            event_type="tool_result"
        )
    
    def log_llm_call(self, goal_id: str, prompt_type: str, tokens_used: Optional[int] = None):
        """Log an LLM API call."""
        self.info(
            f"LLM call for {prompt_type}",
            goal_id=goal_id,
            prompt_type=prompt_type,
            tokens_used=tokens_used,
            event_type="llm_call"
        )
    
    def log_memory_store(self, goal_id: str, memory_type: str, key: str):
        """Log memory storage."""
        self.info(
            f"Stored {memory_type} memory: {key}",
            goal_id=goal_id,
            memory_type=memory_type,
            key=key,
            event_type="memory_store"
        )
    
    def log_memory_retrieve(self, goal_id: str, memory_type: str, key: str, found: bool):
        """Log memory retrieval."""
        self.info(
            f"{'Found' if found else 'Missed'} {memory_type} memory: {key}",
            goal_id=goal_id,
            memory_type=memory_type,
            key=key,
            found=found,
            event_type="memory_retrieve"
        )


# Global logger instance
logger = AgentLogger()
