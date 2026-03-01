"""
Memory System - Short-term and long-term memory with ChromaDB.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    EMBEDDINGS_AVAILABLE = True
except ImportError:
    EMBEDDINGS_AVAILABLE = False

from ..utils.config import config
from ..utils.logger import logger


class ShortTermMemory:
    """In-memory conversation buffer."""
    
    def __init__(self, max_items: int = None):
        self.max_items = max_items or config.MAX_SHORT_TERM_MEMORY
        self.buffer: List[Dict[str, Any]] = []
    
    def add(self, item_type: str, content: Any, metadata: Dict = None):
        """Add item to short-term memory."""
        item = {
            "id": str(uuid.uuid4()),
            "type": item_type,
            "content": content,
            "timestamp": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.buffer.append(item)
        
        # Keep only recent items
        if len(self.buffer) > self.max_items:
            self.buffer = self.buffer[-self.max_items:]
        
        return item["id"]
    
    def get_recent(self, n: int = None) -> List[Dict[str, Any]]:
        """Get recent items."""
        n = n or self.max_items
        return self.buffer[-n:]
    
    def get_by_type(self, item_type: str) -> List[Dict[str, Any]]:
        """Get items by type."""
        return [item for item in self.buffer if item["type"] == item_type]
    
    def clear(self):
        """Clear memory buffer."""
        self.buffer = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "max_items": self.max_items,
            "items": self.buffer
        }


class LongTermMemory:
    """Persistent memory using ChromaDB."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or config.CHROMA_DB_PATH
        self.client = None
        self.collection = None
        self.embedding_model = None
        
        self._init_db()
    
    def _init_db(self):
        """Initialize ChromaDB."""
        if not CHROMADB_AVAILABLE:
            logger.warning("ChromaDB not available. Long-term memory disabled.")
            return
        
        try:
            # Create directory
            Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Initialize client
            self.client = chromadb.Client(Settings(
                chroma_db_impl="duckdb+parquet",
                persist_directory=self.db_path
            ))
            
            # Get or create collection
            self.collection = self.client.get_or_create_collection(
                name="agent_memory",
                metadata={"description": "Agent long-term memory"}
            )
            
            logger.info(f"ChromaDB initialized at {self.db_path}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB: {str(e)}")
            self.client = None
            self.collection = None
    
    def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text."""
        if not EMBEDDINGS_AVAILABLE:
            # Return simple hash-based embedding as fallback
            return [hash(text) % 1000 / 1000.0] * 384
        
        if self.embedding_model is None:
            try:
                self.embedding_model = SentenceTransformer(config.EMBEDDING_MODEL)
            except Exception as e:
                logger.error(f"Failed to load embedding model: {str(e)}")
                return [0.0] * 384
        
        try:
            embedding = self.embedding_model.encode(text)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Failed to generate embedding: {str(e)}")
            return [0.0] * 384
    
    def store(
        self,
        content: str,
        memory_type: str,
        metadata: Dict = None,
        goal_id: str = None
    ) -> str:
        """Store item in long-term memory."""
        if not self.collection:
            logger.warning("Long-term memory not available, skipping store")
            return None
        
        memory_id = str(uuid.uuid4())
        
        document = {
            "content": content,
            "type": memory_type,
            "goal_id": goal_id,
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {})
        }
        
        try:
            self.collection.add(
                ids=[memory_id],
                documents=[content],
                metadatas=[document],
                embeddings=[self._get_embedding(content)]
            )
            
            logger.log_memory_store(goal_id, "long_term", memory_id)
            return memory_id
            
        except Exception as e:
            logger.error(f"Failed to store memory: {str(e)}")
            return None
    
    def retrieve(
        self,
        query: str,
        n_results: int = 5,
        memory_type: str = None
    ) -> List[Dict[str, Any]]:
        """Retrieve relevant memories."""
        if not self.collection:
            return []
        
        try:
            where_filter = {"type": memory_type} if memory_type else None
            
            results = self.collection.query(
                query_embeddings=[self._get_embedding(query)],
                n_results=n_results,
                where=where_filter
            )
            
            memories = []
            if results["ids"]:
                for i, memory_id in enumerate(results["ids"][0]):
                    memories.append({
                        "id": memory_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "distance": results["distances"][0][i] if "distances" in results else None
                    })
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to retrieve memories: {str(e)}")
            return []
    
    def get_by_goal(self, goal_id: str) -> List[Dict[str, Any]]:
        """Get all memories for a goal."""
        if not self.collection:
            return []
        
        try:
            results = self.collection.get(
                where={"goal_id": goal_id}
            )
            
            memories = []
            for i, memory_id in enumerate(results["ids"]):
                memories.append({
                    "id": memory_id,
                    "content": results["documents"][i],
                    "metadata": results["metadatas"][i]
                })
            
            return memories
            
        except Exception as e:
            logger.error(f"Failed to get memories by goal: {str(e)}")
            return []
    
    def persist(self):
        """Persist memory to disk."""
        if self.client:
            try:
                self.client.persist()
                logger.info("Memory persisted to disk")
            except Exception as e:
                logger.error(f"Failed to persist memory: {str(e)}")


class MemoryManager:
    """Manages both short-term and long-term memory."""
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
    
    def add_step_result(
        self,
        goal_id: str,
        step_number: int,
        result: Dict[str, Any]
    ):
        """Add step execution result."""
        # Short-term
        self.short_term.add(
            item_type="step_result",
            content=result,
            metadata={"goal_id": goal_id, "step_number": step_number}
        )
        
        # Long-term
        content = f"Step {step_number}: {result.get('output', '')}"
        self.long_term.store(
            content=content,
            memory_type="step_result",
            goal_id=goal_id,
            metadata={
                "step_number": step_number,
                "success": result.get("success", False)
            }
        )
    
    def add_goal(self, goal: str, goal_id: str):
        """Store goal information."""
        # Short-term
        self.short_term.add(
            item_type="goal",
            content=goal,
            metadata={"goal_id": goal_id}
        )
        
        # Long-term
        self.long_term.store(
            content=goal,
            memory_type="goal",
            goal_id=goal_id,
            metadata={"status": "started"}
        )
    
    def add_reflection(self, reflection: Dict[str, Any], goal_id: str):
        """Store reflection."""
        content = json.dumps(reflection)
        
        # Short-term
        self.short_term.add(
            item_type="reflection",
            content=reflection,
            metadata={"goal_id": goal_id}
        )
        
        # Long-term
        self.long_term.store(
            content=content,
            memory_type="reflection",
            goal_id=goal_id
        )
    
    def get_context_for_goal(self, goal_id: str) -> Dict[str, Any]:
        """Get memory context for a goal."""
        # Get recent short-term items
        recent = self.short_term.get_recent()
        
        # Get long-term memories
        long_term = self.long_term.get_by_goal(goal_id)
        
        return {
            "recent_short_term": recent,
            "long_term_memories": long_term
        }
    
    def persist(self):
        """Persist all memory."""
        self.long_term.persist()


# Global memory manager
memory_manager = MemoryManager()
