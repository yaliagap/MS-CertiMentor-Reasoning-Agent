# 🎓 MS-CertiMentor

> **Multi-Agent Reasoning System for Microsoft Certification Preparation**

A sophisticated multi-agent system that helps students prepare for Microsoft certification exams through intelligent learning path curation, personalized study planning, automated engagement, and readiness assessment.

Built for **AgentsLeague Battle #2 - Reasoning Agents** with Microsoft Foundry.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Agent Framework](https://img.shields.io/badge/Framework-Microsoft%20Agent-green.svg)](https://github.com/microsoft/agent-framework)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 🌟 Features

### Core Capabilities

✅ **Intelligent Learning Path Curation**
- Real-time integration with Microsoft Learn via MCP (Model Context Protocol)
- Priority domain identification with exam weight analysis
- Relevance scoring (1-10) for each learning path
- Module-level breakdown with importance rationale

✅ **Personalized Study Planning**
- Week-by-week structured schedules
- Daily session breakdown with specific objectives
- 4 milestone system (25%, 50%, 75%, 100%) with validation methods
- Rest days and buffer time automatically incorporated

✅ **Automated Engagement**
- Scheduled study reminders
- Motivational messaging
- Progress tracking

✅ **Readiness Assessment**
- 10-question certification-style quiz
- Difficulty distribution: 30% Easy, 50% Medium, 20% Hard
- Bloom's Taxonomy alignment
- Scenario-based questions
- Detailed explanations with Microsoft Learn references

✅ **Exam Planning**
- Certification recommendation based on performance
- Registration details and resources
- Exam day preparation tips

---

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────────────────────────────┐
│                    PREPARATION PHASE                            │
│              (Sequential Workflow - 3 Agents)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  1. Learning Path Curator               │
        │     • Searches Microsoft Learn (MCP)    │
        │     • Prioritizes domains by weight     │
        │     • Output: CuratedLearningPlan       │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  2. Study Plan Generator                │
        │     • Creates weekly schedule           │
        │     • Defines daily sessions            │
        │     • Output: StudyPlan                 │
        └─────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  3. Engagement Agent                    │
        │     • Schedules reminders               │
        │     • Sends motivational messages       │
        └─────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│              HUMAN-IN-THE-LOOP CHECKPOINT                       │
│           Student confirms readiness for assessment             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
        ┌─────────────────────────────────────────┐
        │  4. Assessment Agent                    │
        │     • Generates 10 questions            │
        │     • Evaluates student performance     │
        │     • Output: Quiz with results         │
        └─────────────────────────────────────────┘
                              ↓
                    ┌─────────┴─────────┐
                 PASS?              FAIL?
                    ↓                   ↓
        ┌───────────────────┐   Loop back to
        │  5. Exam Plan     │   Preparation
        │     Agent         │   (max 3 attempts)
        └───────────────────┘
