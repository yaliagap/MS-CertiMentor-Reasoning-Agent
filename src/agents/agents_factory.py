"""
Agent Factory - Creates and configures all specialized agents.
Uses individual agent modules for better organization.
"""
from agent_framework.azure import AzureOpenAIChatClient
import os

# Import individual agent creators
from .learning_path_curator import create_learning_path_curator
from .study_plan_generator import create_study_plan_generator
from .engagement_agent import create_engagement_agent
from .assessment_agent import create_assessment_agent
from .assessment_evaluator_agent import create_assessment_evaluator_agent
from .exam_plan_agent import create_exam_plan_agent


def create_azure_chat_client() -> AzureOpenAIChatClient:
    """
    Create and configure Azure OpenAI Chat Client.

    Reads configuration from environment variables:
    - AZURE_OPENAI_ENDPOINT
    - AZURE_OPENAI_DEPLOYMENT_NAME
    - AZURE_OPENAI_API_KEY
    - AZURE_OPENAI_API_VERSION

    Returns:
        AzureOpenAIChatClient instance configured with environment variables
    """
    return AzureOpenAIChatClient(
        endpoint=os.getenv("AZURE_OPENAI_ENDPOINT", ""),
        deployment_name=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY", ""),
        api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")
    )


def create_all_agents(chat_client: AzureOpenAIChatClient = None) -> dict:
    """
    Create all 6 specialized agents.

    Each agent is created with:
    - Specific temperature (from config)
    - Custom instructions (from prompts/)
    - Dedicated responsibilities

    Agents created:
    1. Learning Path Curator (T=0.3) - Content discovery
    2. Study Plan Generator (T=0.4) - Planning
    3. Engagement Agent (T=0.6) - Motivation
    4. Assessment Agent (T=0.2) - Quiz generation
    5. Assessment Evaluator (T=0.3) - Educational feedback
    6. Exam Plan Agent (T=0.3) - Certification readiness

    Args:
        chat_client: Optional AzureOpenAIChatClient. If None, creates a new one.

    Returns:
        dict: Dictionary with all 6 agents
            - curator: Learning Path Curator
            - planner: Study Plan Generator
            - engagement: Engagement Agent
            - assessor: Assessment Agent
            - evaluator: Assessment Evaluator Agent
            - exam_planner: Exam Plan Agent
    """
    # Create client if not provided
    if chat_client is None:
        chat_client = create_azure_chat_client()

    # Create all agents using individual modules
    return {
        "curator": create_learning_path_curator(chat_client),
        "planner": create_study_plan_generator(chat_client),
        "engagement": create_engagement_agent(chat_client),
        "assessor": create_assessment_agent(chat_client),
        "evaluator": create_assessment_evaluator_agent(chat_client),
        "exam_planner": create_exam_plan_agent(chat_client)
    }
