"""
Preparation Subworkflow - Sequential execution of 3 agents.
Curator -> Planner -> Engagement
"""
from agent_framework.orchestrations import SequentialBuilder
import json
import re
from src.models import CuratedLearningPlan, StudyPlan, EngagementPlan, ReminderType, ExamPlan, DomainStatus
from src.utils.observability import trace_workflow_phase, add_workflow_attributes


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


def create_preparation_workflow(curator, planner, engagement):
    """
    Create sequential preparation workflow.

    Agents execute in order:
    1. Learning Path Curator - Finds relevant Microsoft Learn paths
    2. Study Plan Generator - Creates detailed study plan
    3. Engagement Agent - Schedules reminders and motivation

    Args:
        curator: Learning Path Curator agent
        planner: Study Plan Generator agent
        engagement: Engagement agent

    Returns:
        Workflow: Sequential workflow ready to execute
    """
    return SequentialBuilder(
        participants=[curator, planner, engagement]
    ).build()


@trace_workflow_phase("preparation")
async def run_preparation_workflow(
    workflow,
    topics: str,
    email: str,
    user_level: str = "beginner",
    study_days_per_week: int = 5,
    daily_hours: float = 2.0
):
    """
    Execute the preparation workflow.

    Args:
        workflow: Sequential workflow instance
        topics: Student certification topics
        email: Student email for reminders
        user_level: User experience level (beginner, intermediate, advanced)
        study_days_per_week: Number of days per week the student can study
        daily_hours: Number of hours per day the student can dedicate

    Returns:
        tuple: (conversation, curated_plan, study_plan)
            - conversation: Final conversation messages from all agents
            - curated_plan: CuratedLearningPlan object from curator (if available)
            - study_plan: StudyPlan object from planner (if available)
    """
    # Add preparation context for observability
    add_workflow_attributes({
        "preparation.topics": topics,
        "preparation.user_level": user_level,
        "preparation.study_days_per_week": study_days_per_week,
        "preparation.daily_hours": daily_hours
    })

    # Build initial prompt with student context (each agent's instructions define their specific tasks)
    initial_prompt = f"""Student Profile:
- Certification Goal: {topics}
- Email: {email}
- Experience Level: {user_level}
- Study Availability: {study_days_per_week} days/week, {daily_hours} hours/day
- Total Weekly Capacity: {study_days_per_week * daily_hours} hours/week

Create a complete certification preparation plan for this student."""

    # Execute workflow
    conversation = []
    curated_plan = None
    study_plan = None

    async for event in workflow.run(initial_prompt, stream=True):
        if event.type == "output":
            conversation = event.data

    # Extract structured outputs from conversation
    if conversation:
        for msg in conversation:
            if msg.role == "assistant":
                # Extract curated plan from Learning Path Curator
                if msg.author_name == "learning_path_curator":
                    try:
                        if hasattr(msg, 'structured_output') and msg.structured_output:
                            curated_plan = msg.structured_output
                        else:
                            # Fallback: parse from text (handles markdown)
                            plan_data = extract_json_from_text(msg.text)
                            curated_plan = CuratedLearningPlan(**plan_data)
                    except Exception as e:
                        print(f"[WARNING] Could not extract curated plan: {e}")

                # Extract study plan from Study Plan Generator
                elif msg.author_name == "study_plan_generator":
                    try:
                        if hasattr(msg, 'structured_output') and msg.structured_output:
                            study_plan = msg.structured_output
                        else:
                            # Fallback: parse from text (handles markdown)
                            plan_data = extract_json_from_text(msg.text)
                            study_plan = StudyPlan(**plan_data)
                    except Exception as e:
                        print(f"[WARNING] Could not extract study plan: {e}")

    return conversation, curated_plan, study_plan


