from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
#from composio_crewai import ComposioToolSet
from dotenv import load_dotenv
#from crewai_tools import ScrapegraphScrapeTool
from .tools.custom_tool import GoogleShoppingTool
from .models.model import UserPreference
import os

load_dotenv()

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators
# scrape_tool = ScrapegraphScrapeTool(api_key=os.getenv("SCRAPEGRAPH_API_KEY"))
#composio_toolset = ComposioToolSet(api_key=os.getenv("COMPOSIO_API_KEY"))
##tool = composio_toolset.get_tools(actions=['SERPAPI_SEARCH'])
tool=[]
# tools.append(scrape_tool)
# tools.append(ScraperApiTool())
# tools.append(AmazonSearchTool())
# tools.append(AmazonProductDetailTool())
# tools=Crawl4AITool()

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
    def preference_extraction_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['preference_extraction_agent'],
            verbose=True,
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

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
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
