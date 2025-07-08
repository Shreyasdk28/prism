from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from .tools.custom_tool import GoogleShoppingTool
from .models.model import UserPreference
from .memory import memory_manager  # Import the MemoryManager singleton
import os
import yaml

load_dotenv()


base_dir = os.path.dirname(os.path.abspath(__file__))
config_dir = os.path.join(base_dir, 'config')
agents_path = os.path.join(config_dir, 'agents.yaml')
tasks_path = os.path.join(config_dir, 'tasks.yaml')

# -- Agent base class with cross-agent memory protocol --
class AgentWithMemory:
    def __init__(self, name):
        self.name = name

    def run(self, **kwargs):
        # Default fallback or pass, can log or handle here if needed
        pass

    def send_message(self, to_agent, message):
        memory_manager.send_message(self.name, to_agent, message)
    
    def receive_messages(self):
        return memory_manager.get_messages(self.name)

    def share_data(self, key, value):
        memory_manager.share_data(key, value)
    
    def get_shared_data(self, key):
        return memory_manager.get_shared_data(key)
    
    
@CrewBase
class ShopAgent():
    """ShopAgent crew with cross-agent memory protocol"""

    def __init__(self):
        with open(agents_path,encoding="utf-8") as f:
            self.agents_config = yaml.safe_load(f)
        with open(tasks_path,encoding="utf-8") as f:
            self.tasks_config = yaml.safe_load(f)
    @agent
    def preference_extraction_agent(self) -> Agent:
        class PreferenceExtractionAgent(AgentWithMemory):
            def __init__(self):
                super().__init__('preference_extraction_agent')
            def run(self, **kwargs):
                # Example: send a message to item_find agent
                self.send_message('item_find_agent', 'Please prioritize eco-friendly brands.')
                # Example: share user preferences for all agents
                self.share_data('user_prefs', kwargs.get('user_prefs'))
                # ...your agent logic...
                # (the base class run is now a pass, so this is safe)
                return super().run(**kwargs)
        return Agent(
            config=self.agents_config['preference_extraction_agent'],
            verbose=True,
            # tools=tool,
            base_class=PreferenceExtractionAgent  # Use the memory-enabled base class
        )

    @agent
    def item_find(self) -> Agent:
        class ItemFindAgent(AgentWithMemory):
            def __init__(self):
                super().__init__('item_find_agent')
            def run(self, **kwargs):
                # Example: receive messages from other agents
                msgs = self.receive_messages()
                for msg in msgs:
                    print(f"[item_find_agent] Message from {msg['from']}: {msg['message']}")
                # Example: access shared user preferences
                user_prefs = self.get_shared_data('user_prefs')
                # ...your agent logic...
                return super().run(**kwargs)
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
            def run(self, **kwargs):
                # Example: share comparison summary
                self.share_data('comparison_summary', {'summary': 'Best value found!'})
                # Example: send message to item_find_agent
                self.send_message('item_find_agent', 'Comparison complete.')
                return super().run(**kwargs)
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
            def run(self, **kwargs):
                from .db import MongoDBClient
                import json
                mongo_client = MongoDBClient()
                target_item = kwargs.get('target_item')
                results_json = kwargs.get('results_json')
                final_decision_md = kwargs.get('final_decision_md')

                # Prepare the data to insert
                record = {
                    "target_item": target_item,
                    "results_json": results_json,
                    "final_decision_md": final_decision_md
                }
                mongo_client.insert_output("shop_outputs", record)
                print("✅ Output pushed to MongoDB.")
                return {"status": "success"}
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

    @crew
    def crew(self) -> Crew:
        """Creates the ShopAgent crew with cross-agent memory and messaging"""
        return Crew(
            agents=self.agents,  # Created by the @agent decorator
            tasks=self.tasks,    # Created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )