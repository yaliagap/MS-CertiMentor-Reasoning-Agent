"""
Preparation Subworkflow - Sequential execution of 3 agents.
Curator -> Planner -> Engagement
"""
from agent_framework.orchestrations import SequentialBuilder
import json
import re
from src.models import CuratedLearningPlan, StudyPlan


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


async def run_preparation_workflow(workflow, topics: str, email: str, user_level: str = "beginner"):
    """
    Execute the preparation workflow.

    Args:
        workflow: Sequential workflow instance
        topics: Student certification topics
        email: Student email for reminders
        user_level: User experience level (beginner, intermediate, advanced)

    Returns:
        tuple: (conversation, curated_plan, study_plan)
            - conversation: Final conversation messages from all agents
            - curated_plan: CuratedLearningPlan object from curator (if available)
            - study_plan: StudyPlan object from planner (if available)
    """
    # Build initial prompt with structured guidance
    initial_prompt = f"""Certification Goal: {topics}
Student Email: {email}
Student Level: {user_level}

Task breakdown:
1. Learning Path Curator: Use MCP tools to find and curate 1-3 highly relevant Microsoft Learn paths. Return structured JSON with priority domains, learning paths with modules, and coverage summary.
2. Study Plan Generator: Based on the curated paths, create a detailed study schedule with daily sessions, milestones, and time estimates.
3. Engagement Agent: Set up reminder schedule and send motivational message.

Begin with the curator."""

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
                print(f"\n[AGENTE: {author.upper()}]")
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
                print(f"\n[AGENTE: {author.upper()}]")
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

            else:
                # Regular display for other agents
                print(f"\n[AGENT: {author.upper()}]")
                print("-" * 70)
                print(msg.text)
