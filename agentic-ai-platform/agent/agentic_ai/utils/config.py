"""
Configuration module for Agentic AI Platform.
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """Application configuration."""
    
    # LLM Configuration
    OLLAMA_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    LLM_TIMEOUT: int = 120
    LLM_MAX_RETRIES: int = 3
    
    # MCP Server Configuration
    MCP_SERVER_HOST: str = "127.0.0.1"
    MCP_SERVER_PORT: int = 8001
    MCP_TRANSPORT: str = "stdio"  # or "http"
    
    # Memory Configuration
    CHROMA_DB_PATH: str = "./chroma_db"
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    MAX_SHORT_TERM_MEMORY: int = 10
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "./logs/agent.log"
    LOG_FORMAT: str = "json"
    
    # Security Configuration
    SAFE_DIRECTORY: str = "./safe_workspace"
    MAX_CODE_EXECUTION_TIME: int = 30
    ALLOWED_FILE_EXTENSIONS: tuple = (".txt", ".json", ".csv", ".py", ".md")
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        return cls(
            OLLAMA_URL=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            OLLAMA_MODEL=os.getenv("OLLAMA_MODEL", "mistral"),
            LLM_TIMEOUT=int(os.getenv("LLM_TIMEOUT", "120")),
            LLM_MAX_RETRIES=int(os.getenv("LLM_MAX_RETRIES", "3")),
            MCP_SERVER_HOST=os.getenv("MCP_SERVER_HOST", "127.0.0.1"),
            MCP_SERVER_PORT=int(os.getenv("MCP_SERVER_PORT", "8001")),
            CHROMA_DB_PATH=os.getenv("CHROMA_DB_PATH", "./chroma_db"),
            API_HOST=os.getenv("API_HOST", "0.0.0.0"),
            API_PORT=int(os.getenv("API_PORT", "8000")),
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
            SAFE_DIRECTORY=os.getenv("SAFE_DIRECTORY", "./safe_workspace"),
        )


# Global config instance
config = Config.from_env()
