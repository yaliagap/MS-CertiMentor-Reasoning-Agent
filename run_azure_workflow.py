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


async def main():
    """Main entry point."""
    # Validate configuration
    if not validate_configuration():
        return

    try:
        # Create all 5 specialized agents
        print("\n[SETUP] Creating 5 specialized agents...")
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
