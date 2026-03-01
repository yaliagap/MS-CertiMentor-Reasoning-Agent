"""
Exam Plan Agent - Agent 5
Analyzes quiz performance and provides exam readiness recommendations.
Uses Microsoft Learn MCP Server tools for certification information.
"""
from agent_framework.azure import AzureOpenAIChatClient
from .config.agents_config import AgentConfig
from src.tools.microsoft_learn_tools import get_certification_exams
from src.models import ExamPlan


def create_exam_plan_agent(chat_client: AzureOpenAIChatClient):
    """
    Create Exam Plan agent with Microsoft Learn MCP tools.

    Temperature: 0.3 (low for objective, factual assessment)

    Responsibilities:
    - Analyze quiz performance and domain-level results
    - Apply readiness thresholds (80%+ ready, 65-79% conditional, <65% not ready)
    - Identify critical risks (high-weight domains with <60% performance)
    - Recommend appropriate action (book exam, delay and reinforce, rebuild foundation)
    - Provide targeted next steps for weak domains
    - Share exam strategy and day-of tips

    Decision Logic:
    - Ready (≥80% + no critical risks) → Book exam
    - Nearly Ready (65-79%) → Delay and reinforce weak areas
    - Not Ready (<65%) → Rebuild foundation

    Critical Risk: Domain with exam weight >20% scoring <60%

    Certification Levels:
    - Fundamentals (e.g., AZ-900, AI-900): Basic level, slightly lower threshold
    - Associate (e.g., AZ-104, AI-102): Intermediate level, moderate strictness
    - Expert (e.g., AZ-305): Advanced level, higher threshold

    Output Format:
    - Uses ExamPlan Pydantic model for structured output
    - Includes exam info, readiness assessment, recommendation, next steps, strategies

    Tools Available:
    - get_certification_exams: Get Microsoft certification exam details

    Args:
        chat_client: Configured AzureOpenAIChatClient instance

    Returns:
        Agent instance configured for exam readiness assessment with structured output
    """
    config = AgentConfig.get_agent_config("exam_plan_agent")

    return chat_client.as_agent(
        name=config["name"],
        instructions=config["instructions"],
        temperature=config["temperature"],
        tools=[get_certification_exams],
        response_format=ExamPlan  # Structured output using Pydantic model
    )
