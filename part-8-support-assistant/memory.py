"""
Support Memory Module - Long-term memory for customer support
"""
import json
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class SupportMemory:
    """
    Specialized memory for support assistant.
    Stores: user profile, issues, preferences, and resolutions.
    """

    def __init__(self, storage_path="support_memory.json"):
        self.storage_path = Path(storage_path)
        self.data = {
            "user_profile": {},
            "issues": [],
            "preferences": {},
            "conversations": []
        }
        self._load()

    def _load(self):
        """Load memory from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    self.data.update(loaded)
            except Exception as e:
                print(f"Warning: Could not load memory: {e}")

    def _save(self):
        """Save memory to disk."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save memory: {e}")

    def set_user_name(self, name: str):
        """Store user's name."""
        self.data["user_profile"]["name"] = name
        self._save()

    def get_user_name(self) -> Optional[str]:
        """Retrieve user's name."""
        return self.data["user_profile"].get("name")

    def add_issue(self, issue_description: str, category: str = "general", status: str = "open"):
        """
        Record a new support issue.

        Args:
            issue_description: What the problem is
            category: Type of issue (disk, network, software, etc.)
            status: open, resolved, pending
        """
        issue = {
            "id": hashlib.md5(f"{issue_description}{datetime.now()}".encode()).hexdigest()[:8],
            "description": issue_description,
            "category": category.lower(),
            "status": status,
            "created_at": datetime.now().isoformat(),
            "resolved_at": None,
            "resolution": None
        }
        self.data["issues"].append(issue)
        self._save()
        return issue["id"]

    def get_issues(self, status: Optional[str] = None, category: Optional[str] = None) -> List[Dict]:
        """
        Get issues, optionally filtered by status or category.

        Args:
            status: Filter by 'open', 'resolved', 'pending'
            category: Filter by issue category
        """
        issues = self.data["issues"]

        if status:
            issues = [i for i in issues if i["status"] == status]
        if category:
            issues = [i for i in issues if i["category"] == category.lower()]

        return sorted(issues, key=lambda x: x["created_at"], reverse=True)

    def get_last_issue(self) -> Optional[Dict]:
        """Get the most recent issue."""
        if self.data["issues"]:
            return sorted(self.data["issues"], key=lambda x: x["created_at"])[-1]
        return None

    def resolve_issue(self, issue_id: str, resolution: str):
        """Mark an issue as resolved."""
        for issue in self.data["issues"]:
            if issue["id"] == issue_id:
                issue["status"] = "resolved"
                issue["resolution"] = resolution
                issue["resolved_at"] = datetime.now().isoformat()
                self._save()
                return True
        return False

    def set_preference(self, key: str, value: str):
        """Store a user preference."""
        self.data["preferences"][key] = {
            "value": value,
            "set_at": datetime.now().isoformat()
        }
        self._save()

    def get_preference(self, key: str) -> Optional[str]:
        """Get a user preference."""
        pref = self.data["preferences"].get(key)
        return pref["value"] if pref else None

    def get_all_preferences(self) -> Dict:
        """Get all user preferences."""
        return {k: v["value"] for k, v in self.data["preferences"].items()}

    def add_conversation(self, user_msg: str, assistant_msg: str):
        """Log conversation history."""
        self.data["conversations"].append({
            "timestamp": datetime.now().isoformat(),
            "user": user_msg,
            "assistant": assistant_msg
        })
        # Keep only last 50 conversations
        self.data["conversations"] = self.data["conversations"][-50:]
        self._save()

    def search_issues(self, query: str) -> List[Dict]:
        """Search issues by keyword."""
        query_lower = query.lower()
        matches = []
        for issue in self.data["issues"]:
            if (query_lower in issue["description"].lower() or
                query_lower in issue["category"].lower()):
                matches.append(issue)
        return matches

    def get_stats(self) -> Dict:
        """Get memory statistics."""
        issues = self.data["issues"]
        return {
            "user_name": self.get_user_name(),
            "total_issues": len(issues),
            "open_issues": len([i for i in issues if i["status"] == "open"]),
            "resolved_issues": len([i for i in issues if i["status"] == "resolved"]),
            "preferences_count": len(self.data["preferences"]),
            "conversations_count": len(self.data["conversations"])
        }

    def clear_all(self):
        """Clear all memory."""
        self.data = {
            "user_profile": {},
            "issues": [],
            "preferences": {},
            "conversations": []
        }
        self._save()

    def export_memory(self) -> Dict:
        """Export all memory data."""
        return self.data.copy()
