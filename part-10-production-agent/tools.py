"""
Production Tools Module - Safe, timeout-aware tools
"""
import shutil
import platform
import time
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def check_disk_space() -> Dict:
    """
    Check system disk space with error handling.
    """
    try:
        logger.info("Checking disk space...")
        
        # Get disk usage
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
        
        result = {
            "status": status,
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_used": round(percent_used, 2),
            "message": _get_disk_message(status, percent_used),
            "needs_action": status in ["warning", "critical"],
            "timestamp": time.time()
        }
        
        logger.info(f"Disk check complete: {status} ({percent_used:.1f}% used)")
        return result
        
    except Exception as e:
        logger.error(f"Disk check failed: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
            "message": f"Failed to check disk: {str(e)}",
            "needs_action": False
        }


def _get_disk_message(status: str, percent: float) -> str:
    """Get appropriate message for disk status."""
    messages = {
        "critical": f"CRITICAL: Disk is {percent:.1f}% full! Immediate action required.",
        "warning": f"WARNING: Disk is {percent:.1f}% full. Consider cleaning up files.",
        "good": f"Disk is healthy ({percent:.1f}% used).",
        "error": "Could not determine disk status."
    }
    return messages.get(status, "Unknown status")


def suggest_organize() -> Dict:
    """
    Suggest folders to organize based on size.
    """
    try:
        logger.info("Analyzing folders for organization suggestions...")
        
        suggestions = []
        folders_to_check = [
            ("Downloads", Path.home() / "Downloads"),
            ("Desktop", Path.home() / "Desktop"),
            ("Documents", Path.home() / "Documents"),
            ("Pictures", Path.home() / "Pictures"),
            ("Videos", Path.home() / "Videos"),
        ]
        
        for name, path in folders_to_check:
            if not path.exists():
                continue
                
            try:
                total_size = 0
                file_count = 0
                
                # Limit iteration for performance
                for i, item in enumerate(path.iterdir()):
                    if i > 1000:  # Safety limit
                        break
                    
                    if item.is_file():
                        try:
                            total_size += item.stat().st_size
                            file_count += 1
                        except (OSError, PermissionError):
                            continue
                    elif item.is_dir():
                        # One level deep only for performance
                        for subitem in item.iterdir():
                            if subitem.is_file():
                                try:
                                    total_size += subitem.stat().st_size
                                    file_count += 1
                                except (OSError, PermissionError):
                                    continue
                
                size_mb = round(total_size / (1024**2), 2)
                
                if size_mb > 50:  # Only suggest if > 50MB
                    suggestions.append({
                        "folder": name,
                        "path": str(path),
                        "size_mb": size_mb,
                        "file_count": file_count,
                        "priority": "high" if size_mb > 500 else "medium"
                    })
                    
            except PermissionError:
                logger.warning(f"Permission denied accessing {path}")
                continue
            except Exception as e:
                logger.warning(f"Error analyzing {path}: {str(e)}")
                continue
        
        suggestions.sort(key=lambda x: x["size_mb"], reverse=True)
        
        logger.info(f"Found {len(suggestions)} folders to suggest")
        
        return {
            "suggestions": suggestions[:5],
            "total_suggestions": len(suggestions),
            "message": f"Found {len(suggestions)} folders that could be organized."
        }
        
    except Exception as e:
        logger.error(f"Suggest organize failed: {str(e)}")
        return {
            "suggestions": [],
            "total_suggestions": 0,
            "message": f"Error analyzing folders: {str(e)}"
        }


