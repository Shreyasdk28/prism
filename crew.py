from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from composio_crewai import ComposioToolSet
from dotenv import load_dotenv
from .tools.custom_tool import GoogleShoppingTool
from shop_agent.tools.vector_tools import ShoppingMemorySearchTool
from .models.model import UserPreference, ExtractedProductNames
from typing import List
from .tools.db_tool import SavePreferencesTool, GetPreferencesTool, ListAllPreferencesTool
import os

load_dotenv()

vector_query_tool = ShoppingMemorySearchTool()

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
# scrape_tool = ScrapegraphScrapeTool(api_key=os.getenv("SCRAPEGRAPH_API_KEY"))
composio_toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))
tool = composio_toolset.get_tools(actions=['SERPAPI_SEARCH'])

@CrewBase
class ShopAgent():
    """ShopAgent crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def memory_query_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['memory_query_agent'],
            verbose=True,
            tools=[vector_query_tool],
        )

    @agent
    def preference_extraction_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['preference_extraction_agent'],
            # verbose=True,
            # tools=tool,  # Using ComposioToolSet for SERPAPI_SEARCH
        )
    
    @agent
    def item_find(self) -> Agent:
        return Agent(
            config=self.agents_config['item_find'],
            verbose=True,
            tools = [GoogleShoppingTool()],
        )
    
    @agent
    def compare_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['compare_agent'],
            verbose=True
        )
    
    @agent
    def markdown_parser_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['markdown_parser_agent'],
            verbose=True,
            # tools=[MarkdownParserTool()]  # Uncomment if you have a Markdown parser tool
        )
    
    @agent
    def database_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['database_agent'],
            verbose=True,
            tools=[SavePreferencesTool(), GetPreferencesTool(), ListAllPreferencesTool()],
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    
    @task
    def memory_query_task(self) -> Task:
        return Task(
            config=self.tasks_config['memory_query_task'],
            # output_pydantic=EpisodeList

        )
    
    @task
    def preference_extraction_task(self) -> Task:
        return Task(
            config=self.tasks_config['preference_extraction_task'],
            output_pydantic=UserPreference, 
            # output_file='preferences.json'  # Uncomment if you want to save preferences
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
            #output_file='report.md'
        )
    
    @task
    def markdown_extraction_task(self) -> Task:
        return Task(
            config=self.tasks_config['markdown_extraction_task'],
            output_pydantic=ExtractedProductNames,
            # output_file='parsed_report.json'  # Uncomment if you want to save parsed report
        )
    
    @task
    def save_to_db_task(self) -> Task:
        return Task(
            config=self.tasks_config['save_to_db_task'],
            # Make sure the task has access to the inputs
            inputs=['target_item', 'user_preferences']
        )
    
    @crew
    def crew(self) -> Crew:
        """Creates the ShopAgent crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
