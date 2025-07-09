from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from .tools.custom_tool import GoogleShoppingTool
from .models.model import UserPreference
from .memory import memory_manager
import os
import yaml
import logging
from typing import Dict, Any, Optional

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

base_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.join(base_dir, 'config')
agents_path = os.path.join(config_dir, 'agents.yaml')
tasks_path = os.path.join(config_dir, 'tasks.yaml')

# -- Enhanced Agent base class with better error handling --
class AgentWithMemory:
    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"Agent.{name}")

    def run(self, **kwargs) -> Dict[str, Any]:
        """Enhanced run method with better error handling and logging"""
        try:
            self.logger.info(f"Agent {self.name} starting execution")
            result = self._execute(**kwargs)
            self.logger.info(f"Agent {self.name} completed successfully")
            return result
        except Exception as e:
            self.logger.error(f"Agent {self.name} failed: {str(e)}")
            raise

    def _execute(self, **kwargs) -> Dict[str, Any]:
        """Override this method in subclasses for actual execution logic"""
        return {"status": "completed", "agent": self.name}

    def send_message(self, to_agent: str, message: str) -> bool:
        """Enhanced message sending with validation"""
        try:
            memory_manager.send_message(self.name, to_agent, message)
            self.logger.debug(f"Message sent to {to_agent}: {message}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to send message to {to_agent}: {str(e)}")
            return False
    
    def receive_messages(self) -> list:
        """Enhanced message receiving with error handling"""
        try:
            messages = memory_manager.get_messages(self.name)
            self.logger.debug(f"Received {len(messages)} messages")
            return messages
        except Exception as e:
            self.logger.error(f"Failed to receive messages: {str(e)}")
            return []

    def share_data(self, key: str, value: Any) -> bool:
        """Enhanced data sharing with validation"""
        try:
            memory_manager.share_data(key, value)
            self.logger.debug(f"Shared data: {key}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to share data {key}: {str(e)}")
            return False
    
    def get_shared_data(self, key: str) -> Optional[Any]:
        """Enhanced data retrieval with error handling"""
        try:
            data = memory_manager.get_shared_data(key)
            self.logger.debug(f"Retrieved shared data: {key}")
            return data
        except Exception as e:
            self.logger.error(f"Failed to get shared data {key}: {str(e)}")
            return None

    def validate_input(self, **kwargs) -> bool:
        """Validate input parameters - override in subclasses"""
        return True