def print_preparation_results(conversation: list):
    """
    Print the results from preparation workflow with structured data parsing.

    Args:
        conversation: List of message objects from workflow
    """
    print("\n" + "="*70)
    print("[PREPARATION WORKFLOW RESULTS]")
    print("="*70)

    for i, msg in enumerate(conversation, 1):
        if msg.role == "assistant":
            author = msg.author_name or "assistant"

            # Special handling for Learning Path Curator structured output
            if author == "learning_path_curator":
                print(f"\n[AGENT: {author.upper()}]")
                print("-" * 70)

                try:
                    # Try to parse structured output
                    if hasattr(msg, 'structured_output') and msg.structured_output:
                        plan = msg.structured_output
                    else:
                        # Fallback: parse from text (handles markdown)
                        plan_data = extract_json_from_text(msg.text)
                        plan = CuratedLearningPlan(**plan_data)

                    # Display structured information nicely
                    print(f"\n📋 CURATED LEARNING PLAN")
                    print(f"Exam: {plan.exam}")
                    print(f"Level: {plan.user_level.value}\n")

                    # Priority Domains
                    print("🎯 PRIORITY DOMAINS:")
                    for domain in plan.priority_domains:
                        priority_icon = "🔴" if domain.priority_level.value == "High" else "🟡" if domain.priority_level.value == "Medium" else "🟢"
                        print(f"\n  {priority_icon} {domain.domain_name} ({domain.exam_weight})")
                        print(f"     Priority: {domain.priority_level.value}")
                        print(f"     Reason: {domain.reason}")

                    # Learning Paths
                    print(f"\n📚 RECOMMENDED LEARNING PATHS ({len(plan.recommended_learning_paths)}):")
                    for i, path in enumerate(plan.recommended_learning_paths, 1):
                        print(f"\n  {i}. {path.title}")
                        print(f"     URL: {path.url}")
                        print(f"     Duration: {path.estimated_hours}")
                        print(f"     Level: {path.difficulty_level}")
                        print(f"     Relevance: {path.relevance_score}/10")
                        print(f"     Why: {path.why_recommended}")

                        if path.modules:
                            print(f"\n     Key modules ({len(path.modules)}):")
                            for j, module in enumerate(path.modules[:3], 1):  # Show first 3 modules
                                print(f"       {j}. {module.module_title} ({module.duration})")
                                print(f"          {module.why_important}")
                            if len(path.modules) > 3:
                                print(f"       ... and {len(path.modules) - 3} more modules")

                    # Coverage Summary
                    print(f"\n📊 COVERAGE SUMMARY:")
                    print(f"  High-weight domains covered: {plan.coverage_summary.high_weight_domains_covered}")
                    if plan.coverage_summary.gaps_identified:
                        print(f"  Gaps identified: {plan.coverage_summary.gaps_identified}")

                except Exception as e:
                    # Fallback to plain text if parsing fails
                    print(f"[WARNING] Could not parse structured output: {e}")
                    print(msg.text)

            # Special handling for Study Plan Generator structured output
            elif author == "study_plan_generator":
                print(f"\n[AGENT: {author.upper()}]")
                print("-" * 70)

                try:
                    # Try to parse structured output
                    if hasattr(msg, 'structured_output') and msg.structured_output:
                        plan = msg.structured_output
                    else:
                        # Fallback: parse from text
                        plan_data = extract_json_from_text(msg.text)
                        plan = StudyPlan(**plan_data)

                    # Display structured study plan nicely
                    print(f"\n📅 {plan.plan_title.upper()}")
                    print(f"Certification: {plan.certification_goal}")
                    print(f"Duration: {plan.total_duration_weeks} weeks")
                    print(f"Total hours: {plan.total_estimated_hours:.1f} hours")
                    print(f"Daily target: {plan.daily_hours_target} hours/day\n")

                    # Milestones
                    print("🎯 PROGRESS MILESTONES:")
                    for milestone in plan.milestones:
                        icon = "🏁" if milestone.percentage == 100 else "📍"
                        print(f"\n  {icon} {milestone.percentage}% - Week {milestone.week_number}")
                        print(f"     {milestone.description}")
                        print(f"     Validation: {milestone.validation_method}")

                    # Weeks summary
                    print(f"\n📚 WEEKLY SCHEDULE ({plan.total_duration_weeks} weeks):\n")
                    for week in plan.weeks:
                        print(f"  Week {week.week_number}: {week.week_theme}")
                        print(f"  Hours: {week.total_hours}h | Sessions: {len(week.sessions)}")

                        # Show first 3 sessions as preview
                        learning_sessions = [s for s in week.sessions if s.session_type.value == "learning"]
                        if learning_sessions:
                            print(f"  Featured sessions:")
                            for session in learning_sessions[:2]:
                                print(f"    • Day {session.day_number} ({session.day_of_week}): {session.topic}")
                        print()

                    # Tips and success factors
                    if plan.preparation_tips:
                        print("💡 PREPARATION TIPS:")
                        for tip in plan.preparation_tips[:3]:
                            print(f"  • {tip}")

                    if plan.success_factors:
                        print(f"\n🔑 KEY SUCCESS FACTORS:")
                        for factor in plan.success_factors[:3]:
                            print(f"  • {factor}")

                except Exception as e:
                    # Fallback to plain text if parsing fails
                    print(f"[WARNING] Could not parse structured output: {e}")
                    print(msg.text)

            # Special handling for Engagement Agent structured output
            elif author == "engagement_agent":
                print(f"\n[AGENT: {author.upper()}]")
                print("-" * 70)

                try:
                    # Try to parse structured output
                    if hasattr(msg, 'structured_output') and msg.structured_output:
                        plan = msg.structured_output
                    else:
                        # Fallback: parse from text (handles markdown)
                        plan_data = extract_json_from_text(msg.text)
                        plan = EngagementPlan(**plan_data)

                    # Display engagement plan nicely
                    print(f"\n📬 ENGAGEMENT & REMINDER PLAN")
                    print(f"Certification: {plan.certification_goal}")
                    print(f"Student Level: {plan.user_level}")
                    print(f"Study Duration: {plan.study_duration_weeks} weeks")
                    print(f"Total Reminders: {plan.total_reminders}\n")

                    # Reminder breakdown
                    print("📊 REMINDER BREAKDOWN:")
                    print(f"  • Session reminders: {plan.get_session_count()}")
                    print(f"  • Milestone reminders: {plan.get_milestone_count()}")
                    print(f"  • Assessment reminders: {len(plan.get_reminders_by_type(ReminderType.ASSESSMENT))}")
                    print(f"  • Buffer reminders: {len(plan.get_reminders_by_type(ReminderType.BUFFER))}")
                    print(f"  • Recovery reminders: {len(plan.get_reminders_by_type(ReminderType.RECOVERY))}")

                    # Motivation strategy
                    print(f"\n🎯 MOTIVATION STRATEGY:")
                    print(f"  {plan.motivation_strategy}")

                    # Sample reminders (show first 3)
                    print(f"\n💬 SAMPLE REMINDERS (showing first 3 of {len(plan.reminders)}):")
                    for i, reminder in enumerate(plan.reminders[:3], 1):
                        reminder_icon = {
                            ReminderType.SESSION: "📖",
                            ReminderType.MILESTONE: "🎯",
                            ReminderType.ASSESSMENT: "✍️",
                            ReminderType.BUFFER: "⏸️",
                            ReminderType.RECOVERY: "🔄"
                        }.get(reminder.reminder_type, "📌")

                        print(f"\n  {reminder_icon} {reminder.date_time} - {reminder.study_item}")
                        print(f"     Type: {reminder.reminder_type.value}")
                        print(f"     Message: {reminder.reminder}")
                        if reminder.link:
                            print(f"     Link: {reminder.link[:60]}..." if len(reminder.link) > 60 else f"     Link: {reminder.link}")
                        else:
                            print(f"     Link: (General milestone - no specific resource)")

                    if len(plan.reminders) > 3:
                        print(f"\n     ... and {len(plan.reminders) - 3} more reminders")

                    # Accountability tips
                    print(f"\n💪 ACCOUNTABILITY TIPS:")
                    for tip in plan.accountability_tips:
                        print(f"  • {tip}")

                except Exception as e:
                    # Fallback to plain text if parsing fails
                    print(f"[WARNING] Could not parse structured output: {e}")
                    print(msg.text)

            # Special handling for Exam Plan Agent structured output
            elif author == "exam_plan_agent":
                print(f"\n[AGENT: {author.upper()}]")
                print("-" * 70)

                try:
                    # Try to parse structured output
                    if hasattr(msg, 'structured_output') and msg.structured_output:
                        plan = msg.structured_output
                    else:
                        # Fallback: parse from text (handles markdown)
                        plan_data = extract_json_from_text(msg.text)
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
                    print(f"[WARNING] Could not parse structured output: {e}")
                    print(msg.text)

            else:
                # Regular display for other agents
                print(f"\n[AGENT: {author.upper()}]")
                print("-" * 70)
                print(msg.text)
