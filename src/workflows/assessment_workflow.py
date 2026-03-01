"""
Assessment Workflow - Interactive quiz and evaluation.
"""
import json
import re
from src.models import Quiz, DifficultyLevel, ExamPlan, DomainStatus
from src.utils.observability import (
    trace_workflow_phase,
    add_workflow_attributes,
    create_custom_span,
    trace_assessment_result,
    trace_exam_recommendation
)


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


@trace_workflow_phase("assessment")
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

    # Add assessment context
    add_workflow_attributes({
        "assessment.topics": topics,
        "assessment.has_study_plan": study_plan_summary is not None
    })

    # Build prompt with context (agent instructions already define format and requirements)
    prompt = f"""Generate a readiness assessment quiz for: {topics}"""

    if study_plan_summary:
        prompt += f"""

Study Plan Context:
{study_plan_summary}

Use this context to generate relevant, contextual questions that align with what the student has studied."""

    print("\n[AGENTE 4/5] Assessment Agent (Temperatura: 0.2)")
    print("-" * 70)

    # Generate structured quiz with tracing
    with create_custom_span("quiz.generation", {"topics": topics}):
        result = await agent.run(prompt)

    # Parse structured output
    try:
        # The agent should return a Quiz object directly with structured outputs
        print(f"\n[DEBUG] Checking for structured output...")
        print(f"[DEBUG] Result has structured_output attr: {hasattr(result, 'structured_output')}")
        if hasattr(result, 'structured_output'):
            print(f"[DEBUG] structured_output value: {result.structured_output}")

        if hasattr(result, 'structured_output') and result.structured_output:
            print("[DEBUG] Using structured output (native JSON mode)")
            quiz = result.structured_output
        else:
            # Fallback: try to parse from text if structured output not available
            print("\n[WARNING] Structured output not available, using fallback JSON parsing")
            print("[DEBUG] This may indicate an issue with response_format configuration")

            try:
                # Try direct JSON parse first
                quiz_data = json.loads(result.text)
                print("[DEBUG] Direct JSON parse succeeded")
            except json.JSONDecodeError as je:
                # If direct parse fails, try extracting JSON from markdown/text
                print(f"[WARNING] Direct JSON parse failed: {je}")
                print("[DEBUG] Attempting to extract JSON from text with markdown handling...")
                quiz_data = extract_json_from_text(result.text)
                print("[DEBUG] JSON extraction from text succeeded")

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

        # Add quiz attributes for observability
        add_workflow_attributes({
            "quiz.total_questions": quiz.total_questions,
            "quiz.scenario_count": sum(1 for q in quiz.questions if q.is_scenario_based),
            "quiz.difficulty.easy": quiz.difficulty_distribution.get("easy", 0),
            "quiz.difficulty.medium": quiz.difficulty_distribution.get("medium", 0),
            "quiz.difficulty.hard": quiz.difficulty_distribution.get("hard", 0),
        })

    except json.JSONDecodeError as je:
        print(f"\n[ERROR] JSON parsing failed: {je}")
        print(f"[DEBUG] Error at position {je.pos}: {je.msg}")

        # Show context around the error
        error_pos = je.pos
        context_start = max(0, error_pos - 200)
        context_end = min(len(result.text), error_pos + 200)

        print(f"\n[DEBUG] JSON context around error (position {error_pos}):")
        print(f"{'='*70}")
        print(result.text[context_start:context_end])
        print(f"{'='*70}")

        print(f"\n[DEBUG] Full agent response saved for debugging")
        print(f"[DEBUG] Response length: {len(result.text)} characters")
        print(f"\n[ERROR] The Assessment Agent generated invalid JSON.")
        print(f"[ERROR] This is a model generation issue. Retrying might help.")

        # Save full response to file for debugging
        import os
        debug_file = os.path.join(os.getcwd(), "debug_quiz_response.json")
        with open(debug_file, "w", encoding="utf-8") as f:
            f.write(result.text)
        print(f"[DEBUG] Full response saved to: {debug_file}")

        raise
    except Exception as e:
        print(f"\n[ERROR] Could not parse structured quiz: {e}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        print(f"[DEBUG] Agent response (first 500 chars):")
        print(result.text[:500])
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
    print("\nYour responses will now be evaluated...")

    return quiz, user_answers


@trace_workflow_phase("assessment_evaluation")
async def run_assessment_evaluation(agent, topics: str, quiz: Quiz, user_answers: list):
    """
    Execute detailed assessment evaluation with educational feedback.

    Reviews each question, explains correct/incorrect answers, identifies
    learning gaps, and provides specific study recommendations.

    Args:
        agent: Assessment Evaluator agent
        topics: Topics being assessed
        quiz: Quiz object with all questions
        user_answers: List of user's answers (e.g., ['A', 'B', 'C', ...])

    Returns:
        AssessmentFeedback object with detailed question-by-question feedback
    """
    print("\n" + "="*70)
    print("PHASE 3B: ASSESSMENT EVALUATION & FEEDBACK")
    print("="*70)

    # Build detailed evaluation prompt
    prompt = f"""Review student performance on certification assessment.

Certification Topics: {topics}

Quiz Questions and Student Answers:
"""

    # Include each question with student's answer
    for i, question in enumerate(sorted(quiz.questions, key=lambda q: q.question_number)):
        user_answer = user_answers[i] if i < len(user_answers) else "N/A"

        prompt += f"""
Question {question.question_number}:
- Domain: {question.domain}
- Difficulty: {question.difficulty.value}
- Bloom Level: {question.bloom_level.value}
- Question: {question.question_text}
- Options:
"""
        for option in question.options:
            prompt += f"  {option.option}) {option.text}\n"

        prompt += f"- Correct Answer: {question.correct_answer}\n"
        prompt += f"- Student Answer: {user_answer}\n"
        prompt += f"- Explanation: {question.explanation}\n"

    prompt += """
Provide detailed educational feedback:
1. Review each question and explain correct/incorrect answers
2. Identify key concepts and learning gaps
3. Analyze performance by domain
4. Offer specific study recommendations
5. Provide encouraging feedback
"""

    print("\n[AGENTE 5/6] Assessment Evaluator Agent (Temperatura: 0.3)")
    print("-" * 70)

    # Generate detailed feedback with tracing
    with create_custom_span("assessment.evaluation", {
        "topics": topics,
        "total_questions": len(quiz.questions),
        "user_answers_count": len(user_answers)
    }):
        result = await agent.run(prompt)

    # Parse structured output
    try:
        # The agent should return AssessmentFeedback object directly
        if hasattr(result, 'structured_output') and result.structured_output:
            feedback = result.structured_output
        else:
            # Fallback: try to parse from text
            print("\n[DEBUG] Using fallback JSON parsing for Assessment Feedback...")
            from src.models import AssessmentFeedback
            try:
                feedback_data = extract_json_from_text(result.text)
            except json.JSONDecodeError as je:
                print(f"[ERROR] Failed to extract JSON from Assessment Evaluator response")
                print(f"[ERROR] JSON error: {je}")
                print(f"[DEBUG] Response preview (first 500 chars):")
                print(result.text[:500])
                raise
            feedback = AssessmentFeedback(**feedback_data)

        # Add feedback attributes for observability
        add_workflow_attributes({
            "feedback.total_questions": feedback.total_questions,
            "feedback.correct_count": feedback.correct_count,
            "feedback.score_percentage": feedback.score_percentage,
            "feedback.passed": feedback.passed,
            "feedback.weak_domains_count": len(feedback.get_weak_domains()),
            "feedback.strong_domains_count": len(feedback.get_strong_domains())
        })

        # Display detailed feedback
        print(f"\n" + "="*70)
        print("📊 ASSESSMENT EVALUATION RESULTS")
        print("="*70)

        # Overall score
        print(f"\n📈 OVERALL PERFORMANCE:")
        print(f"  Score: {feedback.correct_count}/{feedback.total_questions} ({feedback.score_percentage}%)")
        print(f"  Status: {'✅ PASSED' if feedback.passed else '❌ NEEDS MORE PREPARATION'}")
        print(f"  Threshold: 70% (7/10 questions)")

        # Domain performance summary
        print(f"\n📚 PERFORMANCE BY DOMAIN:")
        for domain in feedback.domain_performance:
            status_icon = {
                "strong": "🟢",
                "adequate": "🟡",
                "weak": "🔴"
            }.get(domain.status, "⚪")

            print(f"\n  {status_icon} {domain.domain_name}")
            print(f"     Score: {domain.correct_answers}/{domain.total_questions} ({domain.score_percentage}%)")
            print(f"     Status: {domain.status.upper()}")

        # Strengths and weaknesses
        if feedback.strengths:
            print(f"\n💪 STRENGTHS:")
            for strength in feedback.strengths:
                print(f"  ✓ {strength}")

        if feedback.weaknesses:
            print(f"\n⚠️ AREAS FOR IMPROVEMENT:")
            for weakness in feedback.weaknesses:
                print(f"  • {weakness}")

        # Question-by-question feedback
        print(f"\n" + "="*70)
        print("📝 DETAILED QUESTION FEEDBACK")
        print("="*70)

        for q_feedback in sorted(feedback.questions_feedback, key=lambda x: x.question_number):
            status_icon = "✅" if q_feedback.is_correct else "❌"

            print(f"\n{status_icon} Question {q_feedback.question_number} - {q_feedback.domain}")
            print(f"{'='*70}")
            print(f"Question: {q_feedback.question_text}")
            print(f"\nYour answer: {q_feedback.student_answer} | Correct answer: {q_feedback.correct_answer}")

            if q_feedback.is_correct:
                print(f"\n✅ CORRECT!")
                print(f"📖 Explanation: {q_feedback.correct_explanation}")
            else:
                print(f"\n❌ INCORRECT")
                print(f"📖 Why correct answer is right: {q_feedback.correct_explanation}")
                if q_feedback.incorrect_explanation:
                    print(f"⚠️ Why your answer is wrong: {q_feedback.incorrect_explanation}")
                if q_feedback.study_tip:
                    print(f"💡 Study tip: {q_feedback.study_tip}")

            print(f"🎯 Key concept: {q_feedback.key_concept}")

        # Overall feedback and next steps
        print(f"\n" + "="*70)
        print("💬 OVERALL FEEDBACK")
        print("="*70)
        print(f"\n{feedback.overall_feedback}")
        print(f"\n✨ {feedback.motivational_message}")

        # Next focus areas
        if feedback.next_focus_areas:
            print(f"\n🎯 NEXT FOCUS AREAS:")
            for i, area in enumerate(feedback.next_focus_areas, 1):
                print(f"  {i}. {area}")

        print(f"\n" + "="*70)

        return feedback

    except json.JSONDecodeError as je:
        # JSON parsing error
        print(f"\n[ERROR] JSON parsing error in Assessment Evaluator: {je}")
        print(f"[ERROR] Error at position {je.pos}: {je.msg}")
        print(f"[DEBUG] Agent response (first 1000 chars):")
        print(result.text[:1000])
        print(f"\n[DEBUG] Agent response (last 500 chars):")
        print(result.text[-500:])
        return None
    except Exception as e:
        # Other errors (validation, Pydantic, etc.)
        print(f"\n[ERROR] Could not parse structured feedback: {e}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        print(f"[DEBUG] Agent response (first 500 chars):")
        print(result.text[:500])
        return None


@trace_workflow_phase("exam_planning")
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

    # Calculate score for observability
    correct_count = sum(
        1 for i, question in enumerate(sorted(quiz.questions, key=lambda q: q.question_number))
        if i < len(user_answers) and user_answers[i] == question.correct_answer
    )

    # Add exam planning context
    add_workflow_attributes({
        "exam_planning.topics": topics,
        "exam_planning.quiz_questions": len(quiz.questions),
        "exam_planning.correct_answers": correct_count,
        "exam_planning.score_percentage": round((correct_count / len(quiz.questions)) * 100, 2)
    })

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

    # Generate exam plan with tracing
    with create_custom_span("exam_plan.evaluation", {
        "topics": topics,
        "correct_answers": correct_count,
        "total_questions": len(quiz.questions)
    }):
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

        # Add exam recommendation attributes for observability
        trace_exam_recommendation(
            exam_code=plan.exam.code,
            readiness_status=plan.readiness_assessment.status.value,
            overall_score=plan.readiness_assessment.overall_score,
            action=plan.recommendation.action.value
        )

        # Add domain breakdown for observability
        for i, domain in enumerate(plan.readiness_assessment.domain_breakdown):
            add_workflow_attributes({
                f"exam.domain_{i}.name": domain.domain_name,
                f"exam.domain_{i}.score": domain.score,
                f"exam.domain_{i}.status": domain.status.value
            })

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

    except json.JSONDecodeError as je:
        # JSON parsing error
        print(f"\n{'='*70}")
        print("❌ ERROR: EXAM PLAN GENERATION FAILED")
        print(f"{'='*70}")
        print(f"\n[ERROR] JSON parsing error in Exam Plan Agent: {je}")
        print(f"[ERROR] Error at position {je.pos}: {je.msg}")
        print(f"\n[DEBUG] Agent response (first 1000 chars):")
        print(result.text[:1000])
        print(f"\n[DEBUG] Agent response (last 500 chars):")
        print(result.text[-500:])
        print(f"\n{'='*70}")
        print("⚠️ The exam readiness assessment could not be completed.")
        print("However, you can review the detailed feedback from the Assessment Evaluator above.")
        print(f"{'='*70}\n")
    except Exception as e:
        # Other errors (validation, Pydantic, etc.)
        print(f"\n{'='*70}")
        print("❌ ERROR: EXAM PLAN GENERATION FAILED")
        print(f"{'='*70}")
        print(f"\n[ERROR] Could not parse structured Exam Plan: {e}")
        print(f"[ERROR] Error type: {type(e).__name__}")
        print(f"\n[DEBUG] Agent response (first 1000 chars):")
        print(result.text[:1000])
        print(f"\n{'='*70}")
        print("⚠️ The exam readiness assessment could not be completed.")
        print("However, you can review the detailed feedback from the Assessment Evaluator above.")
        print(f"{'='*70}\n")
