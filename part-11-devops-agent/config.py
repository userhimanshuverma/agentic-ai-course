"""
Part 11: DevOps Monitoring Agent - Configuration Module
=======================================================

Centralized configuration management for the agent.
All settings can be customized via environment variables.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class AgentConfig:
    """
    Configuration for the DevOps Monitoring Agent.
    
    All values have sensible defaults but can be overridden
    via environment variables.
    
    Example:
        config = AgentConfig()
        print(f"Max steps: {config.max_steps}")
        
        # Or with custom values
        config = AgentConfig(max_steps=5, reasoning_mode="api")
    """
    
    # Safety Limits
    max_steps: int = 10
    max_time_seconds: int = 300  # 5 minutes
    max_retries: int = 3
    retry_delay_base: float = 1.0  # seconds
    tool_timeout: int = 30  # seconds per tool call
    
    # Reasoning Configuration
    reasoning_mode: str = "mock"  # "local", "api", or "mock"
    hf_api_token: Optional[str] = None
    
    # Monitoring Thresholds
    cpu_warning: float = 70.0
    cpu_critical: float = 90.0
    memory_warning: float = 80.0
    memory_critical: float = 95.0
    disk_warning: float = 80.0
    disk_critical: float = 95.0
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[str] = "devops_agent.log"
    
    def __post_init__(self):
        """Load configuration from environment variables"""
        # Safety limits
        self.max_steps = int(os.getenv("AGENT_MAX_STEPS", self.max_steps))
        self.max_time_seconds = int(os.getenv("AGENT_MAX_TIME", self.max_time_seconds))
        self.max_retries = int(os.getenv("AGENT_MAX_RETRIES", self.max_retries))
        self.retry_delay_base = float(os.getenv("AGENT_RETRY_DELAY", self.retry_delay_base))
        self.tool_timeout = int(os.getenv("AGENT_TOOL_TIMEOUT", self.tool_timeout))
        
        # Reasoning
        self.reasoning_mode = os.getenv("AGENT_REASONING_MODE", self.reasoning_mode)
        self.hf_api_token = os.getenv("HF_API_TOKEN", self.hf_api_token)
        
        # Thresholds
        self.cpu_warning = float(os.getenv("CPU_WARNING", self.cpu_warning))
        self.cpu_critical = float(os.getenv("CPU_CRITICAL", self.cpu_critical))
        self.memory_warning = float(os.getenv("MEMORY_WARNING", self.memory_warning))
        self.memory_critical = float(os.getenv("MEMORY_CRITICAL", self.memory_critical))
        self.disk_warning = float(os.getenv("DISK_WARNING", self.disk_warning))
        self.disk_critical = float(os.getenv("DISK_CRITICAL", self.disk_critical))
        
        # Logging
        self.log_level = os.getenv("AGENT_LOG_LEVEL", self.log_level)
        self.log_file = os.getenv("AGENT_LOG_FILE", self.log_file)


def load_config() -> AgentConfig:
    """
    Load configuration from environment variables.
    
    Returns:
        AgentConfig with values from environment or defaults
    
    Example:
        config = load_config()
        print(config.max_steps)
    """
    return AgentConfig()


# Default configuration instance
default_config = AgentConfig()
