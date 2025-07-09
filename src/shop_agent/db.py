import os
import logging
import threading
from typing import Dict, Any, Optional, List
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MongoDBClient:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(MongoDBClient, cls).__new__(cls)
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
            self.client = MongoClient(
                self.mongo_uri,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=1
            )
            self.client.admin.command('ping')
            logger.info("MongoDB connection established successfully.")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"MongoDB connection failed: {e}")
            self.client = None

    def get_database(self):
        if self.client:
            return self.client[self.db_name]
        else:
            logger.error("No MongoDB client available.")
            return None

    def insert_one(self, collection: str, data: Dict[str, Any]) -> Optional[str]:
        db = self.get_database()
        if db:
            result = db[collection].insert_one(data)
            logger.info(f"Inserted document with id: {result.inserted_id}")
            return str(result.inserted_id)
        return None

    def insert_output(self, collection: str, data: Dict[str, Any]):
        db = self.get_database()
        if db:
            result = db[collection].insert_one(data)
            logger.info(f"Output inserted with id: {result.inserted_id}")
            return result
        return None

    def find(self, collection: str, query: Dict[str, Any]) -> List[Dict[str, Any]]:
        db = self.get_database()
        if db:
            return list(db[collection].find(query))
        return []

    def close(self):
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")
