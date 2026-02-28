"""
Agents module - Specialized AI agents for certification preparation.

This module contains 5 specialized agents:
1. Learning Path Curator - Content discovery (T=0.3)
2. Study Plan Generator - Planning (T=0.4)
3. Engagement Agent - Motivation (T=0.6)
4. Assessment Agent - Evaluation (T=0.2)
5. Exam Plan Agent - Certification (T=0.3)
"""
from .agents_factory import create_all_agents, create_azure_chat_client
from .learning_path_curator import create_learning_path_curator
from .study_plan_generator import create_study_plan_generator
from .engagement_agent import create_engagement_agent
from .assessment_agent import create_assessment_agent
from .exam_plan_agent import create_exam_plan_agent

__all__ = [
    "create_all_agents",
    "create_azure_chat_client",
    "create_learning_path_curator",
    "create_study_plan_generator",
    "create_engagement_agent",
    "create_assessment_agent",
    "create_exam_plan_agent",
]
