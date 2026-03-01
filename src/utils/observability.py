"""
Observability utilities for tracing and monitoring multi-agent workflows.

Provides helper functions to create custom spans and add attributes for better
visibility into agent execution, workflow phases, and performance metrics.
"""
from functools import wraps
from typing import Any, Dict, Optional
import os

# Try to import OpenTelemetry
try:
    from opentelemetry import trace
    from opentelemetry.trace import Status, StatusCode
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False


def is_observability_enabled() -> bool:
    """Check if observability is enabled in configuration."""
    if not OBSERVABILITY_AVAILABLE:
        return False

    enable_obs = os.getenv("ENABLE_OBSERVABILITY", "false").lower() == "true"
    connection_string = os.getenv("APPLICATION_INSIGHTS_CONNECTION_STRING", "")

    return enable_obs and connection_string and connection_string != "your-application-insights-connection-string"


def get_tracer(name: str = "ms-certimentor"):
    """
    Get a tracer instance for creating spans.

    Args:
        name: Name of the tracer (typically the module or component name)

    Returns:
        Tracer instance if observability is enabled, None otherwise
    """
    if not is_observability_enabled():
        return None

    return trace.get_tracer(name)


def trace_workflow_phase(phase_name: str):
    """
    Decorator to trace a workflow phase (e.g., preparation, assessment, exam planning).

    Usage:
        @trace_workflow_phase("preparation_workflow")
        async def run_preparation_workflow(...):
            ...

    Args:
        phase_name: Name of the workflow phase
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            if not is_observability_enabled():
                return await func(*args, **kwargs)

            tracer = get_tracer()
            with tracer.start_as_current_span(
                f"workflow.{phase_name}",
                attributes={
                    "workflow.phase": phase_name,
                    "workflow.type": "multi_agent",
                }
            ) as span:
                try:
                    result = await func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            if not is_observability_enabled():
                return func(*args, **kwargs)

            tracer = get_tracer()
            with tracer.start_as_current_span(
                f"workflow.{phase_name}",
                attributes={
                    "workflow.phase": phase_name,
                    "workflow.type": "multi_agent",
                }
            ) as span:
                try:
                    result = func(*args, **kwargs)
                    span.set_status(Status(StatusCode.OK))
                    return result
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.record_exception(e)
                    raise

        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator


def add_workflow_attributes(attributes: Dict[str, Any]):
    """
    Add custom attributes to the current span.

    Useful for adding contextual information like topics, scores, or agent outputs.

    Args:
        attributes: Dictionary of attribute key-value pairs

    Example:
        add_workflow_attributes({
            "student.topics": "Azure AI",
            "assessment.score": 85,
            "exam.ready": True
        })
    """
    if not is_observability_enabled():
        return

    current_span = trace.get_current_span()
    if current_span.is_recording():
        for key, value in attributes.items():
            # Convert value to string if it's not a basic type
            if isinstance(value, (str, int, float, bool)):
                current_span.set_attribute(key, value)
            else:
                current_span.set_attribute(key, str(value))


def create_custom_span(
    name: str,
    attributes: Optional[Dict[str, Any]] = None
):
    """
    Create a custom span for manual instrumentation.

    Use this as a context manager for fine-grained tracing.

    Args:
        name: Name of the span (e.g., "quiz.generation", "domain.evaluation")
        attributes: Optional attributes to add to the span

    Example:
        with create_custom_span("quiz.generation", {"question.count": 10}):
            quiz = generate_quiz(topics)

    Returns:
        Context manager for the span
    """
    if not is_observability_enabled():
        # Return a no-op context manager
        from contextlib import nullcontext
        return nullcontext()

    tracer = get_tracer()
    span = tracer.start_as_current_span(name)

    if attributes:
        current_span = trace.get_current_span()
        if current_span.is_recording():
            for key, value in attributes.items():
                if isinstance(value, (str, int, float, bool)):
                    current_span.set_attribute(key, value)
                else:
                    current_span.set_attribute(key, str(value))

    return span


def trace_assessment_result(score: int, total: int, passed: bool):
    """
    Add assessment result attributes to the current span.

    Args:
        score: Number of correct answers
        total: Total number of questions
        passed: Whether the student passed
    """
    add_workflow_attributes({
        "assessment.score": score,
        "assessment.total": total,
        "assessment.percentage": round((score / total) * 100, 2),
        "assessment.passed": passed
    })


def trace_exam_recommendation(
    exam_code: str,
    readiness_status: str,
    overall_score: int,
    action: str
):
    """
    Add exam recommendation attributes to the current span.

    Args:
        exam_code: Exam code (e.g., "AI-900")
        readiness_status: Status ("ready", "nearly_ready", "not_ready")
        overall_score: Overall readiness score (0-100)
        action: Recommended action ("book_exam", "delay_and_reinforce", "rebuild_foundation")
    """
    add_workflow_attributes({
        "exam.code": exam_code,
        "exam.readiness_status": readiness_status,
        "exam.overall_score": overall_score,
        "exam.recommended_action": action
    })
