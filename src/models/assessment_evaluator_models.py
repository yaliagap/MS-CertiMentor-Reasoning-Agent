"""
Assessment Evaluator Models - Pydantic models for quiz feedback and evaluation.
"""
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal


class QuestionFeedback(BaseModel):
    """
    Feedback for a single question answered by the student.
    """
    question_number: int = Field(description="Question number (1-10)", ge=1, le=10)
    domain: str = Field(description="Certification domain this question covers", min_length=3)
    question_text: str = Field(description="The question text", min_length=10)
    student_answer: Literal["A", "B", "C", "D"] = Field(description="Student's answer")
    correct_answer: Literal["A", "B", "C", "D"] = Field(description="Correct answer")
    is_correct: bool = Field(description="Whether the student answered correctly")

    # Explanations
    correct_explanation: str = Field(
        description="2-4 sentence explanation of why the correct answer is right",
        min_length=20,
        max_length=500
    )
    incorrect_explanation: Optional[str] = Field(
        default=None,
        description="If student was wrong, explain why their answer is incorrect (2-3 sentences)",
        min_length=20,
        max_length=400
    )
    key_concept: str = Field(
        description="The key concept or skill being tested",
        min_length=5,
        max_length=200
    )
    study_tip: Optional[str] = Field(
        default=None,
        description="If student was wrong, provide a specific study tip for this topic",
        min_length=10,
        max_length=300
    )


class DomainPerformanceSummary(BaseModel):
    """
    Summary of performance in a specific domain.
    """
    domain_name: str = Field(description="Name of the domain", min_length=3)
    total_questions: int = Field(description="Total questions in this domain", ge=1)
    correct_answers: int = Field(description="Correct answers in this domain", ge=0)
    score_percentage: float = Field(description="Percentage score for this domain (0-100)", ge=0, le=100)
    status: Literal["strong", "adequate", "weak"] = Field(
        description="Performance status: strong (≥70%), adequate (60-69%), weak (<60%)"
    )


class AssessmentFeedback(BaseModel):
    """
    Complete assessment feedback with detailed question-by-question analysis.
    """
    # Overall summary
    total_questions: int = Field(default=10, description="Total questions in the quiz")
    correct_count: int = Field(description="Number of correct answers", ge=0, le=10)
    incorrect_count: int = Field(description="Number of incorrect answers", ge=0, le=10)
    score_percentage: float = Field(description="Overall score percentage (0-100)", ge=0, le=100)
    passed: bool = Field(description="Whether student passed (≥70%)")

    # Question-by-question feedback
    questions_feedback: List[QuestionFeedback] = Field(
        description="Detailed feedback for each question",
        min_length=10,
        max_length=10
    )

    # Domain-level analysis
    domain_performance: List[DomainPerformanceSummary] = Field(
        description="Performance summary grouped by domain",
        min_length=1
    )

    # Strengths and weaknesses
    strengths: List[str] = Field(
        description="List of domains or topics where student performed well",
        min_length=0,
        max_length=5
    )
    weaknesses: List[str] = Field(
        description="List of domains or topics where student needs improvement",
        min_length=0,
        max_length=5
    )

    # Overall feedback
    overall_feedback: str = Field(
        description="2-4 sentence overall assessment of student performance",
        min_length=50,
        max_length=600
    )

    motivational_message: str = Field(
        description="1-2 sentence encouraging message based on performance",
        min_length=20,
        max_length=300
    )

    next_focus_areas: List[str] = Field(
        description="Top 3 areas student should focus on next (prioritized by importance)",
        min_length=1,
        max_length=3
    )

    def get_incorrect_questions(self) -> List[QuestionFeedback]:
        """
        Get list of questions the student answered incorrectly.

        Returns:
            List of QuestionFeedback for incorrect answers
        """
        return [q for q in self.questions_feedback if not q.is_correct]

    def get_correct_questions(self) -> List[QuestionFeedback]:
        """
        Get list of questions the student answered correctly.

        Returns:
            List of QuestionFeedback for correct answers
        """
        return [q for q in self.questions_feedback if q.is_correct]

    def get_weak_domains(self) -> List[DomainPerformanceSummary]:
        """
        Get domains where performance is weak (<60%).

        Returns:
            List of weak domain summaries
        """
        return [d for d in self.domain_performance if d.status == "weak"]

    def get_strong_domains(self) -> List[DomainPerformanceSummary]:
        """
        Get domains where performance is strong (≥70%).

        Returns:
            List of strong domain summaries
        """
        return [d for d in self.domain_performance if d.status == "strong"]
