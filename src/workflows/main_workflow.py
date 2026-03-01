"""
Main Workflow Orchestration - Complete certification preparation flow.
"""
from .preparation_workflow import (
    create_preparation_workflow,
    run_preparation_workflow,
    print_preparation_results
)
from .assessment_workflow import run_assessment, run_assessment_evaluation, run_exam_planning
from src.utils.observability import (
    trace_workflow_phase,
    add_workflow_attributes,
    create_custom_span
)


def print_banner(endpoint: str, model: str):
    """Print welcome banner."""
    print("\n" + "="*70)
    print("[MS-CertiMentor] Multi-Agent System with Azure OpenAI")
    print("="*70)
    print(f"\n[MODE] Azure OpenAI Service + Sequential Workflows")
    print(f"[ENDPOINT] {endpoint}")
    print(f"[MODEL] {model}")
    print("\nThis system demonstrates:")
    print("  [x] 6 Specialized agents with Azure OpenAI")
    print("  [x] Sequential Workflow orchestration")
    print("  [x] Human-in-the-loop checkpoints")
    print("  [x] Conditional workflow routing")
    print("  [x] Custom temperatures per agent")
    print("  [x] Educational feedback with detailed explanations")
    print("="*70 + "\n")


def get_user_input():
    """
    Collect user input for certification topics, email, level, and study schedule.

    Returns:
        tuple: (topics, email, user_level, study_days_per_week, daily_hours)
    """
    print("What Microsoft certification topics are you interested in?")
    print("Examples: 'Azure AI', 'Azure Fundamentals', 'Power Platform'")

    try:
        # Try to get user input
        topics = input("\nYour topics: ").strip() or "Azure AI"

        print("\nYour email for reminders?")
        email = input("Your email: ").strip() or "student@certimentor.com"

        print("\nWhat is your current knowledge level?")
        print("Options: 'beginner', 'intermediate', 'advanced'")
        user_level = input("Your level: ").strip().lower()
        if user_level not in ["beginner", "intermediate", "advanced"]:
            print("Invalid level. Defaulting to 'beginner'")
            user_level = "beginner"

        print("\nHow many days per week can you study?")
        print("Recommended: 5 days (Monday-Friday)")
        study_days_input = input("Days per week (1-7): ").strip()
        try:
            study_days_per_week = int(study_days_input)
            if study_days_per_week < 1 or study_days_per_week > 7:
                print("Invalid number. Using default: 5 days")
                study_days_per_week = 5
        except ValueError:
            print("Invalid input. Using default: 5 days")
            study_days_per_week = 5

        print("\nHow many hours per day can you dedicate to studying?")
        print("Recommended: 2 hours/day")
        daily_hours_input = input("Hours per day (0.5-8): ").strip()
        try:
            daily_hours = float(daily_hours_input)
            if daily_hours < 0.5 or daily_hours > 8:
                print("Invalid number. Using default: 2 hours")
                daily_hours = 2.0
        except ValueError:
            print("Invalid input. Using default: 2 hours")
            daily_hours = 2.0

        print("\n" + "="*70)
        print("[SUMMARY] Your Study Configuration")
        print("="*70)
        print(f"Topics: {topics}")
        print(f"Email: {email}")
        print(f"Level: {user_level}")
        print(f"Study schedule: {study_days_per_week} days/week, {daily_hours} hours/day")
        print(f"Total weekly hours: {study_days_per_week * daily_hours} hours/week")
        print("="*70)

        return topics, email, user_level, study_days_per_week, daily_hours

    except (EOFError, OSError):
        # Non-interactive mode or no stdin available: use defaults
        print("\n[AUTO MODE] Using default test values")
        topics = "Azure AI Fundamentals"
        email = "student@certimentor.com"
        user_level = "beginner"
        study_days_per_week = 5
        daily_hours = 2.0
        print(f"Your topics: {topics}")
        print(f"Your email: {email}")
        print(f"Your level: {user_level}")
        print(f"Study schedule: {study_days_per_week} days/week, {daily_hours} hours/day")
        return topics, email, user_level, study_days_per_week, daily_hours


