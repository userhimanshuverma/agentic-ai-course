"""
Tools Module - Available tools for the autonomous agent
"""
import os
import shutil
import platform
from pathlib import Path
from typing import Dict, List


def check_disk_space() -> Dict:
    """
    Check system disk space.
    Returns status and recommendations.
    """
    try:
        # Get disk usage for the current drive
        if platform.system() == "Windows":
            total, used, free = shutil.disk_usage("C:\\")
        else:
            total, used, free = shutil.disk_usage("/")

        percent_used = (used / total) * 100

        # Determine status
        if percent_used > 90:
            status = "critical"
        elif percent_used > 75:
            status = "warning"
        else:
            status = "good"

        return {
            "status": status,
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_used": round(percent_used, 2),
            "message": _get_disk_message(status, percent_used),
            "needs_action": status in ["warning", "critical"]
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "message": f"Could not check disk: {str(e)}",
            "needs_action": False
        }


def _get_disk_message(status: str, percent: float) -> str:
    """Get appropriate message for disk status."""
    messages = {
        "critical": f"CRITICAL: Disk is {percent:.1f}% full! Immediate action needed.",
        "warning": f"WARNING: Disk is {percent:.1f}% full. Consider cleaning up files.",
        "good": f"Disk is healthy ({percent:.1f}% used).",
        "error": "Could not determine disk status."
    }
    return messages.get(status, "Unknown status")


def suggest_organize() -> Dict:
    """
    Suggest folders to organize based on size.
    """
    suggestions = []

    # Common folders to check
    folders_to_check = [
        ("Downloads", Path.home() / "Downloads"),
        ("Desktop", Path.home() / "Desktop"),
        ("Documents", Path.home() / "Documents"),
        ("Pictures", Path.home() / "Pictures"),
    ]

    for name, path in folders_to_check:
        if path.exists():
            try:
                # Calculate folder size
                total_size = 0
                file_count = 0

                for item in path.iterdir():
                    if item.is_file():
                        total_size += item.stat().st_size
                        file_count += 1
                    elif item.is_dir():
                        # Limit depth for performance
                        for subitem in item.iterdir():
                            if subitem.is_file():
                                total_size += subitem.stat().st_size
                                file_count += 1

                size_mb = round(total_size / (1024**2), 2)

                if size_mb > 50:  # Only suggest if > 50MB
                    suggestions.append({
                        "folder": name,
                        "path": str(path),
                        "size_mb": size_mb,
                        "file_count": file_count,
                        "priority": "high" if size_mb > 500 else "medium"
                    })

            except Exception:
                pass

    # Sort by size (largest first)
    suggestions.sort(key=lambda x: x["size_mb"], reverse=True)

    return {
        "suggestions": suggestions[:5],  # Top 5
        "total_suggestions": len(suggestions),
        "message": f"Found {len(suggestions)} folders that could be organized."
    }


def file_organizer(folder_path: str) -> Dict:
    """
    Organize files in a folder by type.
    """
    target = Path(folder_path).expanduser().resolve()

    if not target.exists():
        return {
            "error": f"Folder not found: {folder_path}",
            "success": False
        }

    # File type categories
    categories = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".md"],
        "Data": [".csv", ".xls", ".xlsx", ".json", ".xml"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv"],
        "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg"],
        "Archives": [".zip", ".rar", ".7z", ".tar", ".gz"],
        "Code": [".py", ".js", ".html", ".css", ".java", ".cpp"],
    }

    files_moved = 0
    organized = {}

    try:
        for file_path in target.iterdir():
            if not file_path.is_file():
                continue

            ext = file_path.suffix.lower()
            file_name = file_path.name

            # Find category
            for category, extensions in categories.items():
                if ext in extensions:
                    category_dir = target / category
                    category_dir.mkdir(exist_ok=True)

                    # Move file
                    destination = category_dir / file_name
                    counter = 1
                    while destination.exists():
                        stem = file_path.stem
                        destination = category_dir / f"{stem}_{counter}{ext}"
                        counter += 1

                    shutil.move(str(file_path), str(destination))

                    if category not in organized:
                        organized[category] = []
                    organized[category].append(file_name)
                    files_moved += 1
                    break

        return {
            "success": True,
            "folder": str(target),
            "files_moved": files_moved,
            "organized": organized,
            "message": f"Organized {files_moved} files into {len(organized)} categories."
        }

    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


def system_info() -> Dict:
    """
    Get system information.
    """
    return {
        "os": platform.system(),
        "os_version": platform.release(),
        "platform": platform.platform(),
        "processor": platform.processor() or "Unknown",
        "architecture": platform.architecture()[0],
        "python_version": platform.python_version(),
        "message": f"Running on {platform.system()} {platform.release()}"
    }


def calculator(expression: str) -> Dict:
    """
    Safely evaluate a math expression.
    """
    import re

    # Validate expression
    if not re.match(r'^[0-9+\-*/().\s]+$', expression):
        return {
            "error": "Invalid expression",
            "success": False
        }

    try:
        result = eval(expression)
        return {
            "success": True,
            "expression": expression,
            "result": result,
            "message": f"{expression} = {result}"
        }
    except Exception as e:
        return {
            "error": str(e),
            "success": False
        }


# Tool registry
TOOL_REGISTRY = {
    "check_disk": check_disk_space,
    "suggest_organize": suggest_organize,
    "file_organizer": file_organizer,
    "system_info": system_info,
    "calculator": calculator,
}


def get_tool(name: str):
    """Get a tool by name."""
    return TOOL_REGISTRY.get(name)


def list_tools():
    """List all available tools."""
    return list(TOOL_REGISTRY.keys())
