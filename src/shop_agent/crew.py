from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
from .tools.custom_tool import GoogleShoppingTool
from .models.model import UserPreference
from .memory import memory_manager  # Import the MemoryManager singleton
import os

load_dotenv()

# -- Agent base class with cross-agent memory protocol --
class AgentWithMemory:
    def __init__(self, name):
        self.name = name

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

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def preference_extraction_agent(self) -> Agent:
        # Inherit from AgentWithMemory to expose memory protocol
        class PreferenceExtractionAgent(AgentWithMemory):
            def __init__(self):
                super().__init__('preference_extraction_agent')
            def run(self, **kwargs):
                # Example: send a message to item_find agent
                self.send_message('item_find_agent', 'Please prioritize eco-friendly brands.')
                # Example: share user preferences for all agents
                self.share_data('user_prefs', kwargs.get('user_prefs'))
                # ...your agent logic...
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