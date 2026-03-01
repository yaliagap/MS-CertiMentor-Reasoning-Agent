"""
Engagement Agent - Agent 3
Schedules reminders and sends motivational messages.
"""
from agent_framework.azure import AzureOpenAIChatClient
from .config.agents_config import AgentConfig
from src.models import EngagementPlan


def create_engagement_agent(chat_client: AzureOpenAIChatClient):
    """
    Create Engagement agent.

    Temperature: 0.6 (higher for creative, motivational messages)

    Responsibilities:
    - Configure study reminders
    - Send motivational messages
    - Keep student engaged
    - Foster consistent study habits

    Style:
    - Enthusiastic and supportive
    - Positive and motivating language
    - Acknowledge effort and progress
    - Concise and actionable messages

    Output Format:
    - Uses EngagementPlan Pydantic model for structured output
    - Includes scheduled reminders with dates, messages, and links
    - Provides motivation strategy and accountability tips

    Args:
        chat_client: Configured AzureOpenAIChatClient instance

    Returns:
        Agent instance configured for student engagement
    """
    config = AgentConfig.get_agent_config("engagement_agent")

    return chat_client.as_agent(
        name=config["name"],
        instructions=config["instructions"],
        temperature=config["temperature"],
        response_format=EngagementPlan  # Structured output using Pydantic model
    )