def human_checkpoint():
    """
    Human-in-the-loop checkpoint before assessment.

    Returns:
        bool: True if user wants to proceed, False otherwise
    """
    print("\n" + "="*70)
    print("PHASE 2: HUMAN-IN-THE-LOOP CHECKPOINT")
    print("="*70)
    print("\nStudy plan summary:")
    print("  [x] Learning paths: curated")
    print("  [x] Schedule: created")
    print("  [x] Reminders: scheduled")
    print("\n[CHECKPOINT] Are you ready for the preparation assessment?")

    try:
        # Try to get user input
        ready = input("Proceed? (yes/no): ").strip().lower()
        return ready in ["yes", "y", "si", "sí"]

    except (EOFError, OSError):
        # Non-interactive mode: auto-proceed
        print("[AUTO MODE] Proceeding automatically: YES")
        return True


@trace_workflow_phase("complete_workflow")
async def run_complete_workflow(agents: dict, endpoint: str, model: str):
    """
    Execute the complete multi-agent workflow.

    Phases:
    1. Preparation (Sequential workflow: curator -> planner -> engagement)
    2. Human checkpoint
    3. Assessment (quiz + grading)
    4. Exam planning (certification recommendation)

    Args:
        agents: Dictionary with all 5 agents
        endpoint: Azure OpenAI endpoint (for banner)
        model: Model deployment name (for banner)
    """
    # Print banner
    print_banner(endpoint, model)

    # Get user input
    with create_custom_span("user_input.collection"):
        topics, email, user_level, study_days_per_week, daily_hours = get_user_input()

    # Add workflow context attributes
    add_workflow_attributes({
        "student.topics": topics,
        "student.email": email,
        "student.level": user_level,
        "student.study_days_per_week": study_days_per_week,
        "student.daily_hours": daily_hours,
        "student.weekly_hours": study_days_per_week * daily_hours
    })

    print("\n" + "="*70)
    print("[START] Launching multi-agent workflow...")
    print("="*70)

    # Phase 1: Preparation (Sequential workflow)
    print("\n" + "="*70)
    print("PHASE 1: PREPARATION SUBWORKFLOW (Sequential)")
    print("="*70)
    print("\n[EXECUTING] Sequential workflow with 3 agents...")
    print("-" * 70)

    # Create and run preparation workflow
    prep_workflow = create_preparation_workflow(
        agents["curator"],
        agents["planner"],
        agents["engagement"]
    )

    conversation, curated_plan, study_plan = await run_preparation_workflow(
        prep_workflow,
        topics,
        email,
        user_level=user_level,
        study_days_per_week=study_days_per_week,
        daily_hours=daily_hours
    )
    print_preparation_results(conversation)

    # Extract study plan summary for assessment context
    study_plan_summary = ""
    if study_plan:
        # Use structured study plan data (preferred)
        study_plan_summary = study_plan.summary_text()
    elif curated_plan:
        # Fallback: use curated plan data
        study_plan_summary = curated_plan.summary_text()
    elif conversation and len(conversation) > 0:
        # Fallback: Get messages from planner and engagement agents
        for msg in conversation:
            if hasattr(msg, 'author_name') and msg.author_name in ['study_plan_generator', 'engagement_agent']:
                study_plan_summary += msg.text + "\n\n"
        # Truncate if too long (keep first 500 chars)
        if len(study_plan_summary) > 500:
            study_plan_summary = study_plan_summary[:500] + "..."

    # Phase 2: Human checkpoint
    if not human_checkpoint():
        print("\n[OK] No problem! Review your materials and come back when you're ready.")
        return

    # Phase 3: Assessment (with study plan context)
    quiz, user_answers = await run_assessment(
        agents["assessor"],
        topics,
        study_plan_summary=study_plan_summary
    )

    # Phase 3B: Assessment Evaluation (detailed educational feedback)
    feedback = await run_assessment_evaluation(
        agents["evaluator"],
        topics,
        quiz,
        user_answers
    )

    # Phase 4: Exam Readiness Evaluation (strategic certification recommendation)
    await run_exam_planning(agents["exam_planner"], topics, quiz, user_answers)

    # Summary
    print("\n" + "="*70)
    print("[SESSION COMPLETED]")
    print("="*70)
    print(f"\n[OK] Topics: {topics}")
    print(f"[OK] Assessment: Completed with detailed feedback")
    print(f"[OK] All 6 agents executed successfully")
    print("\nThank you for using MS-CertiMentor!")
    print("="*70 + "\n")
