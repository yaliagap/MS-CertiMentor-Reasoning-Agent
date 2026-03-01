"""
Engagement Agent Data Models
Pydantic models for structured engagement and reminder outputs.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from enum import Enum
from datetime import datetime


class ReminderType(str, Enum):
    """Types of reminders."""
    SESSION = "session"
    MILESTONE = "milestone"
    ASSESSMENT = "assessment"
    RECOVERY = "recovery"
    BUFFER = "buffer"


class StudyReminder(BaseModel):
    """
    Individual study reminder with context and motivation.

    Attributes:
        date_time: ISO 8601 formatted date-time or relative day (e.g., "Day 1", "2026-03-15T09:00:00")
        study_item: Name of the module, topic, or activity
        reminder_type: Type of reminder (session, milestone, assessment, recovery)
        reminder: Concise motivational message (1-2 sentences)
        link: Direct URL to the learning resource
    """
    date_time: str = Field(
        description="Scheduled date/time in ISO 8601 format or relative day (e.g., 'Day 1')"
    )
    study_item: str = Field(
        description="Name of the module, topic, or learning activity",
        min_length=3
    )
    reminder_type: ReminderType = Field(
        description="Type of reminder: session, milestone, assessment, or recovery"
    )
    reminder: str = Field(
        description="Concise motivational message (1-2 sentences)",
        min_length=10,
        max_length=500
    )
    link: Optional[str] = Field(
        default=None,
        description="Direct URL to the Microsoft Learn resource. Required for session reminders, optional for general milestones."
    )

    @field_validator('link')
    @classmethod
    def validate_link_format(cls, v: Optional[str], info) -> Optional[str]:
        """Validate link format when provided."""
        # Allow None or empty string only for non-session types
        if v is None or v == "":
            reminder_type = info.data.get('reminder_type')
            # Session reminders MUST have a URL
            if reminder_type == ReminderType.SESSION:
                raise ValueError("Session reminders MUST have a valid URL from the study plan")
            # Other types (milestone, assessment, recovery, buffer) can have null links
            return None

        # If link is provided, validate format
        if not v.startswith(('http://', 'https://')):
            raise ValueError("Link must start with http:// or https://")

        return v

    @field_validator('reminder')
    @classmethod
    def validate_reminder_length(cls, v: str) -> str:
        """Ensure reminder is concise (not too long)."""
        if len(v) > 500:
            raise ValueError("Reminder must be concise (max 500 characters)")
        return v


class EngagementPlan(BaseModel):
    """
    Complete engagement and reminder plan for certification preparation.

    Attributes:
        certification_goal: Target certification exam code
        user_level: Student's experience level
        total_reminders: Total number of reminders scheduled
        study_duration_weeks: Duration of the study plan in weeks
        reminders: List of all scheduled reminders
        motivation_strategy: Overall strategy being used for this student
        accountability_tips: Key tips for staying accountable
    """
    certification_goal: str = Field(
        description="Target Microsoft certification exam code (e.g., 'AI-900')"
    )
    user_level: str = Field(
        description="Student's experience level: beginner, intermediate, or advanced"
    )
    total_reminders: int = Field(
        description="Total number of reminders scheduled",
        ge=1
    )
    study_duration_weeks: int = Field(
        description="Duration of the study plan in weeks",
        ge=1,
        le=52
    )
    reminders: List[StudyReminder] = Field(
        description="Complete list of scheduled study reminders",
        min_length=1
    )
    motivation_strategy: str = Field(
        description="Brief description of the motivational approach being used",
        max_length=300
    )
    accountability_tips: List[str] = Field(
        description="3-5 key tips for staying accountable and engaged",
        min_length=3,
        max_length=5
    )

    def get_reminders_by_type(self, reminder_type: ReminderType) -> List[StudyReminder]:
        """Get all reminders of a specific type."""
        return [r for r in self.reminders if r.reminder_type == reminder_type]

    def get_session_count(self) -> int:
        """Get count of session reminders."""
        return len(self.get_reminders_by_type(ReminderType.SESSION))

    def get_milestone_count(self) -> int:
        """Get count of milestone reminders."""
        return len(self.get_reminders_by_type(ReminderType.MILESTONE))

    def summary_text(self) -> str:
        """Generate human-readable summary."""
        return f"""Engagement Plan for {self.certification_goal}
Level: {self.user_level}
Duration: {self.study_duration_weeks} weeks
Total Reminders: {self.total_reminders}
- Session reminders: {self.get_session_count()}
- Milestone reminders: {self.get_milestone_count()}
- Assessment reminders: {len(self.get_reminders_by_type(ReminderType.ASSESSMENT))}
- Buffer reminders: {len(self.get_reminders_by_type(ReminderType.BUFFER))}
- Recovery reminders: {len(self.get_reminders_by_type(ReminderType.RECOVERY))}

Strategy: {self.motivation_strategy}"""
