"""
Notification and reminder tools.
Simulates sending study reminders via console output.
"""
from typing import List, Dict
from datetime import datetime, timedelta


def schedule_study_reminders(study_plan: Dict, student_email: str) -> Dict[str, any]:
    """
    Schedule study reminders for the student.
    In production, this would integrate with email/SMS services.
    For MVP, outputs to console.

    Args:
        study_plan: The study plan with sessions
        student_email: Student's email address

    Returns:
        Dictionary with scheduling confirmation
    """
    print("\n" + "="*60)
    print("📅 STUDY REMINDERS SCHEDULED")
    print("="*60)
    print(f"Student Email: {student_email}")
    print(f"Total Sessions: {len(study_plan.get('sessions', []))}")
    print(f"Study Duration: {study_plan.get('total_duration_weeks', 0)} weeks")
    print("\nReminder Schedule:")

    sessions = study_plan.get('sessions', [])
    for i, session in enumerate(sessions[:5]):  # Show first 5
        print(f"  Day {session['day']}: {session['date']} - {', '.join(session['topics'][:2])}")

    if len(sessions) > 5:
        print(f"  ... and {len(sessions) - 5} more sessions")

    print("\n📧 Email reminders will be sent:")
    print("  - 1 day before each study session")
    print("  - Morning of each study session")
    print("  - Weekly progress summary")
    print("="*60 + "\n")

    return {
        "scheduled": True,
        "reminder_count": len(sessions) * 2,  # 2 reminders per session
        "email": student_email,
        "next_reminder_date": sessions[0]['date'] if sessions else None
    }


def send_motivational_message(student_name: str, progress_percentage: float) -> str:
    """
    Send a motivational message based on progress.

    Args:
        student_name: Student's name
        progress_percentage: Percentage of study plan completed

    Returns:
        Motivational message string
    """
    if progress_percentage < 25:
        message = f"Great start, {student_name}! Keep up the momentum! 🚀"
    elif progress_percentage < 50:
        message = f"You're making solid progress, {student_name}! Almost halfway there! 💪"
    elif progress_percentage < 75:
        message = f"Excellent work, {student_name}! You're in the home stretch! 🎯"
    else:
        message = f"Outstanding, {student_name}! Certification is within reach! 🏆"

    print(f"\n💬 {message}\n")
    return message


def send_reminder_notification(session_info: Dict) -> bool:
    """
    Send a reminder for an upcoming study session.

    Args:
        session_info: Information about the study session

    Returns:
        True if reminder was sent successfully
    """
    print("\n" + "-"*60)
    print("⏰ STUDY REMINDER")
    print("-"*60)
    print(f"Session: Day {session_info.get('day', 'N/A')}")
    print(f"Date: {session_info.get('date', 'Today')}")
    print(f"Topics: {', '.join(session_info.get('topics', []))}")
    print(f"Duration: {session_info.get('duration_hours', 2)} hours")
    print("-"*60 + "\n")
    return True
