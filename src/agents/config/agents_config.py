"""
Agent Configuration - Temperatures, models, and settings for all agents.
"""
import os
from pathlib import Path


class AgentConfig:
    """Configuration for all agents."""

    # Base settings
    MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")
    API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2025-01-01-preview")

    # Agent-specific temperatures
    TEMPERATURES = {
        "learning_path_curator": 0.3,  # Low for consistent, factual recommendations
        "study_plan_generator": 0.4,   # Moderate for structured planning
        "engagement_agent": 0.6,        # Higher for creative, motivational messages
        "assessment_agent": 0.2,        # Very low for precise, objective questions
        "exam_plan_agent": 0.3,         # Low for factual certification guidance
    }

    # Prompts directory
    PROMPTS_DIR = Path(__file__).parent.parent / "prompts"

    @classmethod
    def get_temperature(cls, agent_name: str) -> float:
        """
        Get temperature for a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Temperature value (0.0-1.0)

        Raises:
            ValueError: If agent name not found
        """
        temp = cls.TEMPERATURES.get(agent_name)
        if temp is None:
            raise ValueError(f"Unknown agent: {agent_name}")
        return temp

    @classmethod
    def get_prompt(cls, agent_name: str) -> str:
        """
        Load prompt/instructions from file for a specific agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Prompt text as string

        Raises:
            FileNotFoundError: If prompt file doesn't exist
        """
        prompt_file = cls.PROMPTS_DIR / f"{agent_name}.txt"

        if not prompt_file.exists():
            raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

        with open(prompt_file, "r", encoding="utf-8") as f:
            return f.read().strip()

    @classmethod
    def get_agent_config(cls, agent_name: str) -> dict:
        """
        Get complete configuration for an agent.

        Args:
            agent_name: Name of the agent

        Returns:
            Dictionary with temperature, model, and instructions
        """
        return {
            "name": agent_name,
            "temperature": cls.get_temperature(agent_name),
            "model": cls.MODEL,
            "instructions": cls.get_prompt(agent_name)
        }


# Agent metadata for documentation
AGENT_METADATA = {
    "learning_path_curator": {
        "role": "Content Discovery",
        "description": "Searches and ranks Microsoft Learn paths by relevance",
        "temperature": 0.3,
        "responsibilities": [
            "Analyze student study topics",
            "Search relevant learning paths",
            "Rank by relevance",
            "Recommend top 3-5 paths"
        ]
    },
    "study_plan_generator": {
        "role": "Planning",
        "description": "Creates timelines, sessions, milestones (2h/day)",
        "temperature": 0.4,
        "responsibilities": [
            "Convert paths to actionable plans",
            "Create realistic timelines",
            "Define meaningful milestones",
            "Balance daily load"
        ]
    },
    "engagement_agent": {
        "role": "Motivation",
        "description": "Schedules reminders and sends motivational messages",
        "temperature": 0.6,
        "responsibilities": [
            "Configure study reminders",
            "Send motivational messages",
            "Keep student engaged",
            "Foster consistent habits"
        ]
    },
    "assessment_agent": {
        "role": "Evaluation",
        "description": "Generates quizzes, grades answers, provides feedback",
        "temperature": 0.2,
        "responsibilities": [
            "Generate certification-style questions",
            "Evaluate student readiness",
            "Provide detailed feedback",
            "Identify weak areas"
        ]
    },
    "exam_plan_agent": {
        "role": "Certification",
        "description": "Recommends exams and provides registration details",
        "temperature": 0.3,
        "responsibilities": [
            "Recommend appropriate certification",
            "Provide registration information",
            "Share preparation strategies",
            "Offer exam day tips"
        ]
    }
}
