"""
Learning Path Models - Pydantic models for Learning Path Curator output.
"""
from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum


class PriorityLevel(str, Enum):
    """Priority level for domains."""
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class UserLevel(str, Enum):
    """User experience level."""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class PriorityDomain(BaseModel):
    """Priority domain for the learning path."""
    domain_name: str = Field(description="Name of the certification domain")
    exam_weight: str = Field(description="Percentage or weight of this domain in the exam (e.g., '25-30%')")
    priority_level: PriorityLevel = Field(description="Priority level based on user needs")
    reason: str = Field(description="Why this domain is prioritized for this user")


class Module(BaseModel):
    """Individual module within a learning path."""
    module_title: str = Field(description="Module title")
    module_url: str = Field(description="Microsoft Learn module URL")
    duration: str = Field(description="Estimated duration (e.g., '45 min', '2 hr')")
    why_important: str = Field(description="Why this module is important for the certification")


class LearningPath(BaseModel):
    """Recommended learning path from Microsoft Learn."""
    title: str = Field(description="Learning path title")
    url: str = Field(description="Microsoft Learn learning path URL")
    estimated_hours: str = Field(description="Total estimated hours for completion")
    difficulty_level: str = Field(description="Difficulty level (Beginner, Intermediate, Advanced)")
    relevance_score: int = Field(description="Relevance score from 1-10", ge=1, le=10)
    why_recommended: str = Field(description="Explanation of why this path is recommended")
    modules: List[Module] = Field(description="List of key modules in this path")


class CoverageSummary(BaseModel):
    """Summary of exam coverage."""
    high_weight_domains_covered: str = Field(description="Percentage or description of high-weight domains covered")
    gaps_identified: str = Field(description="Any identified gaps in the recommended learning paths")


class CuratedLearningPlan(BaseModel):
    """Complete curated learning plan output from Learning Path Curator."""
    exam: str = Field(description="Exam code or certification goal (e.g., 'AI-900', 'Azure AI Fundamentals')")
    user_level: UserLevel = Field(description="User's experience level")
    priority_domains: List[PriorityDomain] = Field(
        description="List of priority domains ranked by importance"
    )
    recommended_learning_paths: List[LearningPath] = Field(
        description="1-3 recommended learning paths",
        min_length=1,
        max_length=3
    )
    coverage_summary: CoverageSummary = Field(description="Summary of coverage and gaps")

    def get_total_estimated_hours(self) -> float:
        """
        Calculate total estimated hours across all learning paths.

        Returns:
            Total hours (approximate)
        """
        total = 0.0
        for path in self.recommended_learning_paths:
            try:
                # Try to extract number from strings like "10 hours", "2-3 hr"
                hours_str = path.estimated_hours.split()[0]
                if '-' in hours_str:
                    # Take average for ranges like "2-3"
                    parts = hours_str.split('-')
                    total += (float(parts[0]) + float(parts[1])) / 2
                else:
                    total += float(hours_str)
            except (ValueError, IndexError):
                # If parsing fails, skip
                continue
        return total

    def get_high_priority_domains(self) -> List[PriorityDomain]:
        """
        Get only high priority domains.

        Returns:
            List of high priority domains
        """
        return [d for d in self.priority_domains if d.priority_level == PriorityLevel.HIGH]

    def get_modules_by_priority(self) -> List[Module]:
        """
        Get all modules from learning paths ordered by path relevance.

        Returns:
            Flat list of modules ordered by relevance
        """
        modules = []
        # Sort paths by relevance score descending
        sorted_paths = sorted(
            self.recommended_learning_paths,
            key=lambda p: p.relevance_score,
            reverse=True
        )
        for path in sorted_paths:
            modules.extend(path.modules)
        return modules

    def summary_text(self) -> str:
        """
        Generate a human-readable text summary.

        Returns:
            Summary string
        """
        summary = f"Exam: {self.exam}\n"
        summary += f"User Level: {self.user_level.value}\n\n"

        summary += "Priority Domains:\n"
        for domain in self.priority_domains:
            summary += f"  - {domain.domain_name} ({domain.exam_weight}) - {domain.priority_level.value}\n"

        summary += f"\nRecommended Learning Paths ({len(self.recommended_learning_paths)}):\n"
        for i, path in enumerate(self.recommended_learning_paths, 1):
            summary += f"  {i}. {path.title} (Score: {path.relevance_score}/10)\n"
            summary += f"     Duration: {path.estimated_hours}\n"

        summary += f"\nCoverage: {self.coverage_summary.high_weight_domains_covered}\n"

        if self.coverage_summary.gaps_identified:
            summary += f"Gaps: {self.coverage_summary.gaps_identified}\n"

        return summary
