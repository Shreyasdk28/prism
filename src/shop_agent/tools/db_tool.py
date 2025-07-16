from crewai.tools import BaseTool
from typing import Type, Dict, Any
from pydantic import BaseModel, Field
from shop_agent.memory import memory_manager
import json

class SavePreferencesInput(BaseModel):
    """Input schema for SavePreferencesTool."""
    item_name: str = Field(..., description="Name of the item category")
    preferences: Dict[str, Any] = Field(..., description="User preferences dictionary")

class SavePreferencesTool(BaseTool):
    name: str = "save_preferences"
    description: str = (
        "Save user preferences to database for long-term storage. "
        "This tool stores user preferences like budget, color, features, etc. "
        "for future reference when the user searches for similar items."
    )
    args_schema: Type[BaseModel] = SavePreferencesInput

    def _run(self, item_name: str, preferences: Dict[str, Any]) -> str:
        """
        Save user preferences to database.
        
        Args:
            item_name: The name of the item category
            preferences: Dictionary containing user preferences
            
        Returns:
            Success/failure message
        """
        try:
            print(f"🔧 SavePreferencesTool called with:")
            print(f"   • item_name: {item_name}")
            print(f"   • preferences: {preferences}")
            
            # Save preferences to database
            success = memory_manager.save_user_preferences(item_name, preferences)
            
            if success:
                # Verify the save
                verification = memory_manager.get_user_preferences(item_name)
                print(f"✅ Verification - Retrieved after save: {verification}")
                return f"Successfully saved preferences for {item_name} to long-term memory database. Verified: {verification}"
            else:
                return f"Failed to save preferences for {item_name} to database."
                
        except Exception as e:
            error_msg = f"Error saving preferences to database: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

class GetPreferencesTool(BaseTool):
    name: str = "get_preferences"
    description: str = (
        "Retrieve user preferences from database for a specific item category. "
        "This tool helps access previously saved user preferences to provide "
        "personalized recommendations."
    )
    
    class GetPreferencesInput(BaseModel):
        item_name: str = Field(..., description="Name of the item category")
    
    args_schema: Type[BaseModel] = GetPreferencesInput

    def _run(self, item_name: str) -> str:
        """
        Retrieve user preferences from database.
        
        Args:
            item_name: The name of the item category
            
        Returns:
            User preferences or message if not found
        """
        try:
            print(f"🔍 GetPreferencesTool called for item: {item_name}")
            
            # Get preferences from database
            preferences = memory_manager.get_user_preferences(item_name)
            
            if preferences:
                result = f"Retrieved preferences for {item_name}: {json.dumps(preferences, indent=2)}"
                print(f"✅ {result}")
                return result
            else:
                result = f"No preferences found for {item_name} in database."
                print(f"ℹ️ {result}")
                return result
                
        except Exception as e:
            error_msg = f"Error retrieving preferences from database: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg

class ListAllPreferencesTool(BaseTool):
    name: str = "list_all_preferences"
    description: str = (
        "List all stored user preferences in the database. "
        "This tool helps see what preferences are currently stored."
    )
    
    class ListAllPreferencesInput(BaseModel):
        dummy: str = Field(default="", description="Dummy field as no input needed")
    
    args_schema: Type[BaseModel] = ListAllPreferencesInput

    def _run(self, dummy: str = "") -> str:
        """
        List all stored preferences.
        
        Returns:
            All stored preferences or message if none found
        """
        try:
            print("📋 ListAllPreferencesTool called")
            
            # Get all preferences from database
            all_preferences = memory_manager.get_user_preferences()
            
            if all_preferences:
                result = f"All stored preferences:\n{json.dumps(all_preferences, indent=2)}"
                print(f"✅ Found {len(all_preferences) if isinstance(all_preferences, dict) else 'some'} preference(s)")
                return result
            else:
                result = "No preferences found in database."
                print(f"ℹ️ {result}")
                return result
                
        except Exception as e:
            error_msg = f"Error listing all preferences: {str(e)}"
            print(f"❌ {error_msg}")
            return error_msg