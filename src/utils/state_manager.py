"""
State management for the MS-CertiMentor workflow.
Defines the shared state schema that flows through all agents.
"""
from typing import TypedDict, List, Optional, Dict, Any
from pydantic import BaseModel


# Pydantic models for structured data
class LearningPath(BaseModel):
    """A Microsoft Learn learning path."""
    title: str
    url: str
    duration_minutes: int
    description: str
    relevance_score: float
    modules: List[str] = []


class StudySession(BaseModel):
    """A single study session in the plan."""
    day: int
    date: str
    topics: List[str]
    learning_path: str
    duration_hours: float
    milestone: Optional[str] = None


class StudyPlan(BaseModel):
    """A complete study plan."""
    total_duration_weeks: int
    daily_hours: float
    sessions: List[StudySession]
    milestones: List[str]
    estimated_completion_date: str


class AssessmentQuestion(BaseModel):
    """A single assessment question."""
    question_id: int
    question_text: str
    options: List[str]
    correct_answer: int
    topic: str
    difficulty: str


class AssessmentResult(BaseModel):
    """Results from an assessment."""
    score: float
    total_questions: int
    correct_answers: int
    passed: bool
    feedback: str
    weak_areas: List[str]
    questions: List[AssessmentQuestion]
    student_answers: List[int]


class CertificationRecommendation(BaseModel):
    """A recommended Microsoft certification."""
    exam_code: str
    exam_name: str
    description: str
    registration_url: str
    study_resources: List[str]
    estimated_readiness: str


# Main workflow state
class WorkflowState(TypedDict, total=False):
    """
    The shared state dictionary that flows through all workflow nodes.
    Each agent reads from and writes to this state.
    """
    # Input data
    student_topics: str
    student_email: str

    # Preparation phase outputs
    learning_paths: List[LearningPath]
    study_plan: StudyPlan
    reminders_scheduled: bool

    # Human checkpoint
    student_ready: bool

    # Assessment phase
    assessment_questions: List[AssessmentQuestion]
    assessment_result: AssessmentResult

    # Final recommendation
    certification: CertificationRecommendation

    # Workflow metadata
    iteration_count: int
    current_phase: str
    error_message: Optional[str]


def create_initial_state(student_topics: str, student_email: str) -> WorkflowState:
    """Create the initial workflow state with user input."""
    return WorkflowState(
        student_topics=student_topics,
        student_email=student_email,
        iteration_count=0,
        current_phase="preparation",
        error_message=None
    )
