from pymongo import MongoClient
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

class MongoMemoryManager:
    def __init__(self):
        # MongoDB connection
        self.client = MongoClient(os.getenv("MONGODB_URI"))
        self.db = self.client.shopping_agent
        self.preferences_collection = self.db.user_preferences
        
        # Create indexes for better performance
        self.preferences_collection.create_index("item_name")
        self.preferences_collection.create_index("timestamp")
    
    def get_user_preferences(self, item_name: str = None):
        """Get user preferences from MongoDB"""
        try:
            if item_name:
                # Get preferences for specific item
                prefs = self.preferences_collection.find_one({"item_name": item_name})
                if prefs:
                    # Remove MongoDB's _id field
                    prefs.pop('_id', None)
                    return prefs
                return None
            else:
                # Get all preferences
                all_prefs = list(self.preferences_collection.find())
                # Remove MongoDB's _id field from all documents
                for pref in all_prefs:
                    pref.pop('_id', None)
                return all_prefs
        except Exception as e:
            print(f"Error retrieving preferences: {e}")
            return None
    
    def save_user_preferences(self, item_name: str, preferences: dict):
        """Save or update user preferences in MongoDB"""
        try:
            # Add timestamp
            preferences['timestamp'] = datetime.now().isoformat()
            preferences['item_name'] = item_name
            
            # Update or insert preferences
            result = self.preferences_collection.update_one(
                {"item_name": item_name},
                {"$set": preferences},
                upsert=True
            )
            
            if result.upserted_id:
                print(f"New preferences saved for {item_name}")
            else:
                print(f"Preferences updated for {item_name}")
            
            return True
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return False
    
    def delete_preferences(self, item_name: str = None):
        """Delete preferences from MongoDB"""
        try:
            if item_name:
                # Delete specific item preferences
                result = self.preferences_collection.delete_one({"item_name": item_name})
                print(f"Deleted {result.deleted_count} preference(s) for {item_name}")
            else:
                # Delete all preferences
                result = self.preferences_collection.delete_many({})
                print(f"Deleted {result.deleted_count} preference(s)")
            return True
        except Exception as e:
            print(f"Error deleting preferences: {e}")
            return False
    
    def get_preferences_history(self, item_name: str = None, limit: int = 10):
        """Get historical preferences (if you want to track changes over time)"""
        try:
            query = {}
            if item_name:
                query["item_name"] = item_name
            
            # Get recent preferences sorted by timestamp
            history = list(self.preferences_collection.find(query)
                          .sort("timestamp", -1)
                          .limit(limit))
            
            # Remove MongoDB's _id field
            for pref in history:
                pref.pop('_id', None)
            
            return history
        except Exception as e:
            print(f"Error retrieving preferences history: {e}")
            return []
    
    def close_connection(self):
        """Close MongoDB connection"""
        self.client.close()

# Global instance
memory_manager = MongoMemoryManager()