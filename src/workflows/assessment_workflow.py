"""
Assessment Workflow - Interactive quiz and evaluation.
"""
import json
import re
from src.models import Quiz, DifficultyLevel, ExamPlan, DomainStatus


def extract_json_from_text(text: str) -> dict:
    """
    Extract JSON from text, handling markdown code blocks.

    Args:
        text: Text that may contain JSON with or without markdown

    Returns:
        Parsed JSON dict

    Raises:
        json.JSONDecodeError: If no valid JSON found
    """
    # Try direct JSON parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try extracting from markdown code block
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
        return json.loads(json_str)

    # Try finding JSON object in text
    json_match = re.search(r'\{.*\}', text, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        return json.loads(json_str)

    raise json.JSONDecodeError("No valid JSON found", text, 0)


async def run_assessment(agent, topics: str, study_plan_summary: str = None):
    """
    Execute student assessment with structured Quiz output.

    Args:
        agent: Assessment agent (with structured Quiz output)
        topics: Topics to assess
        study_plan_summary: Optional summary of study plan to generate contextual questions

    Returns:
        tuple: (score, passed, quiz)
            - score: Number of correct answers (0-10)
            - passed: Boolean, True if >= 70% (7/10)
            - quiz: Quiz object with all questions and metadata
    """
    print("\n" + "="*70)
    print("PHASE 3: ASSESSMENT")
    print("="*70)

    # Build prompt with context (agent instructions already define format and requirements)
    prompt = f"""Generate a readiness assessment quiz for: {topics}"""

    if study_plan_summary:
        prompt += f"""

Study Plan Context:
{study_plan_summary}

Use this context to generate relevant, contextual questions that align with what the student has studied."""

    print("\n[AGENTE 4/5] Assessment Agent (Temperatura: 0.2)")
    print("-" * 70)

    # Generate structured quiz
    result = await agent.run(prompt)

    # Parse structured output
    try:
        # The agent should return a Quiz object directly with structured outputs
        if hasattr(result, 'structured_output') and result.structured_output:
            quiz = result.structured_output
        else:
            # Fallback: try to parse from text if structured output not available
            quiz_data = json.loads(result.text)
            quiz = Quiz(**quiz_data)

        # Validate quiz
        if not quiz.validate_distribution():
            print("\n[WARNING] Quiz difficulty distribution doesn't match requirements")
        if not quiz.validate_scenario_questions():
            print("\n[WARNING] Quiz has fewer than 2 scenario-based questions")

        # Display quiz summary
        print(f"\n[QUIZ GENERATED]")
        print(f"Total questions: {quiz.total_questions}")
        print(f"Distribution: {quiz.difficulty_distribution}")
        print(f"Scenario questions: {sum(1 for q in quiz.questions if q.is_scenario_based)}")

    except Exception as e:
        print(f"\n[ERROR] Could not parse structured quiz: {e}")
        print(f"[DEBUG] Agent response: {result.text[:500]}")
        raise

    # Display questions
    print("\n" + "="*70)
    print("[ASSESSMENT QUESTIONS]")
    print("="*70)

    for question in sorted(quiz.questions, key=lambda q: q.question_number):
        print(f"\n{'='*70}")
        print(f"Question {question.question_number} [{question.difficulty.value.upper()}] - {question.bloom_level.value}")
        print(f"Domain: {question.domain}")
        print(f"{'='*70}")
        print(f"\n{question.question_text}\n")

        for option in question.options:
            print(f"{option.option}) {option.text}")

        if question.is_scenario_based:
            print("\n[SCENARIO]")

    # Interactive quiz
    print("\n" + "="*70)
    print("[INTERACTIVE QUIZ]")
    print("="*70)
    print("\nAnswer the 10 questions above:")

    user_answers = []
    correct_answers = quiz.get_correct_answers()

    # Auto-generated answers for demo mode
    auto_answers = correct_answers.copy()

    for i, question in enumerate(sorted(quiz.questions, key=lambda q: q.question_number), 1):
        try:
            answer = input(f"\nQuestion {i} - Your answer (A/B/C/D): ").strip().upper()
        except (EOFError, OSError):
            # Non-interactive mode: use auto-generated answer
            answer = auto_answers[i-1]
            print(f"\nQuestion {i} - Your answer (A/B/C/D): [AUTO MODE] {answer}")

        user_answers.append(answer)
        print("✓ Answer recorded")

    # Display completion
    print("\n" + "="*70)
    print("[ASSESSMENT COMPLETED]")
    print("="*70)
    print(f"\n✓ All {len(user_answers)} answers recorded")
    print("\nYour responses will now be evaluated by the Exam Plan Agent...")
    print("The agent will analyze your performance by domain and provide a detailed readiness assessment.")

    return quiz, user_answers


async def run_exam_planning(agent, topics: str, quiz: Quiz, user_answers: list):
    """
    Execute exam planning and certification recommendation based on quiz performance.

    Args:
        agent: Exam plan agent
        topics: Topics studied
        quiz: Quiz object with all questions
        user_answers: List of user's answers (e.g., ['A', 'B', 'C', ...])
    """
    print("\n" + "="*70)
    print("PHASE 4: EXAM READINESS EVALUATION")
    print("="*70)

    # Build detailed assessment context for the agent
    prompt = f"""Evaluate student readiness for certification exam.

Certification Topics: {topics}

Assessment Details:
- Total Questions: {quiz.total_questions}
- Difficulty Distribution: {quiz.difficulty_distribution}

Quiz Questions and Student Answers:
"""

    # Include each question with student's answer
    for i, question in enumerate(sorted(quiz.questions, key=lambda q: q.question_number)):
        user_answer = user_answers[i] if i < len(user_answers) else "N/A"
        is_correct = user_answer == question.correct_answer

        prompt += f"""
Question {question.question_number}:
- Domain: {question.domain}
- Difficulty: {question.difficulty.value}
- Bloom Level: {question.bloom_level.value}
- Question: {question.question_text}
- Correct Answer: {question.correct_answer}
- Student Answer: {user_answer}
- Result: {'CORRECT' if is_correct else 'INCORRECT'}
- Exam Weight Context: This question tests knowledge in the "{question.domain}" domain
"""

    prompt += """
Based on this assessment, please:
1. Calculate the overall score and score per domain
2. Identify which domains are strong, adequate, or weak
3. Determine the student's readiness status (ready/nearly_ready/not_ready)
4. Provide a preparation timeline if additional study is needed
5. Give targeted next steps focusing on weak domains
"""

    print("\n[AGENTE 5/5] Exam Plan Agent (Temperatura: 0.3)")
    print("-" * 70)

    result = await agent.run(prompt)

    # Parse and display structured ExamPlan
    try:
        # Try to parse structured output
        if hasattr(result, 'structured_output') and result.structured_output:
            plan = result.structured_output
        else:
            # Fallback: parse from text (handles markdown)
            plan_data = extract_json_from_text(result.text)
            plan = ExamPlan(**plan_data)

        # Display exam plan nicely
        print(f"\n📋 EXAM READINESS ASSESSMENT")
        print(f"Certification: {plan.exam.code} - {plan.exam.name}")
        print(f"Level: {plan.exam.level.value.capitalize()}")
        print(f"Registration: {plan.exam.registration_url}\n")

        # Readiness assessment
        status_icon = {
            "ready": "✅",
            "nearly_ready": "⚠️",
            "not_ready": "❌"
        }.get(plan.readiness_assessment.status.value, "❓")

        print(f"📊 READINESS STATUS:")
        print(f"  {status_icon} Status: {plan.readiness_assessment.status.value.upper().replace('_', ' ')}")
        print(f"  📈 Overall Score: {plan.readiness_assessment.overall_score}%")
        print(f"  🎯 Confidence: {plan.readiness_assessment.confidence_level.value.capitalize()}")

        # Domain breakdown
        print(f"\n📚 DOMAIN PERFORMANCE:")
        for domain in plan.readiness_assessment.domain_breakdown:
            status_icon = {
                DomainStatus.STRONG: "🟢",
                DomainStatus.ADEQUATE: "🟡",
                DomainStatus.WEAK: "🔴"
            }.get(domain.status, "⚪")

            print(f"\n  {status_icon} {domain.domain_name}")
            print(f"     Weight: {domain.exam_weight} | Score: {domain.score}% | Status: {domain.status.value}")

        # Critical risks
        if plan.readiness_assessment.critical_risks:
            print(f"\n⚠️ CRITICAL RISKS ({len(plan.readiness_assessment.critical_risks)}):")
            for risk in plan.readiness_assessment.critical_risks:
                print(f"  • {risk}")

        # Recommendation
        action_icon = {
            "book_exam": "✅",
            "delay_and_reinforce": "⚠️",
            "rebuild_foundation": "🔄"
        }.get(plan.recommendation.action.value, "❓")

        print(f"\n💡 RECOMMENDATION:")
        print(f"  {action_icon} Action: {plan.recommendation.action.value.upper().replace('_', ' ')}")
        print(f"  📝 Justification: {plan.recommendation.justification}")

        # Preparation timeline
        print(f"\n⏱️ PREPARATION TIMELINE:")
        if plan.preparation_timeline.days_needed:
            print(f"  • Days needed: {plan.preparation_timeline.days_needed}")
            if plan.preparation_timeline.suggested_exam_date_range:
                print(f"  • Suggested exam date: {plan.preparation_timeline.suggested_exam_date_range}")
        else:
            print(f"  • Ready to book now!")
            if plan.preparation_timeline.suggested_exam_date_range:
                print(f"  • Suggested booking: {plan.preparation_timeline.suggested_exam_date_range}")
        print(f"  • Rationale: {plan.preparation_timeline.rationale}")

        # Targeted next steps
        if plan.targeted_next_steps:
            print(f"\n🎯 TARGETED NEXT STEPS ({len(plan.targeted_next_steps)}):")
            for i, action in enumerate(plan.targeted_next_steps, 1):
                print(f"\n  {i}. Focus: {action.focus_domain}")
                print(f"     Action: {action.recommended_action}")

        # Exam strategy
        if plan.exam_strategy:
            print(f"\n🧠 EXAM STRATEGY:")
            for tip in plan.exam_strategy:
                print(f"  • {tip}")

        # Exam day tips
        if plan.exam_day_tips:
            print(f"\n📝 EXAM DAY TIPS:")
            for tip in plan.exam_day_tips:
                print(f"  • {tip}")

    except Exception as e:
        # Fallback to plain text if parsing fails
        print(f"\n[WARNING] Could not parse structured output: {e}")
        print(result.text)
