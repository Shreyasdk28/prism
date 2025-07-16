import threading
import os
import json
from datetime import datetime
from pymongo import MongoClient

# File where episodic memory is stored

class MemoryManager:
    """
    Singleton manager for handling short-term, episodic, and long-term memory.
    """

    def __init__(self):
        self.short_term = {}  # Short-term memory
        try:
            # MongoDB connection
            self.client = MongoClient(os.getenv("MONGODB_URI"))
            self.db = self.client.shop_agent
            self.preferences_collection = self.db.user_preferences
            
            # Test connection
            self.client.admin.command('ping')
            print("✅ Connected to MongoDB successfully")
            
            # Create indexes for better performance
            self.preferences_collection.create_index("item_name")
            self.preferences_collection.create_index("timestamp")
            
        except Exception as e:
            print(f"❌ MongoDB connection failed: {e}")
            print("📝 Falling back to file-based storage...")
            self.client = None
            self.db = None
            self.preferences_collection = None
            
            # Create knowledge directory if it doesn't exist
            os.makedirs("knowledge", exist_ok=True)
    
    def get_user_preferences(self, item_name: str = None):
        """Get user preferences - MongoDB first, fallback to file"""
        try:
            if self.preferences_collection is not None:
                # MongoDB approach
                if item_name:
                    prefs = self.preferences_collection.find_one({"item_name": item_name})
                    if prefs:
                        prefs.pop('_id', None)
                        return prefs
                    return None
                else:
                    all_prefs = list(self.preferences_collection.find())
                    for pref in all_prefs:
                        pref.pop('_id', None)
                    return all_prefs
            else:
                # File-based fallback
                return self._get_preferences_from_file(item_name)
                
        except Exception as e:
            print(f"Error retrieving preferences: {e}")
            return self._get_preferences_from_file(item_name)
    
    def _get_preferences_from_file(self, item_name: str = None):
        """Fallback method to get preferences from file"""
        path = "knowledge/user_preferences.json"
        if not os.path.exists(path):
            return None
        try:
            with open(path, 'r') as f:
                all_prefs = json.load(f)
            if item_name:
                return all_prefs.get(item_name)
            return all_prefs
        except json.JSONDecodeError:
            return None
    
    def save_user_preferences(self, item_name: str, preferences: dict):
        """Save or update user preferences"""
        try:
            if self.preferences_collection is not None:
                # MongoDB approach
                preferences['timestamp'] = datetime.now().isoformat()
                preferences['item_name'] = item_name
                
                result = self.preferences_collection.update_one(
                    {"item_name": item_name},
                    {"$set": preferences},
                    upsert=True
                )
                
                if result.upserted_id:
                    print(f"✅ New preferences saved for {item_name}")
                else:
                    print(f"✅ Preferences updated for {item_name}")
                
                return True
            else:
                # File-based fallback
                return self._save_preferences_to_file(item_name, preferences)
                
        except Exception as e:
            print(f"Error saving preferences: {e}")
            return self._save_preferences_to_file(item_name, preferences)
    
    def _save_preferences_to_file(self, item_name: str, preferences: dict):
        """Fallback method to save preferences to file"""
        path = "knowledge/user_preferences.json"
        try:
            # Load existing preferences
            if os.path.exists(path):
                with open(path, 'r') as f:
                    all_prefs = json.load(f)
            else:
                all_prefs = {}
            
            # Add timestamp
            preferences['timestamp'] = datetime.now().isoformat()
            
            # Update preferences
            all_prefs[item_name] = preferences
            
            # Save back to file
            with open(path, 'w') as f:
                json.dump(all_prefs, f, indent=2)
            
            print(f"✅ Preferences saved to file for {item_name}")
            return True
            
        except Exception as e:
            print(f"Error saving preferences to file: {e}")
            return False
    
    def delete_preferences(self, item_name: str = None):
        """Delete preferences"""
        try:
            if self.preferences_collection is not None:
                # MongoDB approach
                if item_name:
                    result = self.preferences_collection.delete_one({"item_name": item_name})
                    print(f"Deleted {result.deleted_count} preference(s) for {item_name}")
                else:
                    result = self.preferences_collection.delete_many({})
                    print(f"Deleted {result.deleted_count} preference(s)")
                return True
            else:
                # File-based fallback
                return self._delete_preferences_from_file(item_name)
                
        except Exception as e:
            print(f"Error deleting preferences: {e}")
            return False
    
    def _delete_preferences_from_file(self, item_name: str = None):
        """Fallback method to delete preferences from file"""
        path = "knowledge/user_preferences.json"
        try:
            if not os.path.exists(path):
                return True
            
            with open(path, 'r') as f:
                all_prefs = json.load(f)
            
            if item_name:
                if item_name in all_prefs:
                    del all_prefs[item_name]
                    print(f"Deleted preferences for {item_name}")
            else:
                all_prefs = {}
                print("Deleted all preferences")
            
            with open(path, 'w') as f:
                json.dump(all_prefs, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error deleting preferences from file: {e}")
            return False
    
    def get_preferences_history(self, item_name: str = None, limit: int = 10):
        """Get historical preferences"""
        try:
            if self.preferences_collection is not None:
                # MongoDB approach
                query = {}
                if item_name:
                    query["item_name"] = item_name
                
                history = list(self.preferences_collection.find(query)
                              .sort("timestamp", -1)
                              .limit(limit))
                
                for pref in history:
                    pref.pop('_id', None)
                
                return history
            else:
                # File-based fallback - just return current preferences
                prefs = self.get_user_preferences(item_name)
                return [prefs] if prefs else []
                
        except Exception as e:
            print(f"Error retrieving preferences history: {e}")
            return []
    
    def close_connection(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            print("🔌 MongoDB connection closed")

    # --------------------
    # Short-term memory
    # --------------------
    def write_short(self, key: str, value):
        """Write a key-value pair into short-term memory."""
        self.short_term[key] = value

    def read_short(self, key: str):
        """Read a value from short-term memory."""
        return self.short_term.get(key)

    def clear_short(self):
        """Clear all short-term memory."""
        self.short_term.clear()

# Provide a module-level singleton instance
memory_manager = MemoryManager()
