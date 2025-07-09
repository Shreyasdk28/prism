import os
import logging
import threading
from typing import Dict, Any, List, Optional
from datetime import datetime
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId

# Load environment variables early
load_dotenv()

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def sanitize_mongo_doc(doc):
    """Convert all ObjectId fields to str for JSON serialization."""
    doc = dict(doc)
    for k, v in doc.items():
        if isinstance(v, ObjectId):
            doc[k] = str(v)
    return doc

class MongoMemoryManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MongoMemoryManager, cls).__new__(cls)
                cls._instance._initialize()
        return cls._instance

    def _initialize(self):
        self.mongo_uri = os.getenv("MONGO_URI")
        self.db_name = os.getenv("MONGO_DB_NAME", "shopping_ai")
        if not self.mongo_uri:
            logger.error("MONGO_URI not found in environment variables.")
            self.client = None
            return
        try:
            self.client = MongoClient(self.mongo_uri)
            self.db = self.client[self.db_name]
            self.short_term_collection = self.db["short_term_memory"]
            self.episodic_collection = self.db["episodic_memory"]
            self.long_term_collection = self.db["long_term_memory"]
            self.messages_collection = self.db["agent_messages"]
            self.shared_data_collection = self.db["shared_data"]
            logger.info("MongoDB memory manager initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {e}")
            self.client = None

    # Short-term memory
    def write_short(self, key: str, value: Any) -> bool:
        try:
            self.short_term_collection.replace_one(
                {"key": key},
                {"key": key, "value": value, "timestamp": datetime.utcnow()},
                upsert=True
            )
            logger.debug(f"Short-term memory updated: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to write short-term memory {key}: {e}")
            return False

    def read_short(self, key: str) -> Optional[Any]:
        try:
            doc = self.short_term_collection.find_one({"key": key})
            return doc.get("value") if doc else None
        except Exception as e:
            logger.error(f"Failed to read short-term memory {key}: {e}")
            return None

    def clear_short(self) -> bool:
        try:
            self.short_term_collection.delete_many({})
            logger.info("Short-term memory cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear short-term memory: {e}")
            return False

    def get_short_term_summary(self) -> Dict[str, Any]:
        try:
            docs = list(self.short_term_collection.find({}))
            return {
                "total_items": len(docs),
                "keys": [doc["key"] for doc in docs],
                "last_updated": max([doc["timestamp"] for doc in docs], default=None)
            }
        except Exception as e:
            logger.error(f"Failed to get short-term summary: {e}")
            return {'total_items': 0, 'keys': [], 'last_updated': None}

    # Episodic memory
    def append_episode(self, episode_data: Dict[str, Any]) -> bool:
        try:
            if not all(k in episode_data for k in ["user_id", "query", "final_items"]):
                logger.error("Episode missing required fields")
                return False
            episode_data.setdefault("timestamp", datetime.utcnow().isoformat())
            self.episodic_collection.insert_one(episode_data)
            logger.info(f"Episode appended for user {episode_data.get('user_id')}")
            return True
        except Exception as e:
            logger.error(f"Failed to append episode: {e}")
            return False

    def get_episodes(self, user_id: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        try:
            query = {"user_id": user_id} if user_id else {}
            cursor = self.episodic_collection.find(query).sort("timestamp", -1)
            if limit:
                cursor = cursor.limit(limit)
            episodes = [sanitize_mongo_doc(ep) for ep in cursor]
            logger.debug(f"Retrieved {len(episodes)} episodes for user {user_id}")
            return episodes
        except Exception as e:
            logger.error(f"Failed to get episodes: {e}")
            return []

    def clear_episodes(self) -> bool:
        try:
            self.episodic_collection.delete_many({})
            logger.info("Episodic memory cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear episodes: {e}")
            return False

    # Long-term memory
    def write_long(self, user_id: str, key: str, value: Any) -> bool:
        try:
            self.long_term_collection.update_one(
                {"user_id": user_id, "key": key},
                {"$set": {"user_id": user_id, "key": key, "value": value, "timestamp": datetime.utcnow()}},
                upsert=True
            )
            logger.debug(f"Long-term memory updated for user {user_id}: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to write long-term memory: {e}")
            return False

    def read_long(self, user_id: str, key: str) -> Optional[Any]:
        try:
            doc = self.long_term_collection.find_one({"user_id": user_id, "key": key})
            return doc.get("value") if doc else None
        except Exception as e:
            logger.error(f"Failed to read long-term memory: {e}")
            return None

    # Messaging
    def send_message(self, from_agent: str, to_agent: str, message: str) -> bool:
        try:
            self.messages_collection.insert_one({
                "from_agent": from_agent,
                "to_agent": to_agent,
                "message": message,
                "timestamp": datetime.utcnow()
            })
            logger.debug(f"Message sent from {from_agent} to {to_agent}")
            return True
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            return False

    def get_messages(self, agent_name: str) -> List[Dict[str, Any]]:
        try:
            msgs = [sanitize_mongo_doc(m) for m in self.messages_collection.find({"to_agent": agent_name})]
            self.messages_collection.delete_many({"to_agent": agent_name})
            logger.debug(f"Retrieved {len(msgs)} messages for {agent_name}")
            return msgs
        except Exception as e:
            logger.error(f"Failed to get messages for {agent_name}: {e}")
            return []

    # Shared data
    def share_data(self, key: str, value: Any) -> bool:
        try:
            self.shared_data_collection.replace_one(
                {"key": key},
                {"key": key, "value": value, "timestamp": datetime.utcnow()},
                upsert=True
            )
            logger.debug(f"Data shared: {key}")
            return True
        except Exception as e:
            logger.error(f"Failed to share data {key}: {e}")
            return False

    def get_shared_data(self, key: str) -> Optional[Any]:
        try:
            doc = self.shared_data_collection.find_one({"key": key})
            return doc.get("value") if doc else None
        except Exception as e:
            logger.error(f"Failed to get shared data {key}: {e}")
            return None

    def clear_shared_data(self) -> bool:
        try:
            self.shared_data_collection.delete_many({})
            logger.info("Shared data cleared")
            return True
        except Exception as e:
            logger.error(f"Failed to clear shared data: {e}")
            return False

memory_manager = MongoMemoryManager()
