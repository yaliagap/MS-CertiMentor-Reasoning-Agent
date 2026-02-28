"""
Quiz Models - Pydantic models for structured assessment output.
"""
from pydantic import BaseModel, Field
from typing import List, Literal
from enum import Enum


class DifficultyLevel(str, Enum):
    """Question difficulty levels."""
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class BloomLevel(str, Enum):
    """Bloom's Taxonomy cognitive levels."""
    REMEMBER = "Remember"
    UNDERSTAND = "Understand"
    APPLY = "Apply"
    ANALYZE = "Analyze"
    EVALUATE = "Evaluate"
    CREATE = "Create"


class QuestionOption(BaseModel):
    """Multiple choice option."""
    option: Literal["A", "B", "C", "D"] = Field(description="Option letter")
    text: str = Field(description="Option text")


class Question(BaseModel):
    """Individual assessment question."""
    question_number: int = Field(description="Question number (1-10)", ge=1, le=10)
    domain: str = Field(description="Certification domain this question covers")
    learning_objective: str = Field(description="Specific learning objective being tested")
    bloom_level: BloomLevel = Field(description="Bloom's taxonomy cognitive level")
    difficulty: DifficultyLevel = Field(description="Question difficulty level")
    question_text: str = Field(description="The question text")
    options: List[QuestionOption] = Field(description="4 multiple choice options", min_length=4, max_length=4)
    correct_answer: Literal["A", "B", "C", "D"] = Field(description="Correct answer letter")
    explanation: str = Field(description="2-4 sentence explanation of why the answer is correct")
    reference_url: str = Field(description="Microsoft Learn URL for this topic")
    is_scenario_based: bool = Field(default=False, description="Whether this is a scenario-based question")


class Quiz(BaseModel):
    """Complete assessment quiz."""
    total_questions: int = Field(default=10, description="Total number of questions")
    difficulty_distribution: dict = Field(
        default={
            "easy": 3,
            "medium": 5,
            "hard": 2
        },
        description="Required difficulty distribution"
    )
    questions: List[Question] = Field(description="List of assessment questions", min_length=10, max_length=10)

    def validate_distribution(self) -> bool:
        """
        Validate that the quiz meets the difficulty distribution requirements.

        Returns:
            bool: True if distribution is correct
        """
        easy_count = sum(1 for q in self.questions if q.difficulty == DifficultyLevel.EASY)
        medium_count = sum(1 for q in self.questions if q.difficulty == DifficultyLevel.MEDIUM)
        hard_count = sum(1 for q in self.questions if q.difficulty == DifficultyLevel.HARD)

        return (
            easy_count == self.difficulty_distribution["easy"] and
            medium_count == self.difficulty_distribution["medium"] and
            hard_count == self.difficulty_distribution["hard"]
        )

    def validate_scenario_questions(self) -> bool:
        """
        Validate that there are at least 2 scenario-based questions.

        Returns:
            bool: True if at least 2 scenario questions exist
        """
        scenario_count = sum(1 for q in self.questions if q.is_scenario_based)
        return scenario_count >= 2

    def get_questions_by_difficulty(self, difficulty: DifficultyLevel) -> List[Question]:
        """
        Get all questions of a specific difficulty level.

        Args:
            difficulty: The difficulty level to filter by

        Returns:
            List of questions matching the difficulty
        """
        return [q for q in self.questions if q.difficulty == difficulty]

    def get_correct_answers(self) -> List[str]:
        """
        Get list of correct answers in order.

        Returns:
            List of correct answer letters ["A", "C", "B", ...]
        """
        return [q.correct_answer for q in sorted(self.questions, key=lambda x: x.question_number)]
