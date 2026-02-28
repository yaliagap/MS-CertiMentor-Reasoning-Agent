"""
Assessment Workflow - Interactive quiz and evaluation.
"""
import json
from src.models import Quiz, DifficultyLevel


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

    # Improved prompt with context from study plan
    if study_plan_summary:
        prompt = f"""Generate a readiness assessment for: {topics}

Study Plan Context:
{study_plan_summary}

Follow all requirements from your instructions including:
- Exactly 10 questions
- Difficulty distribution: 3 easy, 5 medium, 2 hard
- At least 2 scenario-based questions
- Include domain, learning objective, Bloom level, explanation, and reference URL for each question
- Return STRICT JSON only (no markdown, no extra text)"""
    else:
        prompt = f"""Generate a readiness assessment for: {topics}

Follow all requirements from your instructions including:
- Exactly 10 questions
- Difficulty distribution: 3 easy, 5 medium, 2 hard
- At least 2 scenario-based questions
- Include domain, learning objective, Bloom level, explanation, and reference URL for each question
- Return STRICT JSON only (no markdown, no extra text)"""

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

    # Include quiz performance details if available
    quiz_summary = ""
    if quiz:
        easy_correct = sum(1 for q in quiz.get_questions_by_difficulty(DifficultyLevel.EASY))
        medium_correct = sum(1 for q in quiz.get_questions_by_difficulty(DifficultyLevel.MEDIUM))
        hard_correct = sum(1 for q in quiz.get_questions_by_difficulty(DifficultyLevel.HARD))
        quiz_summary = f"""
Assessment Performance:
- Easy questions: {easy_correct}/3
- Medium questions: {medium_correct}/5
- Hard questions: {hard_correct}/2"""

    prompt = f"""Recommend the Microsoft certification and exam plan for: {topics}

Student score: {percentage:.0f}%
{quiz_summary}

Provide exam code, registration details, and next steps."""

    print("\n[AGENTE 5/5] Exam Plan Agent (Temperatura: 0.3)")
    print("-" * 70)

    result = await agent.run(prompt)
    print(result.text)
