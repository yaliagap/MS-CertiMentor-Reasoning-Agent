"""
Exam Plan Agent Data Models
Pydantic models for structured exam readiness assessment and certification planning.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum


class ExamLevel(str, Enum):
    """Microsoft certification levels."""
    FUNDAMENTALS = "fundamentals"
    ASSOCIATE = "associate"
    EXPERT = "expert"
    SPECIALTY = "specialty"


class ReadinessStatus(str, Enum):
    """Student readiness status."""
    READY = "ready"
    NEARLY_READY = "nearly_ready"
    NOT_READY = "not_ready"


class ConfidenceLevel(str, Enum):
    """Confidence level in readiness assessment."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class RecommendedAction(str, Enum):
    """Recommended next action."""
    BOOK_EXAM = "book_exam"
    DELAY_AND_REINFORCE = "delay_and_reinforce"
    REBUILD_FOUNDATION = "rebuild_foundation"


class ExamInfo(BaseModel):
    """
    Microsoft certification exam information.

    Attributes:
        code: Exam code (e.g., "AI-900")
        name: Full exam name
        level: Certification level
        registration_url: Official Microsoft exam registration URL
    """
    code: str = Field(
        description="Microsoft exam code (e.g., 'AI-900', 'AZ-104')",
        min_length=5,
        max_length=10
    )
    name: str = Field(
        description="Full exam name",
        min_length=10
    )
    level: ExamLevel = Field(
        description="Certification level: fundamentals, associate, expert, or specialty"
    )
    registration_url: str = Field(
        description="Official Microsoft exam registration URL"
    )

    @field_validator('registration_url')
    @classmethod
    def validate_url(cls, v: str) -> str:
        """Validate registration URL format."""
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Registration URL must start with http:// or https://")
        if 'microsoft.com' not in v.lower() and 'pearsonvue.com' not in v.lower():
            raise ValueError("Registration URL should be from microsoft.com or pearsonvue.com")
        return v


class DomainStatus(str, Enum):
    """Domain performance status."""
    STRONG = "strong"
    ADEQUATE = "adequate"
    WEAK = "weak"


class DomainPerformance(BaseModel):
    """
    Performance on a specific exam domain.

    Attributes:
        domain_name: Name of the knowledge domain
        exam_weight: Percentage weight on the exam (e.g., "25-30%")
        score: Performance score on this domain (0-100)
        status: Performance status (strong, adequate, weak)
    """
    domain_name: str = Field(
        description="Name of the knowledge domain",
        min_length=3
    )
    exam_weight: str = Field(
        description="Percentage weight on the exam (e.g., '25-30%', '15-20%')"
    )
    score: int = Field(
        description="Performance score on this domain (0-100)",
        ge=0,
        le=100
    )
    status: DomainStatus = Field(
        description="Performance status: strong (≥70%), adequate (60-69%), weak (<60%)"
    )


class ReadinessAssessment(BaseModel):
    """
    Student readiness assessment based on quiz performance.

    Attributes:
        overall_score: Overall readiness percentage (0-100)
        status: Readiness status (ready, nearly_ready, not_ready)
        confidence_level: Confidence in the assessment
        critical_risks: List of critical risk factors
        domain_breakdown: Performance breakdown by exam domain
    """
    overall_score: int = Field(
        description="Overall readiness score (0-100)",
        ge=0,
        le=100
    )
    status: ReadinessStatus = Field(
        description="Current readiness status"
    )
    confidence_level: ConfidenceLevel = Field(
        description="Confidence level in this assessment"
    )
    critical_risks: List[str] = Field(
        default_factory=list,
        description="List of critical risk factors (e.g., weak high-weight domains)"
    )
    domain_breakdown: List[DomainPerformance] = Field(
        description="Performance breakdown by exam domain (1-6 domains typically)",
        min_length=1,
        max_length=10
    )


class Recommendation(BaseModel):
    """
    Actionable recommendation based on readiness assessment.

    Attributes:
        action: Recommended next action
        justification: Clear justification referencing performance metrics
    """
    action: RecommendedAction = Field(
        description="Recommended action: book exam, delay and reinforce, or rebuild foundation"
    )
    justification: str = Field(
        description="Clear justification based on performance metrics",
        min_length=20,
        max_length=500
    )


class TargetedAction(BaseModel):
    """
    Targeted preparation action for a specific domain.

    Attributes:
        focus_domain: Domain name to focus on
        recommended_action: Specific action to take
    """
    focus_domain: str = Field(
        description="Knowledge domain to focus on",
        min_length=3
    )
    recommended_action: str = Field(
        description="Specific, actionable recommendation",
        min_length=10,
        max_length=300
    )


