"""
System information tool for MCP server.
"""

import platform
import time
from typing import Any, Dict


class SystemTool:
    """System information tool."""
    
    name = "system_tool"
    description = "Get system information (CPU, memory, platform)"
    
    input_schema = {
        "type": "object",
        "properties": {
            "info_type": {
                "type": "string",
                "enum": ["platform", "cpu", "memory", "all"],
                "description": "Type of system information to retrieve"
            }
        },
        "required": ["info_type"]
    }
    
    def __init__(self):
        self.start_time = time.time()
    
    def execute(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Execute system tool."""
        info_type = arguments.get("info_type", "all")
        
        try:
            if info_type == "platform":
                result = self._get_platform_info()
            elif info_type == "cpu":
                result = self._get_cpu_info()
            elif info_type == "memory":
                result = self._get_memory_info()
            elif info_type == "all":
                result = self._get_all_info()
            else:
                return {
                    "content": [{"type": "text", "text": f"Error: Unknown info_type: {info_type}"}],
                    "isError": True
                }
            
            return {
                "content": [{"type": "text", "text": result}],
                "isError": False
            }
        except Exception as e:
            return {
                "content": [{"type": "text", "text": f"Error: {str(e)}"}],
                "isError": True
            }
    
    def _get_platform_info(self) -> str:
        """Get platform information."""
        return (
            f"Platform: {platform.system()}\n"
            f"Release: {platform.release()}\n"
            f"Version: {platform.version()}\n"
            f"Machine: {platform.machine()}\n"
            f"Processor: {platform.processor()}\n"
            f"Python: {platform.python_version()}"
        )
    
    def _get_cpu_info(self) -> str:
        """Get CPU information."""
        try:
            import psutil
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_count = psutil.cpu_count()
            cpu_freq = psutil.cpu_freq()
            
            return (
                f"CPU Cores: {cpu_count}\n"
                f"CPU Usage: {cpu_percent}%\n"
                f"CPU Frequency: {cpu_freq.current:.0f} MHz"
            )
        except ImportError:
            return "CPU Info: psutil not installed. Install with: pip install psutil"
    
    def _get_memory_info(self) -> str:
        """Get memory information."""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            return (
                f"Total Memory: {self._format_bytes(memory.total)}\n"
                f"Available: {self._format_bytes(memory.available)}\n"
                f"Used: {self._format_bytes(memory.used)} ({memory.percent}%)\n"
                f"Free: {self._format_bytes(memory.free)}"
            )
        except ImportError:
            return "Memory Info: psutil not installed. Install with: pip install psutil"
    
    def _get_all_info(self) -> str:
        """Get all system information."""
        uptime = time.time() - self.start_time
        
        return (
            f"=== System Information ===\n\n"
            f"{self._get_platform_info()}\n\n"
            f"{self._get_cpu_info()}\n\n"
            f"{self._get_memory_info()}\n\n"
            f"Server Uptime: {uptime:.0f} seconds"
        )
    
    def _format_bytes(self, bytes: int) -> str:
        """Format bytes to human readable."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024
        return f"{bytes:.2f} PB"


# Tool instance
system_tool = SystemTool()