```

### Technology Stack

- **Framework**: [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) (Python)
- **LLM Provider**: Azure OpenAI Service
- **Orchestration**: Sequential Workflows with `SequentialBuilder`
- **Model**: GPT-4o (configurable)
- **Agent Client**: `AzureOpenAIChatClient`
- **MCP Integration**: Microsoft Learn MCP Server
- **Data Validation**: Pydantic v2
- **Language**: Python 3.11+

### Agent Configuration

| Agent | Temperature | Role | Responsibilities |
|-------|-------------|------|------------------|
| **Learning Path Curator** | 0.3 | Content Discovery | Search & rank Microsoft Learn paths by relevance |
| **Study Plan Generator** | 0.4 | Planning | Create timelines, sessions, milestones (2h/day) |
| **Engagement Agent** | 0.6 | Motivation | Schedule reminders, send motivational messages |
| **Assessment Agent** | 0.2 | Evaluation | Generate quizzes, grade answers, provide feedback |
| **Exam Plan Agent** | 0.3 | Certification | Recommend exams, provide registration details |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Azure OpenAI Service resource with GPT-4o deployment
- Azure OpenAI API key and endpoint

### Installation

```bash
# Clone repository
git clone <repository-url>
cd MS-CertiMentor-Reasoning-Agent

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials
```

### Configuration

Edit `.env` with your Azure OpenAI credentials:

```bash
# Azure OpenAI Service Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Environment
ENVIRONMENT=development
```

**Get your credentials from Azure Portal:**
1. Go to your Azure OpenAI resource
2. Navigate to "Keys and Endpoint"
3. Copy KEY 1 → `AZURE_OPENAI_API_KEY`
4. Copy Endpoint → `AZURE_OPENAI_ENDPOINT`
5. Go to "Model deployments" → Copy deployment name → `AZURE_OPENAI_DEPLOYMENT_NAME`

### Verify Connection

```bash
python test_azure_connection.py
```

Expected output:
```
[OK] Connection successful!
[OK] Model response: Hello
```

---

## 🎮 Running the System

### Main Execution

```bash
python run_azure_workflow.py
```

This runs the complete multi-agent workflow with:
- ✅ Azure OpenAI Service integration
- ✅ Sequential Workflow orchestration
- ✅ All 5 specialized agents
- ✅ Interactive quiz
- ✅ Human-in-the-loop checkpoints

---

## 📊 Example Execution

```bash
$ python run_azure_workflow.py

======================================================================
[MS-CertiMentor] Multi-Agent System with Azure OpenAI
======================================================================

[MODE] Azure OpenAI Service + Sequential Workflows
[ENDPOINT] https://your-resource.openai.azure.com/
[MODEL] gpt-4o

What Microsoft certification topics are you interested in?
> Azure AI Fundamentals

Your email for reminders?
> student@example.com

======================================================================
PHASE 1: PREPARATION SUBWORKFLOW (Sequential)
======================================================================

[AGENT: LEARNING_PATH_CURATOR]
✓ 3 Microsoft Learn paths curated
  - Azure AI Fundamentals (1h)
  - Azure Machine Learning (2h)
  - NLP on Azure (1.5h)

[AGENT: STUDY_PLAN_GENERATOR]
✓ 4-week study plan created
  - 24 sessions of 2 hours
  - 4 milestones: 25%, 50%, 75%, 100%
  - Estimated completion: [date]

[AGENT: ENGAGEMENT_AGENT]
✓ 24 reminders scheduled
✓ Motivational message sent

======================================================================
PHASE 2: HUMAN-IN-THE-LOOP CHECKPOINT
======================================================================

[CHECKPOINT] Are you ready for the assessment?
> yes

======================================================================
PHASE 3: ASSESSMENT
======================================================================

[AGENT: ASSESSMENT_AGENT]
10 questions generated...

[QUIZ]
Question 1: Which Azure service is used for ML?
> B
[CORRECT]

...

Score: 80% (8/10 correct)
Status: [PASSED]

======================================================================
PHASE 4: CERTIFICATION PLANNING
======================================================================

[AGENT: EXAM_PLAN_AGENT]
✓ Recommended certification: AI-900
✓ Registration URL provided
✓ Study resources listed
✓ Exam day tips shared

