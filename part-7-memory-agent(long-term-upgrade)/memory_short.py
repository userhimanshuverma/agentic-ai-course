"""
Short-Term Memory Module - Conversation history (from Part 6)
"""


class ConversationMemory:
    """
    Simple in-memory conversation history.
    Stores messages in a list for short-term context.
    """

    def __init__(self, max_history=10):
        """
        Initialize memory with optional history limit.

        Args:
            max_history: Maximum number of exchanges to remember
        """
        self.history = []
        self.max_history = max_history

    def add_user_message(self, message: str):
        """Add a user message to history."""
        self.history.append({"role": "user", "content": message})
        self._trim_history()

    def add_assistant_message(self, message: str):
        """Add an assistant message to history."""
        self.history.append({"role": "assistant", "content": message})
        self._trim_history()

    def add_system_message(self, message: str):
        """Add a system message to history."""
        self.history.append({"role": "system", "content": message})

    def get_history(self):
        """Get full conversation history."""
        return self.history.copy()

    def get_recent(self, n=5):
        """Get last n messages."""
        return self.history[-n:] if self.history else []

    def get_context_string(self):
        """Get history as a formatted string for prompts."""
        context = []
        for msg in self.history:
            role = msg["role"].capitalize()
            content = msg["content"]
            context.append(f"{role}: {content}")
        return "\n".join(context)

    def clear(self):
        """Clear all history."""
        self.history = []

    def _trim_history(self):
        """Remove oldest messages if history exceeds max."""
        while len(self.history) > self.max_history * 2:
            for i, msg in enumerate(self.history):
                if msg["role"] != "system":
                    self.history.pop(i)
                    break

    def is_empty(self):
        """Check if memory is empty."""
        return len(self.history) == 0

    def get_last_user_message(self):
        """Get the most recent user message."""
        for msg in reversed(self.history):
            if msg["role"] == "user":
                return msg["content"]
        return None

    def get_last_assistant_message(self):
        """Get the most recent assistant message."""
        for msg in reversed(self.history):
            if msg["role"] == "assistant":
                return msg["content"]
        return None
