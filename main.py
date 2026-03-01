#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MS-CertiMentor - Azure OpenAI with Sequential Workflows
Main entry point for the multi-agent certification preparation system.
"""
import asyncio
import sys
import os

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import agent factory and workflow orchestration
from src.agents.agents_factory import create_all_agents
from src.workflows.main_workflow import run_complete_workflow

# Import observability configuration
try:
    from azure.monitor.opentelemetry import configure_azure_monitor
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    OBSERVABILITY_AVAILABLE = True
except ImportError:
    OBSERVABILITY_AVAILABLE = False
    print("[WARNING] Observability packages not installed. Run: pip install azure-monitor-opentelemetry")


def validate_configuration():
    """Validate that required environment variables are set."""
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
    api_key = os.getenv("AZURE_OPENAI_API_KEY", "")

    if not endpoint or not api_key:
        print("\n" + "="*70)
        print("[ERROR] Incomplete configuration!")
        print("="*70)
        print("\nMake sure you have these variables in .env:")
        print("  AZURE_OPENAI_ENDPOINT=https://xxx.openai.azure.com/")
        print("  AZURE_OPENAI_API_KEY=your-api-key")
        print("  AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o")
        print("\nTo get these credentials:")
        print("  1. Azure Portal -> Your OpenAI resource")
        print("  2. Keys and Endpoint -> Copy KEY 1 and Endpoint")
        print("  3. Model deployments -> Note the deployment name")
        print("\nOr run: python test_azure_connection.py")
        print("="*70 + "\n")
        return False

    return True


def setup_observability():
    """
    Configure Azure Monitor Application Insights for observability.

    This enables automatic tracing of:
    - Agent execution spans
    - Tool calls and results
    - Model API calls (Azure OpenAI)
    - Workflow orchestration steps

    Traces are sent to Azure Application Insights for monitoring and analysis.
    """
    # Check if observability is enabled
    enable_obs = os.getenv("ENABLE_OBSERVABILITY", "false").lower() == "true"

    if not enable_obs:
        print("[INFO] Observability is disabled (ENABLE_OBSERVABILITY=false)")
        return False

    if not OBSERVABILITY_AVAILABLE:
        print("[WARNING] Observability requested but packages not installed")
        print("         Run: pip install azure-monitor-opentelemetry")
        return False

    # Get Application Insights connection string
    connection_string = os.getenv("APPLICATION_INSIGHTS_CONNECTION_STRING", "")

    if not connection_string or connection_string == "your-application-insights-connection-string":
        print("[WARNING] APPLICATION_INSIGHTS_CONNECTION_STRING not configured")
        print("          Observability disabled. Add connection string to .env file")
        return False

    try:
        print("\n" + "="*70)
        print("[OBSERVABILITY] Configuring Azure Application Insights")
        print("="*70)

        # Configure Azure Monitor with Application Insights
        configure_azure_monitor(
            connection_string=connection_string,
            # Enable auto-instrumentation for HTTP, OpenAI, and other libraries
            enable_live_metrics=True,
            logger_name="ms-certimentor"
        )

        print("✓ Azure Monitor configured successfully")
        print("✓ Traces and spans will be sent to Application Insights")
        print("✓ View telemetry in Azure Portal -> Application Insights -> Transaction search")
        print("="*70 + "\n")

        return True

    except Exception as e:
        print(f"[ERROR] Failed to configure observability: {e}")
        print("        Continuing without observability...")
        return False


async def main():
    """Main entry point."""
    # Validate configuration
    if not validate_configuration():
        return

    # Setup observability (Azure Application Insights)
    observability_enabled = setup_observability()

    try:
        # Create all 6 specialized agents
        print("\n[SETUP] Creating 6 specialized agents...")
        agents = create_all_agents()

        # Get configuration for banner
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
        model = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4o")

        # Run complete workflow
        await run_complete_workflow(agents, endpoint, model)

    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Workflow stopped by user.")
    except Exception as e:
        print(f"\n[ERROR] Error during execution: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
