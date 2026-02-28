"""
Exam Plan Agent - Agent 5
Recommends certifications and provides registration details.
Uses Microsoft Learn MCP Server tools for certification information.
"""
from agent_framework.azure import AzureOpenAIChatClient
from .config.agents_config import AgentConfig
from src.tools.microsoft_learn_tools import get_certification_exams


def create_exam_plan_agent(chat_client: AzureOpenAIChatClient):
    """
    Create Exam Plan agent with Microsoft Learn MCP tools.

    Temperature: 0.3 (low for factual certification guidance)

    Responsibilities:
    - Recommend appropriate Microsoft certification
    - Provide registration information via MCP
    - Share preparation strategies
    - Offer exam day tips

    Certification Levels:
    - Fundamentals (e.g., AZ-900, AI-900): Basic level
    - Associate (e.g., AZ-104, AI-102): Intermediate level
    - Expert (e.g., AZ-305): Advanced level

    Tools Available:
    - get_certification_exams: Get Microsoft certification exam details

    Args:
        chat_client: Configured AzureOpenAIChatClient instance

    Returns:
        Agent instance configured for exam planning with MCP tools
    """
    config = AgentConfig.get_agent_config("exam_plan_agent")

    return chat_client.as_agent(
        name=config["name"],
        instructions=config["instructions"],
        temperature=config["temperature"],
        tools=[get_certification_exams]
    )
