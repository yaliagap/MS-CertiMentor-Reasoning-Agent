"""
Engagement Agent - Agent 3
Schedules reminders and sends motivational messages.
"""
from agent_framework.azure import AzureOpenAIChatClient
from .config.agents_config import AgentConfig


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

    Args:
        chat_client: Configured AzureOpenAIChatClient instance

    Returns:
        Agent instance configured for student engagement
    """
    config = AgentConfig.get_agent_config("engagement_agent")

    return chat_client.as_agent(
        name=config["name"],
        instructions=config["instructions"],
        temperature=config["temperature"]
    )
