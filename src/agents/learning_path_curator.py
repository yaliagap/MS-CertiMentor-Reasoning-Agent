"""
Learning Path Curator Agent - Agent 1
Searches and ranks Microsoft Learn content by relevance.
Uses Microsoft Learn MCP Server tools for real content discovery.
"""
from agent_framework.azure import AzureOpenAIChatClient
from .config.agents_config import AgentConfig
from src.models import CuratedLearningPlan
from src.tools.microsoft_learn_tools import (
    search_learning_paths,
    search_certification_modules,
    fetch_learning_path_details
)


def create_learning_path_curator(chat_client: AzureOpenAIChatClient):
    """
    Create Learning Path Curator agent with Microsoft Learn MCP tools.

    Temperature: 0.3 (low for consistent, factual recommendations)

    Responsibilities:
    - Analyze student study topics
    - Search relevant learning paths in Microsoft Learn via MCP
    - Rank by relevance
    - Recommend top 3-5 paths

    Tools Available:
    - search_learning_paths: Search Microsoft Learn for learning paths
    - search_certification_modules: Find individual modules
    - fetch_learning_path_details: Get detailed path information

    Args:
        chat_client: Configured AzureOpenAIChatClient instance

    Returns:
        Agent instance configured for learning path curation with MCP tools
    """
    config = AgentConfig.get_agent_config("learning_path_curator")

    return chat_client.as_agent(
        name=config["name"],
        instructions=config["instructions"],
        temperature=config["temperature"],
        tools=[
            search_learning_paths,
            search_certification_modules,
            fetch_learning_path_details
        ],
        response_format=CuratedLearningPlan  # Structured output using Pydantic model
    )
