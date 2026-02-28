"""
Human-in-the-loop utilities for workflow checkpoints.
"""
from typing import Dict, List


def human_approval_checkpoint(state: Dict) -> Dict:
    """
    Pause workflow for human approval before assessment.

    Args:
        state: Current workflow state

    Returns:
        Updated state with student_ready flag
    """
    print("\n" + "="*70)
    print("🎯 READINESS CHECKPOINT")
    print("="*70)

    # Show study plan summary
    if "study_plan" in state:
        study_plan = state["study_plan"]
        print(f"\nStudy Plan Summary:")
        print(f"  Duration: {study_plan.total_duration_weeks} weeks")
        print(f"  Daily commitment: {study_plan.daily_hours} hours")
        print(f"  Total sessions: {len(study_plan.sessions)}")

    # Show preparation status
    if "learning_paths" in state:
        print(f"\nLearning Paths: {len(state['learning_paths'])} recommended")

    if "reminders_scheduled" in state and state["reminders_scheduled"]:
        print(f"Study Reminders: ✓ Scheduled")

    print("\n" + "-"*70)
    print("Are you ready to take the readiness assessment?")
    print("This will test your knowledge of the study topics.")
    print("-"*70)

    # Get user input
    while True:
        response = input("\nProceed with assessment? (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            state["student_ready"] = True
            print("\n✓ Great! Preparing your assessment...\n")
            break
        elif response in ["no", "n"]:
            state["student_ready"] = False
            print("\n✓ No problem! Review your study materials and return when ready.\n")
            break
        else:
            print("Please enter 'yes' or 'no'")

    return state


def collect_assessment_answers(questions: List[Dict]) -> List[int]:
    """
    Interactive quiz interface to collect student answers.

    Args:
        questions: List of assessment questions

    Returns:
        List of student's answer indices (0-based)
    """
    print("\n" + "="*70)
    print("📝 READINESS ASSESSMENT")
    print("="*70)
    print(f"Questions: {len(questions)}")
    print("Instructions: Select the best answer for each question (A, B, C, or D)")
    print("="*70 + "\n")

    student_answers = []

    for i, question in enumerate(questions):
        print(f"\nQuestion {i+1} of {len(questions)}")
        print("-"*70)
        print(f"{question['question_text']}\n")

        # Display options
        options_labels = ["A", "B", "C", "D"]
        for j, option in enumerate(question["options"]):
            print(f"  {options_labels[j]}) {option}")

        # Get answer
        while True:
            answer = input("\nYour answer (A/B/C/D): ").strip().upper()
            if answer in options_labels:
                answer_index = options_labels.index(answer)
                student_answers.append(answer_index)
                break
            else:
                print("Please enter A, B, C, or D")

    print("\n" + "="*70)
    print("✓ Assessment complete! Evaluating your answers...")
    print("="*70 + "\n")

    return student_answers


def display_assessment_results(assessment_result: Dict):
    """
    Display formatted assessment results to the student.

    Args:
        assessment_result: Assessment result dictionary
    """
    print("\n" + "="*70)
    print("📊 ASSESSMENT RESULTS")
    print("="*70)

    score_percentage = assessment_result["score"] * 100
    print(f"\nScore: {score_percentage:.1f}%")
    print(f"Correct: {assessment_result['correct_answers']}/{assessment_result['total_questions']}")

    # Status
    if assessment_result["passed"]:
        print("\n✅ STATUS: PASSED")
        print("Congratulations! You're ready for certification!")
    else:
        print("\n❌ STATUS: NOT PASSED")
        print("Keep studying - you'll get there!")

    # Feedback
    print(f"\nFeedback:")
    print(f"  {assessment_result['feedback']}")

    # Weak areas
    if assessment_result.get("weak_areas"):
        print(f"\nAreas to review:")
        for area in assessment_result["weak_areas"]:
            print(f"  • {area}")

    print("="*70 + "\n")


def confirm_retry(iteration_count: int, max_iterations: int) -> bool:
    """
    Ask student if they want to retry after failing assessment.

    Args:
        iteration_count: Current iteration number
        max_iterations: Maximum allowed iterations

    Returns:
        True if student wants to retry, False otherwise
    """
    if iteration_count >= max_iterations:
        print("\n" + "="*70)
        print("Maximum attempts reached.")
        print("Consider additional study time before taking a certification exam.")
        print("="*70 + "\n")
        return False

    attempts_left = max_iterations - iteration_count
    print("\n" + "="*70)
    print(f"You have {attempts_left} attempt(s) remaining.")
    print("Would you like to review your study materials and try again?")
    print("="*70)

    while True:
        response = input("\nRetry assessment? (yes/no): ").strip().lower()
        if response in ["yes", "y"]:
            print("\n✓ Great! Let's review your weak areas and try again.\n")
            return True
        elif response in ["no", "n"]:
            print("\n✓ Take your time to study. Good luck with your certification!\n")
            return False
        else:
            print("Please enter 'yes' or 'no'")
