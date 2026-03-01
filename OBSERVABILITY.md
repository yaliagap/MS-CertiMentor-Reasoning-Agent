# Observability with Azure Application Insights

This document explains how observability is implemented in MS-CertiMentor and how to view traces and metrics in Azure Application Insights.

## Overview

MS-CertiMentor uses **OpenTelemetry** with **Azure Monitor** to provide comprehensive observability of the multi-agent workflow. All agent executions, tool calls, and workflow phases are automatically traced and sent to Azure Application Insights.

## What Gets Traced?

### 1. Workflow Phases
Each major phase of the workflow is traced as a span:
- **`workflow.complete_workflow`**: The entire end-to-end execution
- **`workflow.preparation`**: Preparation subworkflow (curator → planner → engagement)
- **`workflow.assessment`**: Quiz generation and student answers
- **`workflow.exam_planning`**: Exam readiness evaluation

### 2. Custom Spans
Fine-grained operations within workflows:
- **`user_input.collection`**: User input gathering (topics, email, study schedule)
- **`quiz.generation`**: Assessment quiz generation by Assessment Agent
- **`exam_plan.evaluation`**: Exam readiness evaluation by Exam Plan Agent

### 3. Agent Executions
The Agent Framework automatically instruments:
- Agent invocations (each agent.run() call)
- Tool calls made by agents
- Azure OpenAI API calls
- Completion tokens and latency

### 4. Custom Attributes

#### Student Context
- `student.topics`: Certification topics
- `student.email`: Student email
- `student.level`: Experience level (beginner/intermediate/advanced)
- `student.study_days_per_week`: Study frequency
- `student.daily_hours`: Daily study hours
- `student.weekly_hours`: Total weekly capacity

#### Assessment Data
- `assessment.topics`: Topics being assessed
- `assessment.has_study_plan`: Whether study plan context is available
- `quiz.total_questions`: Number of questions generated
- `quiz.scenario_count`: Number of scenario-based questions
- `quiz.difficulty.easy/medium/hard`: Distribution of difficulty levels

#### Exam Planning Data
- `exam_planning.topics`: Certification topics
- `exam_planning.quiz_questions`: Total questions
- `exam_planning.correct_answers`: Number of correct answers
- `exam_planning.score_percentage`: Student score percentage

#### Exam Recommendation
- `exam.code`: Exam code (e.g., "AI-900")
- `exam.readiness_status`: ready/nearly_ready/not_ready
- `exam.overall_score`: Readiness score (0-100)
- `exam.recommended_action`: book_exam/delay_and_reinforce/rebuild_foundation
- `exam.domain_0..N.name/score/status`: Performance by domain

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This includes:
- `azure-monitor-opentelemetry>=1.2.0`
- `opentelemetry-api>=1.21.0`
- `opentelemetry-sdk>=1.21.0`

### 2. Get Application Insights Connection String

1. Go to **Azure Portal** → **Application Insights** resource
2. Navigate to **Settings** → **Properties**
3. Copy the **Connection String**
   - Format: `InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/;LiveEndpoint=https://xxx.livediagnostics.monitor.azure.com/`

### 3. Configure Environment Variables

Add to your `.env` file:

```bash
# Azure Application Insights (Observability)
APPLICATION_INSIGHTS_CONNECTION_STRING=InstrumentationKey=xxx;IngestionEndpoint=https://xxx.in.applicationinsights.azure.com/;LiveEndpoint=https://xxx.livediagnostics.monitor.azure.com/
ENABLE_OBSERVABILITY=true
```

### 4. Run the Application

```bash
python run_azure_workflow.py
```

You should see:
```
======================================================================
[OBSERVABILITY] Configuring Azure Application Insights
======================================================================
✓ Azure Monitor configured successfully
✓ Traces and spans will be sent to Application Insights
✓ View telemetry in Azure Portal -> Application Insights -> Transaction search
======================================================================
```

## Viewing Traces in Azure Portal

### 1. Transaction Search (Real-time)

1. Go to **Azure Portal** → **Application Insights** resource
2. Navigate to **Monitoring** → **Transaction search**
3. Set time range (e.g., "Last 30 minutes")
4. Look for:
   - **Request** events: Workflow phases
   - **Dependency** events: Agent calls, OpenAI API calls
   - **Trace** events: Custom logs

### 2. Application Map

1. Go to **Monitoring** → **Application Map**
2. Visualize dependencies between:
   - Your application
   - Azure OpenAI Service
   - Agent executions

