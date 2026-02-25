"""
Support Tools Module - Tools for the support assistant
"""
import shutil
import platform
import subprocess
from pathlib import Path
from typing import Dict, List


def check_disk_space() -> Dict:
    """Check system disk space."""
    try:
        total, used, free = shutil.disk_usage("/")
        percent_used = (used / total) * 100

        status = "good"
        if percent_used > 90:
            status = "critical"
        elif percent_used > 75:
            status = "warning"

        return {
            "status": status,
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_used": round(percent_used, 2),
            "message": _get_disk_advice(percent_used)
        }
    except Exception as e:
        return {"error": f"Could not check disk space: {str(e)}"}


def _get_disk_advice(percent_used: float) -> str:
    """Get advice based on disk usage."""
    if percent_used > 90:
        return "CRITICAL: Disk space is very low. Consider cleaning up files immediately."
    elif percent_used > 75:
        return "WARNING: Disk space is getting full. Consider organizing or deleting files."
    elif percent_used > 50:
        return "Disk space is moderate. Monitor usage."
    else:
        return "Disk space is healthy."


def check_system_info() -> Dict:
    """Get basic system information."""
    return {
        "os": platform.system(),
        "os_version": platform.release(),
        "platform": platform.platform(),
        "processor": platform.processor() or "Unknown",
        "architecture": platform.architecture()[0]
    }


def suggest_organize_disk() -> Dict:
    """Suggest organizing files to free space."""
    common_folders = [
        ("Downloads", Path.home() / "Downloads"),
        ("Desktop", Path.home() / "Desktop"),
        ("Documents", Path.home() / "Documents"),
        ("Temp", Path.home() / "AppData" / "Local" / "Temp"),
    ]

    suggestions = []
    for name, path in common_folders:
        if path.exists():
            try:
                size = sum(f.stat().st_size for f in path.rglob('*') if f.is_file())
                size_mb = round(size / (1024**2), 2)
                if size_mb > 100:  # Only suggest if > 100MB
                    suggestions.append({
                        "folder": name,
                        "path": str(path),
                        "size_mb": size_mb
                    })
            except:
                pass

    suggestions.sort(key=lambda x: x["size_mb"], reverse=True)

    return {
        "message": "Folders that could be organized to free space:",
        "suggestions": suggestions[:5]  # Top 5
    }


def get_common_fixes(issue_type: str) -> List[str]:
    """Get common fixes for known issues."""
    fixes = {
        "disk": [
            "Run Disk Cleanup utility",
            "Uninstall unused programs",
            "Clear browser cache",
            "Move large files to external storage",
            "Use the file organizer tool"
        ],
        "slow": [
            "Restart your computer",
            "Close unused applications",
            "Check for malware",
            "Update drivers",
            "Free up disk space"
        ],
        "network": [
            "Restart your router",
            "Check WiFi connection",
            "Run network troubleshooter",
            "Update network drivers",
            "Check for Windows updates"
        ],
        "memory": [
            "Close unused applications",
            "Restart your computer",
            "Check for memory leaks",
            "Add more RAM if possible",
            "Disable startup programs"
        ]
    }
    return fixes.get(issue_type.lower(), [
        "Restart your computer",
        "Check for updates",
        "Run system diagnostics"
    ])


# Tool registry
TOOL_REGISTRY = {
    "check_disk": check_disk_space,
    "system_info": check_system_info,
    "suggest_organize": suggest_organize_disk,
    "get_fixes": get_common_fixes,
}


def get_tool(name: str):
    """Get a tool by name."""
    return TOOL_REGISTRY.get(name)


def list_tools():
    """List all available tools."""
    return list(TOOL_REGISTRY.keys())