class PreparationTimeline(BaseModel):
    """
    Estimated time needed before booking the exam.

    Attributes:
        days_needed: Estimated days needed for preparation (null if ready now)
        suggested_exam_date_range: Suggested date range for booking
        rationale: Explanation for the timeline recommendation
    """
    days_needed: Optional[int] = Field(
        default=None,
        description="Estimated days needed for additional preparation (null if ready to book now)",
        ge=0,
        le=180
    )
    suggested_exam_date_range: Optional[str] = Field(
        default=None,
        description="Suggested date range for booking (e.g., '2-3 weeks from now', 'within 1 week')"
    )
    rationale: str = Field(
        description="Clear explanation for the timeline recommendation",
        min_length=20,
        max_length=300
    )


class ExamPlan(BaseModel):
    """
    Complete exam readiness plan with assessment and recommendations.

    Attributes:
        exam: Exam information
        readiness_assessment: Current readiness evaluation with domain breakdown
        recommendation: Recommended action with justification
        preparation_timeline: Estimated time needed before booking exam
        targeted_next_steps: Domain-specific preparation actions
        exam_strategy: Strategic approach tips for the exam
        exam_day_tips: Practical tips for exam day
    """
    exam: ExamInfo = Field(
        description="Target certification exam details"
    )
    readiness_assessment: ReadinessAssessment = Field(
        description="Current readiness evaluation based on quiz performance with domain breakdown"
    )
    recommendation: Recommendation = Field(
        description="Recommended action with justification"
    )
    preparation_timeline: PreparationTimeline = Field(
        description="Estimated time needed for additional preparation before booking exam"
    )
    targeted_next_steps: List[TargetedAction] = Field(
        description="Domain-specific preparation actions (0-5 items)",
        max_length=5
    )
    exam_strategy: List[str] = Field(
        description="Strategic tips for approaching the exam (3-7 items)",
        min_length=3,
        max_length=7
    )
    exam_day_tips: List[str] = Field(
        description="Practical exam day tips (3-5 items)",
        min_length=3,
        max_length=5
    )

    def is_ready_to_book(self) -> bool:
        """Check if student is ready to book the exam."""
        return self.recommendation.action == RecommendedAction.BOOK_EXAM

    def get_critical_focus_areas(self) -> List[str]:
        """Get list of critical domains to focus on."""
        return [action.focus_domain for action in self.targeted_next_steps]

    def get_weak_domains(self) -> List[DomainPerformance]:
        """Get list of weak domains (score < 60%)."""
        return [d for d in self.readiness_assessment.domain_breakdown if d.status == DomainStatus.WEAK]

    def get_strong_domains(self) -> List[DomainPerformance]:
        """Get list of strong domains (score ≥ 70%)."""
        return [d for d in self.readiness_assessment.domain_breakdown if d.status == DomainStatus.STRONG]

    def summary_text(self) -> str:
        """Generate human-readable summary."""
        action_text = {
            RecommendedAction.BOOK_EXAM: "✅ Ready to book exam",
            RecommendedAction.DELAY_AND_REINFORCE: "⚠️ Delay and reinforce weak areas",
            RecommendedAction.REBUILD_FOUNDATION: "❌ Rebuild foundational knowledge"
        }

        weak_domains = self.get_weak_domains()
        strong_domains = self.get_strong_domains()

        summary = f"""Exam Readiness Assessment: {self.exam.code}
Status: {self.readiness_assessment.status.value.upper()} ({self.readiness_assessment.overall_score}%)
Confidence: {self.readiness_assessment.confidence_level.value.capitalize()}

Recommendation: {action_text[self.recommendation.action]}
{self.recommendation.justification}

Domain Performance:
  • Strong domains: {len(strong_domains)}
  • Weak domains: {len(weak_domains)}
  • Critical risks: {len(self.readiness_assessment.critical_risks)}

Preparation Timeline:
  • {self.preparation_timeline.rationale}"""

        if self.preparation_timeline.days_needed:
            summary += f"\n  • Estimated prep time: {self.preparation_timeline.days_needed} days"
            if self.preparation_timeline.suggested_exam_date_range:
                summary += f"\n  • Suggested exam date: {self.preparation_timeline.suggested_exam_date_range}"

        summary += f"\n\nNext Steps: {len(self.targeted_next_steps)} targeted actions"

        return summary