### 3. Performance Blade

1. Go to **Monitoring** → **Performance**
2. View:
   - Average response times for workflow phases
   - Slowest operations (which agent takes longest?)
   - P95/P99 latency percentiles

### 4. Logs (Kusto Query Language)

Navigate to **Monitoring** → **Logs** and run queries:

#### View all workflow executions
```kusto
traces
| where timestamp > ago(1h)
| where customDimensions.workflow_phase != ""
| project timestamp, workflow_phase=customDimensions.workflow_phase, student_topics=customDimensions.["student.topics"], score=customDimensions.["exam.overall_score"]
| order by timestamp desc
```

#### Find failed workflows
```kusto
traces
| where timestamp > ago(1h)
| where severityLevel >= 3
| project timestamp, message, customDimensions
| order by timestamp desc
```

#### Average assessment scores
```kusto
traces
| where timestamp > ago(24h)
| where customDimensions.["exam.overall_score"] != ""
| summarize avg_score=avg(todouble(customDimensions.["exam.overall_score"])), count=count() by bin(timestamp, 1h)
| render timechart
```

#### Agent performance comparison
```kusto
dependencies
| where timestamp > ago(1h)
| where name contains "agent"
| summarize avg_duration=avg(duration), count=count() by name
| order by avg_duration desc
```

#### Students by readiness status
```kusto
traces
| where timestamp > ago(24h)
| where customDimensions.["exam.readiness_status"] != ""
| summarize count() by tostring(customDimensions.["exam.readiness_status"])
| render piechart
```

## Disabling Observability

To disable observability (e.g., for local development without Azure):

1. Set in `.env`:
   ```bash
   ENABLE_OBSERVABILITY=false
   ```

2. Or remove the environment variable entirely

The application will continue to work normally without sending telemetry.

## Troubleshooting

### No traces appearing in Application Insights

1. **Check connection string**: Verify `APPLICATION_INSIGHTS_CONNECTION_STRING` is correct
2. **Check observability flag**: Ensure `ENABLE_OBSERVABILITY=true`
3. **Wait 1-2 minutes**: There can be a delay before traces appear
4. **Check Azure Status**: Verify Application Insights service is healthy

### Import errors

```
ImportError: No module named 'azure.monitor.opentelemetry'
```

**Solution**: Install dependencies
```bash
pip install azure-monitor-opentelemetry opentelemetry-api opentelemetry-sdk
```

### Observability disabled warning

```
[WARNING] Observability requested but packages not installed
```

**Solution**: Run `pip install -r requirements.txt`

## Custom Instrumentation (Advanced)

### Adding Custom Spans

```python
from src.utils.observability import create_custom_span

# Wrap any operation
with create_custom_span("my_operation", {"param": "value"}):
    result = do_something()
```

### Adding Custom Attributes

```python
from src.utils.observability import add_workflow_attributes

# Add context to current span
add_workflow_attributes({
    "custom.metric": 42,
    "custom.status": "success"
})
```

### Tracing Async Functions

```python
from src.utils.observability import trace_workflow_phase

@trace_workflow_phase("my_phase")
async def my_async_function():
    # Your code here
    pass
```

## Best Practices

1. **Use descriptive span names**: `quiz.generation` is better than `generate`
2. **Add relevant attributes**: Include IDs, counts, scores for better filtering
3. **Don't over-instrument**: Focus on high-level operations, not every line
4. **Set up alerts**: Create Azure Monitor alerts for:
   - High failure rates (>5%)
   - Slow response times (>30 seconds)
   - Low assessment scores (<60%)

## GenAI Semantic Conventions

MS-CertiMentor follows OpenTelemetry GenAI semantic conventions:

- **`gen_ai.system`**: "azure_openai"
- **`gen_ai.request.model`**: Model deployment name
- **`gen_ai.response.model`**: Actual model used
- **`gen_ai.request.temperature`**: Agent temperature
- **`gen_ai.usage.input_tokens`**: Prompt tokens
- **`gen_ai.usage.output_tokens`**: Completion tokens

These are automatically captured by the Agent Framework's OpenAI instrumentation.

## Resources

- [Azure Monitor OpenTelemetry](https://learn.microsoft.com/azure/azure-monitor/app/opentelemetry-enable)
- [Microsoft Agent Framework Observability](https://learn.microsoft.com/agent-framework/agents/observability)
- [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/)
- [Application Insights Overview](https://learn.microsoft.com/azure/azure-monitor/app/app-insights-overview)
