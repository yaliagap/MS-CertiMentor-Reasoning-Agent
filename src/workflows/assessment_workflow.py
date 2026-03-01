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

    score = 0
    correct_answers = quiz.get_correct_answers()
    user_answers = []

    # Auto-generated answers for demo mode (use correct answers for auto-pass)
    auto_answers = correct_answers.copy()

    for i, question in enumerate(sorted(quiz.questions, key=lambda q: q.question_number), 1):
        try:
            answer = input(f"\nQuestion {i} - Your answer (A/B/C/D): ").strip().upper()
        except (EOFError, OSError):
            # Non-interactive mode: use auto-generated answer
            answer = auto_answers[i-1]
            print(f"\nQuestion {i} - Your answer (A/B/C/D): [AUTO MODE] {answer}")

        user_answers.append(answer)

        # Check answer
        if answer == question.correct_answer:
            score += 1
            print("✓ [CORRECT]")
        else:
            print(f"✗ [INCORRECT] (Correct answer: {question.correct_answer})")
            print(f"   Explanation: {question.explanation}")

    percentage = (score / 10) * 100  # 10 questions now
    passed = percentage >= 70  # 70% = 7/10 correct

    # Display results
    print("\n" + "="*70)
    print("[ASSESSMENT RESULTS]")
    print("="*70)
    print(f"\nScore: {percentage:.0f}% ({score}/10 correct)")
    print(f"Status: {'✓ [PASSED]' if passed else '✗ [FAILED]'}")

    # Show breakdown by difficulty
    easy_score = sum(1 for i, q in enumerate(sorted(quiz.questions, key=lambda q: q.question_number))
                     if q.difficulty == DifficultyLevel.EASY and user_answers[i] == q.correct_answer)
    medium_score = sum(1 for i, q in enumerate(sorted(quiz.questions, key=lambda q: q.question_number))
                       if q.difficulty == DifficultyLevel.MEDIUM and user_answers[i] == q.correct_answer)
    hard_score = sum(1 for i, q in enumerate(sorted(quiz.questions, key=lambda q: q.question_number))
                     if q.difficulty == DifficultyLevel.HARD and user_answers[i] == q.correct_answer)

    print(f"\nBreakdown by difficulty:")
    print(f"  Easy:   {easy_score}/3 correct")
    print(f"  Medium: {medium_score}/5 correct")
    print(f"  Hard:   {hard_score}/2 correct")

    return score, passed, quiz


async def run_exam_planning(agent, topics: str, percentage: float, quiz=None):
    """
    Execute exam planning and certification recommendation.

    Args:
        agent: Exam plan agent
        topics: Topics studied
        percentage: Assessment score percentage
        quiz: Optional Quiz object with assessment details
    """
    print("\n" + "="*70)
    print("PHASE 4: CERTIFICATION PLANNING")
    print("="*70)

    # Build prompt with performance context (agent instructions already define output format)
    prompt = f"""Analyze readiness and recommend certification exam plan.

Certification Topics: {topics}
Overall Score: {percentage:.0f}%"""

    # Include detailed quiz performance if available
    if quiz:
        easy_correct = sum(1 for q in quiz.get_questions_by_difficulty(DifficultyLevel.EASY))
        medium_correct = sum(1 for q in quiz.get_questions_by_difficulty(DifficultyLevel.MEDIUM))
        hard_correct = sum(1 for q in quiz.get_questions_by_difficulty(DifficultyLevel.HARD))

        prompt += f"""

Assessment Performance Breakdown:
- Easy questions: {easy_correct}/3 ({easy_correct/3*100:.0f}%)
- Medium questions: {medium_correct}/5 ({medium_correct/5*100:.0f}%)
- Hard questions: {hard_correct}/2 ({hard_correct/2*100:.0f}%)"""

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
