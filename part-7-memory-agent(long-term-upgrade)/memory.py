"""
Long-Term Memory Module - Vector-based persistent storage
"""
import json
import hashlib
import numpy as np
from pathlib import Path
from datetime import datetime


class LongTermMemory:
    """
    Long-term memory using simple vector similarity.
    Stores memories with embeddings for semantic search.
    """

    def __init__(self, storage_path="memory_store.json", max_results=3):
        """
        Initialize long-term memory.

        Args:
            storage_path: File to persist memories
            max_results: Maximum similar memories to retrieve
        """
        self.storage_path = Path(storage_path)
        self.max_results = max_results
        self.memories = []
        self._load()

    def _load(self):
        """Load memories from disk."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.memories = data.get('memories', [])
            except Exception as e:
                print(f"Warning: Could not load memory: {e}")
                self.memories = []
        else:
            self.memories = []

    def _save(self):
        """Save memories to disk."""
        try:
            with open(self.storage_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'memories': self.memories,
                    'metadata': {
                        'count': len(self.memories),
                        'last_updated': datetime.now().isoformat()
                    }
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save memory: {e}")

    def _simple_embedding(self, text: str) -> list:
        """
        Create a simple embedding from text.
        This is a basic implementation using character frequencies.
        In production, use proper embeddings (OpenAI, HuggingFace, etc.)
        """
        # Normalize text
        text = text.lower().strip()

        # Character frequency vector (simplified)
        char_vector = np.zeros(256)
        for char in text:
            char_vector[ord(char) % 256] += 1

        # Word-based features
        words = text.split()
        word_count = len(words)
        avg_word_len = sum(len(w) for w in words) / max(word_count, 1)

        # Combine features
        features = list(char_vector[:64])  # First 64 char frequencies
        features.extend([word_count, avg_word_len, len(text)])

        # Normalize
        norm = np.linalg.norm(features)
        if norm > 0:
            features = [f / norm for f in features]

        return features

    def _cosine_similarity(self, vec1: list, vec2: list) -> float:
        """Calculate cosine similarity between two vectors."""
        v1 = np.array(vec1)
        v2 = np.array(vec2)
        dot = np.dot(v1, v2)
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        if norm1 == 0 or norm2 == 0:
            return 0
        return dot / (norm1 * norm2)

    def add(self, content: str, memory_type: str = "fact", metadata: dict = None):
        """
        Add a memory to long-term storage.

        Args:
            content: The text to remember
            memory_type: Type of memory (fact, preference, event, etc.)
            metadata: Additional data to store
        """
        memory = {
            'id': hashlib.md5(content.encode()).hexdigest()[:8],
            'content': content,
            'type': memory_type,
            'embedding': self._simple_embedding(content),
            'timestamp': datetime.now().isoformat(),
            'metadata': metadata or {}
        }

        # Check for duplicates
        existing_ids = [m['id'] for m in self.memories]
        if memory['id'] not in existing_ids:
            self.memories.append(memory)
            self._save()
            return True
        return False

    def search(self, query: str, threshold: float = 0.5) -> list:
        """
        Search for similar memories.

        Args:
            query: Search query
            threshold: Minimum similarity score (0-1)

        Returns:
            List of similar memories sorted by relevance
        """
        if not self.memories:
            return []

        query_embedding = self._simple_embedding(query)

        # Calculate similarity for all memories
        scored_memories = []
        for memory in self.memories:
            similarity = self._cosine_similarity(
                query_embedding,
                memory['embedding']
            )
            if similarity >= threshold:
                scored_memories.append({
                    **memory,
                    'similarity': round(similarity, 3)
                })

        # Sort by similarity (highest first)
        scored_memories.sort(key=lambda x: x['similarity'], reverse=True)

        return scored_memories[:self.max_results]

    def get_all(self, memory_type: str = None) -> list:
        """Get all memories, optionally filtered by type."""
        if memory_type:
            return [m for m in self.memories if m['type'] == memory_type]
        return self.memories.copy()

    def get_by_id(self, memory_id: str) -> dict:
        """Get a specific memory by ID."""
        for memory in self.memories:
            if memory['id'] == memory_id:
                return memory
        return None

    def delete(self, memory_id: str) -> bool:
        """Delete a memory by ID."""
        for i, memory in enumerate(self.memories):
            if memory['id'] == memory_id:
                self.memories.pop(i)
                self._save()
                return True
        return False

    def clear(self):
        """Clear all memories."""
        self.memories = []
        self._save()

    def get_stats(self) -> dict:
        """Get memory statistics."""
        types = {}
        for m in self.memories:
            t = m['type']
            types[t] = types.get(t, 0) + 1

        return {
            'total_memories': len(self.memories),
            'storage_file': str(self.storage_path),
            'types': types
        }


class HybridMemory:
    """
    Combines short-term and long-term memory.
    Short-term: Recent conversation
    Long-term: Persistent storage with semantic search
    """

    def __init__(self, short_term_limit=10, long_term_file="memory_store.json"):
        from memory_short import ConversationMemory
        self.short_term = ConversationMemory(max_history=short_term_limit)
        self.long_term = LongTermMemory(storage_path=long_term_file)

    def add_interaction(self, user_message: str, assistant_response: str, store_long_term: bool = True):
        """
        Add an interaction to both memories.

        Args:
            user_message: What the user said
            assistant_response: How the agent responded
            store_long_term: Whether to store in long-term memory
        """
        # Always add to short-term
        self.short_term.add_user_message(user_message)
        self.short_term.add_assistant_message(assistant_response)

        # Optionally store important info in long-term
        if store_long_term:
            # Store user preferences and facts
            self._extract_and_store(user_message)

    def _extract_and_store(self, message: str):
        """Extract important information and store in long-term memory."""
        # Simple extraction - in production, use LLM to extract facts
        important_patterns = [
            (r'(?:my name is|i am|call me)\s+(\w+)', 'name'),
            (r'(?:my favorite|i like|i prefer|i love)\s+(.+)', 'preference'),
            (r'(?:i work at|my company is|i work for)\s+(.+)', 'work'),
            (r'(?:i live in|my city is|i am from)\s+(.+)', 'location'),
        ]

        import re
        for pattern, mem_type in important_patterns:
            match = re.search(pattern, message.lower())
            if match:
                content = match.group(0)
                self.long_term.add(content, memory_type=mem_type)

    def get_context(self, query: str = None) -> dict:
        """
        Get combined context from both memories.

        Args:
            query: Optional query to search long-term memory

        Returns:
            Dictionary with short_term and long_term contexts
        """
        context = {
            'short_term': self.short_term.get_context_string(),
            'long_term': []
        }

        # Search long-term memory if query provided
        if query:
            relevant_memories = self.long_term.search(query)
            context['long_term'] = relevant_memories

        return context

    def clear_short_term(self):
        """Clear only short-term memory."""
        self.short_term.clear()

    def clear_all(self):
        """Clear both memories."""
        self.short_term.clear()
        self.long_term.clear()
