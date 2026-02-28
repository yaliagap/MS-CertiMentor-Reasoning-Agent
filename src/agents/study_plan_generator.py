"""
Study Plan Generator Agent - Agent 2
Creates detailed timelines, sessions, and milestones.
"""
from agent_framework.azure import AzureOpenAIChatClient
from .config.agents_config import AgentConfig
from src.models import StudyPlan


def create_study_plan_generator(chat_client: AzureOpenAIChatClient):
    """
    Create Study Plan Generator agent.

    Temperature: 0.4 (moderate for structured planning)

    Responsibilities:
    - Convert learning paths to actionable study plans
    - Create realistic timelines
    - Define meaningful milestones (25%, 50%, 75%, 100%)
    - Balance daily load (assumes 2 hours/day)

    Args:
        chat_client: Configured AzureOpenAIChatClient instance

    Returns:
        Agent instance configured for study plan generation
    """
    config = AgentConfig.get_agent_config("study_plan_generator")

    return chat_client.as_agent(
        name=config["name"],
        instructions=config["instructions"],
        temperature=config["temperature"],
        response_format=StudyPlan  # Structured output using Pydantic model
    )
