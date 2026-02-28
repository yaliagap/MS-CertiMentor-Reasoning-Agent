"""
Study Plan Models - Pydantic models for Study Plan Generator output.
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, timedelta
from enum import Enum


class SessionType(str, Enum):
    """Type of study session."""
    LEARNING = "learning"
    PRACTICE = "practice"
    REVIEW = "review"
    BUFFER = "buffer"
    REST = "rest"


class DailySession(BaseModel):
    """Individual daily study session."""
    day_number: int = Field(description="Day number in the plan (1, 2, 3...)", ge=1)
    day_of_week: str = Field(description="Day of the week (Monday, Tuesday, etc.)")
    session_type: SessionType = Field(description="Type of session")
    topic: str = Field(description="Topic or activity for the day")
    learning_path: Optional[str] = Field(default=None, description="Learning path being studied")
    module: Optional[str] = Field(default=None, description="Specific module if applicable")
    estimated_hours: float = Field(description="Estimated study hours for this session", ge=0, le=8)
    objectives: List[str] = Field(description="Learning objectives for this session")
    resources: List[str] = Field(default=[], description="URLs or resources for this session")


class WeekPlan(BaseModel):
    """Weekly study plan."""
    week_number: int = Field(description="Week number (1, 2, 3...)", ge=1)
    week_theme: str = Field(description="Main theme or focus for this week")
    sessions: List[DailySession] = Field(description="Daily sessions for this week", min_length=1, max_length=7)
    total_hours: float = Field(description="Total study hours for this week")

    def get_learning_sessions(self) -> List[DailySession]:
        """Get only learning sessions (exclude rest/buffer)."""
        return [s for s in self.sessions if s.session_type not in [SessionType.REST, SessionType.BUFFER]]


class Milestone(BaseModel):
    """Progress milestone."""
    percentage: int = Field(description="Progress percentage (25, 50, 75, 100)", ge=0, le=100)
    week_number: int = Field(description="Week when this milestone is reached")
    description: str = Field(description="What should be accomplished at this milestone")
    validation_method: str = Field(description="How to validate this milestone is achieved")


class StudyPlan(BaseModel):
    """Complete structured study plan."""
    plan_title: str = Field(description="Title of the study plan")
    certification_goal: str = Field(description="Target certification or exam")
    total_duration_weeks: int = Field(description="Total duration in weeks", ge=1, le=52)
    total_estimated_hours: float = Field(description="Total estimated study hours")
    daily_hours_target: float = Field(description="Target study hours per day", default=2.0)
    start_date: Optional[str] = Field(default=None, description="Recommended start date (YYYY-MM-DD)")
    completion_date: Optional[str] = Field(default=None, description="Estimated completion date (YYYY-MM-DD)")

    weeks: List[WeekPlan] = Field(description="Weekly breakdown of the study plan")
    milestones: List[Milestone] = Field(description="Progress milestones", min_length=4)

    rest_days_per_week: int = Field(description="Number of rest days per week", default=2)
    buffer_time_percentage: int = Field(description="Buffer time as percentage of total", default=15)

    preparation_tips: List[str] = Field(description="General preparation tips")
    success_factors: List[str] = Field(description="Key success factors for this plan")

    def get_total_learning_hours(self) -> float:
        """Calculate total hours excluding rest/buffer."""
        total = 0.0
        for week in self.weeks:
            for session in week.get_learning_sessions():
                total += session.estimated_hours
        return total

    def get_week(self, week_number: int) -> Optional[WeekPlan]:
        """Get a specific week by number."""
        for week in self.weeks:
            if week.week_number == week_number:
                return week
        return None

    def get_current_milestone(self, current_week: int) -> Optional[Milestone]:
        """Get the next milestone based on current week."""
        for milestone in sorted(self.milestones, key=lambda m: m.week_number):
            if milestone.week_number >= current_week:
                return milestone
        return None

    def calculate_dates(self, start_date: date = None) -> None:
        """Calculate start and completion dates."""
        if start_date is None:
            start_date = date.today()

        self.start_date = start_date.isoformat()

        # Calculate completion date (weeks * 7 days)
        completion = start_date + timedelta(weeks=self.total_duration_weeks)
        self.completion_date = completion.isoformat()

    def summary_text(self) -> str:
        """Generate a human-readable summary."""
        summary = f"Plan de Estudio: {self.plan_title}\n"
        summary += f"Certificación: {self.certification_goal}\n"
        summary += f"Duración: {self.total_duration_weeks} semanas\n"
        summary += f"Horas totales: {self.total_estimated_hours:.1f} horas\n"
        summary += f"Horas diarias: {self.daily_hours_target} horas/día\n\n"

        summary += "Semanas:\n"
        for week in self.weeks:
            summary += f"  Semana {week.week_number}: {week.week_theme} ({week.total_hours}h)\n"

        summary += "\nHitos:\n"
        for milestone in self.milestones:
            summary += f"  {milestone.percentage}% - Semana {milestone.week_number}: {milestone.description}\n"

        return summary

    def validate_plan(self) -> bool:
        """Validate that the study plan meets requirements."""
        # Check milestones
        milestone_percentages = {m.percentage for m in self.milestones}
        required_milestones = {25, 50, 75, 100}

        if not required_milestones.issubset(milestone_percentages):
            return False

        # Check that we have at least one week
        if len(self.weeks) < 1:
            return False

        # Check that total weeks matches
        if len(self.weeks) != self.total_duration_weeks:
            return False

        return True
