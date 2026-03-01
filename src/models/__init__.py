"""
Models module - Pydantic models for structured outputs.
"""
from .quiz_models import (
    Quiz,
    Question,
    QuestionOption,
    DifficultyLevel,
    BloomLevel
)
from .learning_path_models import (
    CuratedLearningPlan,
    LearningPath,
    Module,
    PriorityDomain,
    CoverageSummary,
    PriorityLevel,
    UserLevel
)
from .study_plan_models import (
    StudyPlan,
    WeekPlan,
    DailySession,
    Milestone,
    SessionType
)
from .engagement_models import (
    EngagementPlan,
    StudyReminder,
    ReminderType
)
from .exam_plan_models import (
    ExamPlan,
    ExamInfo,
    ReadinessAssessment,
    Recommendation,
    TargetedAction,
    PreparationTimeline,
    DomainPerformance,
    ExamLevel,
    ReadinessStatus,
    ConfidenceLevel,
    RecommendedAction,
    DomainStatus
)

__all__ = [
    # Quiz models
    "Quiz",
    "Question",
    "QuestionOption",
    "DifficultyLevel",
    "BloomLevel",
    # Learning path models
    "CuratedLearningPlan",
    "LearningPath",
    "Module",
    "PriorityDomain",
    "CoverageSummary",
    "PriorityLevel",
    "UserLevel",
    # Study plan models
    "StudyPlan",
    "WeekPlan",
    "DailySession",
    "Milestone",
    "SessionType",
    # Engagement models
    "EngagementPlan",
    "StudyReminder",
    "ReminderType",
    # Exam plan models
    "ExamPlan",
    "ExamInfo",
    "ReadinessAssessment",
    "Recommendation",
    "TargetedAction",
    "PreparationTimeline",
    "DomainPerformance",
    "ExamLevel",
    "ReadinessStatus",
    "ConfidenceLevel",
    "RecommendedAction",
    "DomainStatus"
]
