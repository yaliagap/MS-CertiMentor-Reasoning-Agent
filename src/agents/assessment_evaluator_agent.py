"""
Assessment Evaluator Agent - Agent 5
Reviews quiz answers and provides detailed educational feedback.
"""
from agent_framework.azure import AzureOpenAIChatClient
from .config.agents_config import AgentConfig
from src.models import AssessmentFeedback


def create_assessment_evaluator_agent(chat_client: AzureOpenAIChatClient):
    """
    Create Assessment Evaluator agent.

    Temperature: 0.3 (low-moderate for consistent, educational feedback)

    Responsibilities:
    - Review each quiz question and student's answer
    - Explain why correct answers are correct
    - Explain why incorrect answers are wrong
    - Identify key concepts and learning gaps
    - Provide specific study tips for mistakes
    - Analyze performance by domain
    - Offer actionable next steps
    - Provide encouraging, constructive feedback

    This agent focuses purely on educational feedback and learning.
    The Exam Plan Agent (Agent 6) will use this feedback to make
    strategic certification readiness recommendations.

    Args:
        chat_client: Configured AzureOpenAIChatClient instance

    Returns:
        Agent instance configured for assessment evaluation
    """
    config = AgentConfig.get_agent_config("assessment_evaluator_agent")

    return chat_client.as_agent(
        name=config["name"],
        instructions=config["instructions"],
        temperature=config["temperature"],
        response_format=AssessmentFeedback  # Structured output using Pydantic model
    )
