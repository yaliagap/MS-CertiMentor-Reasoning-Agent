"""
Main Workflow Orchestration - Complete certification preparation flow.
"""
from .preparation_workflow import (
    create_preparation_workflow,
    run_preparation_workflow,
    print_preparation_results
)
from .assessment_workflow import run_assessment, run_exam_planning


def print_banner(endpoint: str, model: str):
    """Print welcome banner."""
    print("\n" + "="*70)
    print("[MS-CertiMentor] Multi-Agent System with Azure OpenAI")
    print("="*70)
    print(f"\n[MODE] Azure OpenAI Service + Sequential Workflows")
    print(f"[ENDPOINT] {endpoint}")
    print(f"[MODEL] {model}")
    print("\nThis system demonstrates:")
    print("  [x] 5 Specialized agents with Azure OpenAI")
    print("  [x] Sequential Workflow orchestration")
    print("  [x] Human-in-the-loop checkpoints")
    print("  [x] Conditional workflow routing")
    print("  [x] Custom temperatures per agent")
    print("="*70 + "\n")


def get_user_input():
    """
    Collect user input for certification topics and email.

    Returns:
        tuple: (topics, email)
    """
    print("What Microsoft certification topics are you interested in?")
    print("Examples: 'Azure AI', 'Azure Fundamentals', 'Power Platform'")

    try:
        # Try to get user input
        topics = input("\nYour topics: ").strip() or "Azure AI"

        print("\nYour email for reminders?")
        email = input("Your email: ").strip() or "student@certimentor.com"

        return topics, email

    except (EOFError, OSError):
        # Non-interactive mode or no stdin available: use defaults
        print("\n[AUTO MODE] Using default test values")
        topics = "Azure AI Fundamentals"
        email = "student@certimentor.com"
        print(f"Your topics: {topics}")
        print(f"Your email: {email}")
        return topics, email


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


def print_summary(topics: str, percentage: float):
    """
    Print final session summary.

    Args:
        topics: Certification topics studied
        percentage: Final assessment score
    """
    print("\n" + "="*70)
    print("[SESSION COMPLETED]")
    print("="*70)
    print(f"\n[OK] Topics: {topics}")
    print(f"[OK] Assessment: {percentage:.0f}% (PASSED)")
    print(f"[OK] All 5 agents executed successfully")
    print("\nThank you for using MS-CertiMentor!")
    print("="*70 + "\n")


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
    topics, email = get_user_input()

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

    conversation, curated_plan, study_plan = await run_preparation_workflow(prep_workflow, topics, email, user_level="beginner")
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
    score, passed, quiz = await run_assessment(
        agents["assessor"],
        topics,
        study_plan_summary=study_plan_summary
    )
    percentage = (score / 10) * 100  # 10 questions now

    if not passed:
        print("\nReview the weak areas and try again. You can do it!")
        return

    # Phase 4: Exam Planning
    await run_exam_planning(agents["exam_planner"], topics, percentage, quiz=quiz)

    # Summary
    print_summary(topics, percentage)
