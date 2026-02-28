"""
Study plan creation and timeline calculation tools.
"""
from typing import List, Dict, Any
from datetime import datetime, timedelta
from src.config import Config


def calculate_study_timeline(
    total_content_hours: int,
    daily_study_hours: float = None
) -> Dict[str, Any]:
    """
    Calculate study timeline based on content hours and daily availability.

    Args:
        total_content_hours: Total hours of content to study
        daily_study_hours: Hours per day student can dedicate

    Returns:
        Timeline dictionary with duration and key dates
    """
    if daily_study_hours is None:
        daily_study_hours = Config.DEFAULT_DAILY_STUDY_HOURS

    total_days = int(total_content_hours / daily_study_hours)
    total_weeks = max(1, (total_days + 6) // 7)  # Round up to weeks

    start_date = datetime.now()
    end_date = start_date + timedelta(days=total_days)

    # Calculate milestone dates
    milestone_dates = []
    for i in range(1, 4):  # 3 milestones
        milestone_day = int(total_days * i / 4)
        milestone_date = start_date + timedelta(days=milestone_day)
        milestone_dates.append(milestone_date)

    return {
        "total_days": total_days,
        "total_weeks": total_weeks,
        "daily_hours": daily_study_hours,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "milestone_dates": [d.strftime("%Y-%m-%d") for d in milestone_dates]
    }


def create_study_sessions(
    timeline: Dict[str, Any],
    learning_paths: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Create detailed study sessions from timeline and learning paths.

    Args:
        timeline: Timeline dictionary from calculate_study_timeline
        learning_paths: List of learning path dictionaries

    Returns:
        List of study session dictionaries
    """
    sessions = []
    total_days = timeline["total_days"]
    daily_hours = timeline["daily_hours"]
    start_date = datetime.strptime(timeline["start_date"], "%Y-%m-%d")

    # Distribute learning paths across days
    paths_per_day = max(1, len(learning_paths) // total_days)

    for day in range(1, total_days + 1):
        session_date = start_date + timedelta(days=day - 1)

        # Assign learning paths to this day
        path_index = (day - 1) % len(learning_paths)
        current_path = learning_paths[path_index]

        # Extract topics from modules
        topics = current_path.get("modules", ["General Study"])[:3]

        # Determine if this is a milestone day
        milestone = None
        if day == total_days // 4:
            milestone = "25% Complete - First Checkpoint"
        elif day == total_days // 2:
            milestone = "50% Complete - Midpoint Review"
        elif day == 3 * total_days // 4:
            milestone = "75% Complete - Final Push"
        elif day == total_days:
            milestone = "100% Complete - Ready for Assessment"

        session = {
            "day": day,
            "date": session_date.strftime("%Y-%m-%d"),
            "topics": topics,
            "learning_path": current_path.get("title", "Study Session"),
            "duration_hours": daily_hours,
            "milestone": milestone
        }
        sessions.append(session)

    return sessions


def create_milestones(total_weeks: int) -> List[str]:
    """
    Create milestone descriptions for the study plan.

    Args:
        total_weeks: Total duration in weeks

    Returns:
        List of milestone strings
    """
    milestones = [
        f"Week {total_weeks // 4 or 1}: Complete foundational modules",
        f"Week {total_weeks // 2 or 2}: Finish hands-on labs and practice",
        f"Week {3 * total_weeks // 4 or 3}: Review weak areas and advanced topics",
        f"Week {total_weeks}: Take practice assessment and prepare for certification"
    ]
    return milestones