@CrewBase
class ShopAgent():
    """Enhanced ShopAgent crew with improved error handling and validation"""

    def __init__(self):
        self.agents_config = self._load_config(agents_path)
        self.tasks_config = self._load_config(tasks_path)
        
    def _load_config(self, path: str) -> dict:
        """Load configuration with error handling"""
        try:
            with open(path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.error(f"Config file not found: {path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file {path}: {str(e)}")
            raise

    @agent
    def preference_extraction_agent(self) -> Agent:
        class PreferenceExtractionAgent(AgentWithMemory):
            def __init__(self):
                super().__init__('preference_extraction_agent')
            
            def validate_input(self, **kwargs) -> bool:
                """Validate that we have the necessary input data"""
                required_fields = ['target_item', 'item_details']
                for field in required_fields:
                    if not kwargs.get(field):
                        self.logger.error(f"Missing required field: {field}")
                        return False
                return True
                
            def _execute(self, **kwargs) -> Dict[str, Any]:
                if not self.validate_input(**kwargs):
                    return {"status": "error", "message": "Invalid input"}
                
                # Extract and process user preferences
                user_prefs = self._extract_preferences(kwargs)
                
                # Share processed preferences with other agents
                self.share_data('user_prefs', user_prefs)
                
                # Send contextual messages to other agents
                self.send_message('item_find_agent', 
                                f'User preferences extracted for {kwargs.get("target_item")}')
                
                return {
                    "status": "success",
                    "preferences": user_prefs,
                    "target_item": kwargs.get('target_item')
                }
            
            def _extract_preferences(self, kwargs: dict) -> dict:
                """Extract user preferences from input"""
                return {
                    "target_item": kwargs.get('target_item'),
                    "item_details": kwargs.get('item_details'),
                    "long_term_preferences": kwargs.get('long_term_preferences'),
                    "short_term": kwargs.get('short_term', {}),
                    "episode_history": kwargs.get('episode_history', [])
                }
                
        return Agent(
            config=self.agents_config['preference_extraction_agent'],
            verbose=True,
            base_class=PreferenceExtractionAgent
        )

    @agent
    def item_find(self) -> Agent:
        class ItemFindAgent(AgentWithMemory):
            def __init__(self):
                super().__init__('item_find_agent')
                
            def _execute(self, **kwargs) -> Dict[str, Any]:
                # Process messages from other agents
                messages = self.receive_messages()
                for msg in messages:
                    self.logger.info(f"Received message from {msg['from']}: {msg['message']}")
                
                # Get shared user preferences
                user_prefs = self.get_shared_data('user_prefs')
                if not user_prefs:
                    self.logger.warning("No user preferences found in shared data")
                    return {"status": "error", "message": "No user preferences available"}
                
                # Perform item search using Google Shopping Tool
                search_results = self._search_items(user_prefs)
                
                # Share search results with comparison agent
                self.share_data('search_results', search_results)
                self.send_message('compare_agent', 'Search results ready for comparison')
                
                return {
                    "status": "success",
                    "search_results": search_results,
                    "items_found": len(search_results.get('items', []))
                }
            
            def _search_items(self, user_prefs: dict) -> dict:
                """Search for items using Google Shopping Tool"""
                try:
                    # Use the GoogleShoppingTool to search
                    shopping_tool = GoogleShoppingTool()
                    query = f"{user_prefs['target_item']} {user_prefs['item_details']}"
                    results = shopping_tool.search(query)
                    
                    self.logger.info(f"Found {len(results.get('items', []))} items")
                    return results
                except Exception as e:
                    self.logger.error(f"Search failed: {str(e)}")
                    return {"items": [], "error": str(e)}
                    
        return Agent(
            config=self.agents_config['item_find'],
            verbose=True,
            tools=[GoogleShoppingTool()],
            base_class=ItemFindAgent
        )

    @agent
    def compare_agent(self) -> Agent:
        class CompareAgent(AgentWithMemory):
            def __init__(self):
                super().__init__('compare_agent')
                
            def _execute(self, **kwargs) -> Dict[str, Any]:
                # Wait for search results
                search_results = self.get_shared_data('search_results')
                if not search_results:
                    self.logger.error("No search results available for comparison")
                    return {"status": "error", "message": "No search results available"}
                
                # Perform comparison
                comparison_result = self._compare_items(search_results)
                
                # Share comparison results
                self.share_data('comparison_result', comparison_result)
                self.send_message('output_push_agent', 'Comparison completed')
                
                return {
                    "status": "success",
                    "comparison": comparison_result,
                    "top_recommendations": comparison_result.get('top_items', [])
                }
            
            def _compare_items(self, search_results: dict) -> dict:
                """Compare items and generate recommendations"""
                items = search_results.get('items', [])
                if not items:
                    return {"top_items": [], "summary": "No items to compare"}
                
                # Sort items by price, rating, etc.
                sorted_items = sorted(items, key=lambda x: (
                    -x.get('rating', 0),  # Higher rating first
                    x.get('price', float('inf'))  # Lower price first
                ))
                
                return {
                    "top_items": sorted_items[:5],  # Top 5 recommendations
                    "summary": f"Analyzed {len(items)} items, found {len(sorted_items)} valid options",
                    "total_analyzed": len(items)
                }
                
        return Agent(
            config=self.agents_config['compare_agent'],
            verbose=True,
            base_class=CompareAgent
        )

    @agent
    def output_push_agent(self) -> Agent:
        class OutputPushAgent(AgentWithMemory):
            def __init__(self):
                super().__init__('output_push_agent')
                
            def _execute(self, **kwargs) -> Dict[str, Any]:
                try:
                    from .db import MongoDBClient
                    
                    # Get comparison results
                    comparison_result = self.get_shared_data('comparison_result')
                    user_prefs = self.get_shared_data('user_prefs')
                    
                    # Prepare comprehensive record
                    record = {
                        "target_item": kwargs.get('target_item') or user_prefs.get('target_item'),
                        "user_preferences": user_prefs,
                        "comparison_result": comparison_result,
                        "results_json": kwargs.get('results_json'),
                        "final_decision_md": kwargs.get('final_decision_md'),
                        "timestamp": kwargs.get('timestamp'),
                        "session_id": kwargs.get('session_id')
                    }
                    
                    # Insert to MongoDB
                    mongo_client = MongoDBClient()
                    result = mongo_client.insert_output("shop_outputs", record)
                    
                    self.logger.info(f"✅ Output pushed to MongoDB with ID: {result.inserted_id}")
                    
                    return {
                        "status": "success",
                        "mongodb_id": str(result.inserted_id),
                        "record": record
                    }
                    
                except Exception as e:
                    self.logger.error(f"Failed to push output to MongoDB: {str(e)}")
                    return {"status": "error", "message": str(e)}
                    
        return Agent(
            config=self.agents_config['output_push_agent'],
            verbose=True,
            base_class=OutputPushAgent
        )

    @task
    def preference_extraction_task(self) -> Task:
        return Task(
            config=self.tasks_config['preference_extraction_task'],
            output_pydantic=UserPreference,
        )
    
    @task
    def item_find_task(self) -> Task:
        return Task(
            config=self.tasks_config['item_find_task'],
        )
    
    @task
    def item_compare_task(self) -> Task:
        return Task(
            config=self.tasks_config['item_compare_task'],
        )
    
    @task
    def output_push_task(self) -> Task:
        return Task(
            config=self.tasks_config.get('output_push_task', {
                'description': 'Push final results to MongoDB',
                'expected_output': 'Confirmation of successful data storage'
            }),
        )

    @crew
    def crew(self) -> Crew:
        """Creates the enhanced ShopAgent crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
            memory=False,  # Enable CrewAI's built-in memory
            embedder={
                "provider": "openai",
                "config": {
                    "model": "text-embedding-3-small"
                }
            }
        )