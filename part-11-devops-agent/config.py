"""Simple configuration for DevOps Agent"""

from dataclasses import dataclass


@dataclass
class Config:
    """Agent configuration"""
    max_steps: int = 10
    max_time: int = 300  # seconds
    retries: int = 3
    retry_delay: float = 1.0
    ollama_url: str = "http://localhost:11434"