def file_organizer(folder_path: str) -> Dict:
    """
    Organize files in a folder by type with comprehensive error handling.
    """
    try:
        logger.info(f"Organizing files in: {folder_path}")
        
        target = Path(folder_path).expanduser().resolve()
        
        if not target.exists():
            logger.error(f"Folder not found: {target}")
            return {
                "error": f"Folder not found: {folder_path}",
                "success": False
            }
        
        if not target.is_dir():
            return {
                "error": f"Path is not a directory: {folder_path}",
                "success": False
            }
        
        # File type categories
        categories = {
            "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico"],
            "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".md", ".odt"],
            "Data": [".csv", ".xls", ".xlsx", ".json", ".xml", ".yaml", ".yml"],
            "Videos": [".mp4", ".avi", ".mkv", ".mov", ".wmv", ".flv"],
            "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".m4a"],
            "Archives": [".zip", ".rar", ".7z", ".tar", ".gz", ".bz2"],
            "Code": [".py", ".js", ".html", ".css", ".java", ".cpp", ".c", ".h", ".php"],
            "Executables": [".exe", ".msi", ".dmg", ".pkg"]
        }
        
        files_moved = 0
        organized = {}
        errors = []
        
        # Get files (limit for safety)
        files = [f for f in target.iterdir() if f.is_file()][:1000]
        
        for file_path in files:
            try:
                ext = file_path.suffix.lower()
                file_name = file_path.name
                
                # Find category
                categorized = False
                for category, extensions in categories.items():
                    if ext in extensions:
                        category_dir = target / category
                        
                        try:
                            category_dir.mkdir(exist_ok=True)
                        except PermissionError:
                            errors.append(f"Permission denied creating {category_dir}")
                            continue
                        
                        destination = category_dir / file_name
                        
                        # Handle duplicates
                        counter = 1
                        original_destination = destination
                        while destination.exists():
                            stem = file_path.stem
                            destination = category_dir / f"{stem}_{counter}{ext}"
                            counter += 1
                            
                            if counter > 100:  # Safety limit
                                errors.append(f"Too many duplicates for {file_name}")
                                break
                        
                        if counter > 100:
                            continue
                        
                        # Move file
                        try:
                            shutil.move(str(file_path), str(destination))
                            
                            if category not in organized:
                                organized[category] = []
                            organized[category].append(file_name)
                            files_moved += 1
                            categorized = True
                            
                        except PermissionError:
                            errors.append(f"Permission denied moving {file_name}")
                            continue
                        except Exception as e:
                            errors.append(f"Error moving {file_name}: {str(e)}")
                            continue
                        
                        break
                
                if not categorized:
                    # Move to Others
                    others_dir = target / "Others"
                    try:
                        others_dir.mkdir(exist_ok=True)
                        destination = others_dir / file_name
                        shutil.move(str(file_path), str(destination))
                        
                        if "Others" not in organized:
                            organized["Others"] = []
                        organized["Others"].append(file_name)
                        files_moved += 1
                    except Exception as e:
                        errors.append(f"Error moving {file_name} to Others: {str(e)}")
                        
            except Exception as e:
                errors.append(f"Error processing {file_path.name}: {str(e)}")
                continue
        
        logger.info(f"Organized {files_moved} files into {len(organized)} categories")
        
        result = {
            "success": True,
            "folder": str(target),
            "files_moved": files_moved,
            "organized": organized,
            "message": f"Organized {files_moved} files into {len(organized)} categories."
        }
        
        if errors:
            result["warnings"] = errors[:10]  # Limit error messages
            result["total_errors"] = len(errors)
        
        return result
        
    except Exception as e:
        logger.exception("File organizer failed")
        return {
            "error": str(e),
            "success": False
        }


def system_info() -> Dict:
    """
    Get system information safely.
    """
    try:
        logger.info("Gathering system information...")
        
        result = {
            "os": platform.system(),
            "os_version": platform.release(),
            "platform": platform.platform(),
            "processor": platform.processor() or "Unknown",
            "architecture": platform.architecture()[0],
            "python_version": platform.python_version(),
            "machine": platform.machine(),
            "node": platform.node(),
            "message": f"Running on {platform.system()} {platform.release()}"
        }
        
        logger.info(f"System info gathered: {result['os']} {result['os_version']}")
        return result
        
    except Exception as e:
        logger.error(f"System info failed: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to gather system information"
        }


def calculator(expression: str) -> Dict:
    """
    Safely evaluate a math expression.
    """
    import re
    
    try:
        logger.info(f"Calculating: {expression}")
        
        # Validate expression
        if not expression:
            return {
                "error": "Empty expression",
                "success": False
            }
        
        # Only allow safe characters
        if not re.match(r'^[0-9+\-*/().\s]+$', expression):
            return {
                "error": "Invalid characters in expression. Only numbers and operators allowed.",
                "success": False
            }
        
        # Check for dangerous patterns
        dangerous = ['__', 'import', 'eval', 'exec', 'compile', 'open']
        for d in dangerous:
            if d in expression.lower():
                return {
                    "error": f"Dangerous pattern detected: {d}",
                    "success": False
                }
        
        try:
            result = eval(expression, {"__builtins__": {}}, {})
            
            logger.info(f"Calculation result: {result}")
            
            return {
                "success": True,
                "expression": expression,
                "result": result,
                "message": f"{expression} = {result}"
            }
        except ZeroDivisionError:
            return {
                "error": "Division by zero",
                "success": False
            }
        except Exception as e:
            return {
                "error": f"Calculation error: {str(e)}",
                "success": False
            }
            
    except Exception as e:
        logger.error(f"Calculator failed: {str(e)}")
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
    tool = TOOL_REGISTRY.get(name)
    if tool:
        logger.debug(f"Tool retrieved: {name}")
    else:
        logger.warning(f"Tool not found: {name}")
    return tool


def list_tools():
    """List all available tools."""
    return list(TOOL_REGISTRY.keys())
