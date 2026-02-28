"""
Assessment Agent - Agent 4
Generates quizzes, grades answers, and provides feedback.
"""
from agent_framework.azure import AzureOpenAIChatClient
from .config.agents_config import AgentConfig
from src.models import Quiz


def create_assessment_agent(chat_client: AzureOpenAIChatClient):
    """
    Create Assessment agent.

    Temperature: 0.2 (very low for precise, objective questions)

    Responsibilities:
    - Generate certification-style questions
    - Evaluate student readiness
    - Provide detailed feedback
    - Identify weak areas
    - Determine if ready for certification (70% threshold)

    Criteria:
    - Score >= 70%: APPROVED (ready for certification)
    - Score < 70%: NEEDS MORE PREPARATION

    Args:
        chat_client: Configured AzureOpenAIChatClient instance

    Returns:
        Agent instance configured for student assessment
    """
    config = AgentConfig.get_agent_config("assessment_agent")

    return chat_client.as_agent(
        name=config["name"],
        instructions=config["instructions"],
        temperature=config["temperature"],
        response_format=Quiz  # Structured output using Pydantic model
    )
