"""
Tools Module - Available tools for the agent
"""
import os
import shutil
import json
from pathlib import Path


def calculator_tool(expression: str):
    """Safely evaluate basic math expressions."""
    import re
    try:
        if not re.match(r'^[0-9+\-*/().\s]+$', expression):
            return {"error": "Invalid characters in expression"}
        result = eval(expression)
        return {"result": result, "expression": expression}
    except Exception as e:
        return {"error": f"Error calculating: {str(e)}"}


def system_tool(command_type: str):
    """Execute safe system commands."""
    import platform
    try:
        if command_type == "disk_usage":
            total, used, free = shutil.disk_usage("/")
            return {
                "total_gb": round(total / (1024**3), 2),
                "used_gb": round(used / (1024**3), 2),
                "free_gb": round(free / (1024**3), 2),
                "percent_used": round((used / total) * 100, 2)
            }
        elif command_type == "os_info":
            return {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine()
            }
        else:
            return {"error": f"Unknown command: {command_type}"}
    except Exception as e:
        return {"error": f"System command failed: {str(e)}"}


def file_organizer_tool(folder_path: str):
    """Organizes files in a folder by their type."""
    file_categories = {
        "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp"],
        "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf"],
        "Data": [".csv", ".xls", ".xlsx", ".json", ".xml"],
        "Videos": [".mp4", ".avi", ".mkv", ".mov"],
        "Audio": [".mp3", ".wav", ".flac", ".aac"],
        "Archives": [".zip", ".rar", ".7z", ".tar"],
        "Code": [".py", ".js", ".html", ".css", ".java"],
    }

    target_folder = Path(folder_path).expanduser().resolve()

    if not target_folder.exists():
        return {"error": f"Folder not found: {folder_path}"}

    files = [f for f in target_folder.iterdir() if f.is_file()]

    if not files:
        return {"message": "No files to organize", "organized": {}}

    organized = {}

    for file_path in files:
        file_ext = file_path.suffix.lower()
        file_name = file_path.name

        categorized = False
        for category, extensions in file_categories.items():
            if file_ext in extensions:
                category_folder = target_folder / category
                category_folder.mkdir(exist_ok=True)
                destination = category_folder / file_name

                counter = 1
                while destination.exists():
                    stem = file_path.stem
                    destination = category_folder / f"{stem}_{counter}{file_ext}"
                    counter += 1

                shutil.move(str(file_path), str(destination))

                if category not in organized:
                    organized[category] = []
                organized[category].append(file_name)
                categorized = True
                break

        if not categorized:
            others_folder = target_folder / "Others"
            others_folder.mkdir(exist_ok=True)
            destination = others_folder / file_name
            shutil.move(str(file_path), str(destination))
            if "Others" not in organized:
                organized["Others"] = []
            organized["Others"].append(file_name)

    return {
        "message": f"Organized {len(files)} files",
        "folder": str(target_folder),
        "organized": organized
    }


def list_directory_tool(path: str = "."):
    """List files and folders in a directory."""
    try:
        target = Path(path).expanduser().resolve()
        if not target.exists():
            return {"error": f"Path not found: {path}"}

        items = []
        for item in target.iterdir():
            item_type = "folder" if item.is_dir() else "file"
            items.append({
                "name": item.name,
                "type": item_type,
                "size": item.stat().st_size if item.is_file() else None
            })

        return {
            "path": str(target),
            "items": items,
            "total": len(items)
        }
    except Exception as e:
        return {"error": f"Failed to list directory: {str(e)}"}


TOOL_REGISTRY = {
    "calculator": calculator_tool,
    "system": system_tool,
    "file_organizer": file_organizer_tool,
    "list_directory": list_directory_tool,
}


def get_tool(name: str):
    """Get a tool by name."""
    return TOOL_REGISTRY.get(name)


def list_tools():
    """List all available tools."""
    return list(TOOL_REGISTRY.keys())