[SESSION COMPLETED]
```

---

## 📁 Project Structure

```
MS-CertiMentor-Reasoning-Agent/
├── run_azure_workflow.py        # ⭐ Main entry point
├── test_azure_connection.py     # Connection verification
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
├── setup.py                      # Package setup
├── LICENSE                       # MIT License
│
├── src/
│   ├── agents/                   # Agent definitions
│   │   ├── agents_factory.py    # Agent creation factory
│   │   ├── learning_path_curator.py
│   │   ├── study_plan_generator.py
│   │   ├── engagement_agent.py
│   │   ├── assessment_agent.py
│   │   ├── exam_plan_agent.py
│   │   ├── config/
│   │   │   └── agents_config.py  # Agent configurations
│   │   └── prompts/              # Agent prompt templates
│   │       ├── learning_path_curator.txt
│   │       ├── study_plan_generator.txt
│   │       ├── engagement_agent.txt
│   │       ├── assessment_agent.txt
│   │       └── exam_plan_agent.txt
│   │
│   ├── models/                   # Pydantic data models
│   │   ├── quiz_models.py       # Quiz structured output
│   │   ├── learning_path_models.py  # Learning path data
│   │   └── study_plan_models.py # Study plan data
│   │
│   ├── tools/                    # Tool functions
│   │   ├── microsoft_learn_tools.py  # MCP integration
│   │   ├── mcp_client.py        # MCP client implementation
│   │   ├── assessment_tools.py
│   │   ├── notification_tools.py
│   │   └── study_plan_tools.py
│   │
│   ├── workflows/                # Workflow orchestration
│   │   ├── preparation_workflow.py  # Sequential subworkflow
│   │   ├── assessment_workflow.py   # Assessment execution
│   │   └── main_workflow.py     # Complete workflow
│   │
│   ├── utils/                    # Utilities
│   │   ├── state_manager.py
│   │   └── human_input.py
│   │
│   └── config.py                 # Configuration management
│
├── tests/                        # Test suite
│   └── __init__.py
│
├── data/                         # Sample data
│   └── sample_topics.json
│
├── .agents/                      # External skills
│   └── skills/
│       └── microsoft-agent-framework/
│
└── AZURE_SETUP.md               # Azure setup guide
```

---

## 🔄 Reasoning Patterns

| Pattern | Implementation | Purpose |
|---------|---------------|---------|
| **Planner-Executor** | Curator plans → Others execute | Clear role separation |
| **Sequential Orchestration** | `SequentialBuilder` | Structured agent pipeline |
| **Iterative Refinement** | Assessment loop (max 3) | Learning from failure |
| **Role-Based Specialization** | 5 distinct agents | Reduce overlap, increase quality |
| **Human-in-the-Loop** | Checkpoint before assessment | Safety & control |
| **Critic/Verifier** | Assessment Agent validation | Quality assurance |

---

## 🎓 Key Features

### ✅ Implemented

- [x] Multi-agent orchestration with Sequential Workflows
- [x] Azure OpenAI Service integration
- [x] 5 specialized agents with custom temperatures
- [x] Structured outputs using Pydantic models
- [x] Microsoft Learn MCP integration
- [x] Interactive certification-style assessments
- [x] Human approval checkpoints
- [x] Conditional routing (pass/fail branching)
- [x] Iteration limits for safety (max 3 attempts)
- [x] Personalized study plans (2h/day default)
- [x] Automated reminder scheduling (console simulation)
- [x] Detailed feedback and weak area identification

### 🔮 Future Enhancements

- [ ] Email/SMS notifications via Azure Communication Services
- [ ] Persistent state with Azure Cosmos DB
- [ ] Telemetry with Application Insights
- [ ] Web UI with React + FastAPI
- [ ] Multi-language support
- [ ] Advanced progress tracking dashboard

---

## 📊 Structured Data Models

The system uses Pydantic v2 models for structured outputs from agents:

### CuratedLearningPlan (Learning Path Curator)
```python
{
  "exam": "AI-900",
  "user_level": "beginner",
  "priority_domains": [
    {
      "domain_name": "Azure AI Services",
      "exam_weight": "30-35%",
      "priority_level": "High",
      "reason": "Core exam topic with highest weight"
    }
  ],
  "recommended_learning_paths": [
    {
      "title": "Azure AI Fundamentals",
      "url": "https://learn.microsoft.com/...",
      "estimated_hours": "8h",
      "relevance_score": 10,
      "modules": [...]
    }
  ]
}
```

### StudyPlan (Study Plan Generator)
```python
{
  "plan_title": "AI-900 Certification Study Plan",
  "total_duration_weeks": 4,
  "daily_hours_target": 2.0,
  "weeks": [
    {
      "week_number": 1,
      "week_theme": "Azure AI Fundamentals",
      "sessions": [...]
    }
  ],
  "milestones": [
    {"percentage": 25, "week_number": 1, "description": "..."},
    {"percentage": 50, "week_number": 2, "description": "..."},
    {"percentage": 75, "week_number": 3, "description": "..."},
    {"percentage": 100, "week_number": 4, "description": "..."}
  ]
}
```

### Quiz (Assessment Agent)
```python
{
  "total_questions": 10,
  "difficulty_distribution": {"easy": 3, "medium": 5, "hard": 2},
  "questions": [
    {
      "question_number": 1,
      "question_text": "...",
      "options": ["A", "B", "C", "D"],
      "correct_answer": "B",
      "difficulty": "medium",
      "bloom_level": "apply",
      "explanation": "...",
      "microsoft_learn_reference": "https://..."
    }
  ]
}
```

---

## 🔧 MCP Integration

The system integrates with Microsoft Learn via the Model Context Protocol (MCP):

**Endpoints Used:**
- `search_learning_paths` - Search for relevant learning paths
- `get_module_details` - Fetch detailed module information
- `search_certifications` - Find certification exams

**MCP Client:** `src/tools/mcp_client.py`
- JSON-RPC 2.0 over HTTP
- Server-Sent Events (SSE) support
- Automatic retry with exponential backoff
- Error handling and fallback mechanisms

---

## 📊 Evaluation Criteria (AgentsLeague)

| Criterion | Weight | Implementation |
|-----------|--------|---------------|
| **Accuracy & Relevance** | 25% | Relevant paths, proper exam recommendations |
| **Reasoning & Multi-step Thinking** | 25% | Sequential workflow, clear agent collaboration |
| **Reliability & Safety** | 20% | Iteration limits, human checkpoints, error handling |
| **User Experience** | 15% | Polished CLI, clear output, interactive quiz |
| **Creativity** | 15% | Iterative refinement, temperature tuning, engagement |

---

## 🛡️ Responsible AI

- ✅ Human approval required before assessment
- ✅ Maximum 3 assessment attempts (prevents infinite loops)
- ✅ Objective 70% passing threshold
- ✅ Constructive feedback on failures
- ✅ Educational focus only (no exam dumps)
- ✅ Privacy-conscious (console-only notifications in MVP)

---

## 🧪 Testing

### Test Connection

```bash
python test_azure_connection.py
```

### Run Test Suite

```bash
pytest tests/ -v
```

---

## 🐛 Troubleshooting

### "Cannot connect to host"
- Verify `AZURE_OPENAI_ENDPOINT` is correct
- Check firewall/network settings
- Ensure Azure OpenAI resource is active

### "API key invalid"
- Regenerate key in Azure Portal
- Copy KEY 1 (not KEY 2)
- Remove any extra spaces from `.env` file

### "Deployment not found"
- Verify deployment name in Azure Portal → Model deployments
- Ensure model is deployed (not just available)

### "Module not found"
- Run `pip install -r requirements.txt`
- Ensure Python 3.9+ is installed
- Consider using a virtual environment

---

## 🙏 Acknowledgments

- **Microsoft Agent Framework** - Agent orchestration framework
- **Azure OpenAI Service** - LLM inference
- **Microsoft Learn** - Certification content and MCP server
- **AgentsLeague** - Challenge platform and community

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

This project is developed for the AgentsLeague Battle #2 challenge.

---

**Status**: ✅ Fully Functional | **Track**: Reasoning Agents | **Platform**: Microsoft Agent Framework

**Demo Video**: [Coming soon]

**Date**: February 2026
**Challenge**: AgentsLeague Battle #2 - Reasoning Agents with Microsoft Foundry
