#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Azure OpenAI Connection Verification Script
Tests that configuration is correct before running the full project.
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

print("\n" + "="*70)
print("[VERIFICATION] Azure OpenAI Configuration")
print("="*70 + "\n")

# Check environment variables
print("1. Checking environment variables...")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME", "gpt-4")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

print(f"   ✓ ENVIRONMENT: {ENVIRONMENT}")
print(f"   ✓ AZURE_OPENAI_ENDPOINT: {AZURE_OPENAI_ENDPOINT if AZURE_OPENAI_ENDPOINT else '❌ NOT CONFIGURED'}")
print(f"   ✓ AZURE_OPENAI_DEPLOYMENT_NAME: {AZURE_OPENAI_DEPLOYMENT}")
print(f"   ✓ AZURE_OPENAI_API_VERSION: {AZURE_OPENAI_API_VERSION}")

if ENVIRONMENT.lower() == "development":
    api_key_display = f"{AZURE_OPENAI_API_KEY[:8]}..." if AZURE_OPENAI_API_KEY else "❌ NOT CONFIGURED"
    print(f"   ✓ AZURE_OPENAI_API_KEY: {api_key_display}")
else:
    print(f"   ✓ AZURE_KEY_VAULT_NAME: {os.getenv('AZURE_KEY_VAULT_NAME', '❌ NOT CONFIGURED')}")

if not AZURE_OPENAI_API_KEY and ENVIRONMENT.lower() == "development":
    print("\n❌ ERROR: AZURE_OPENAI_API_KEY is not configured")
    print("\nPlease edit the .env file and add your API key:")
    print("   AZURE_OPENAI_API_KEY=your-api-key-here")
    print("\nGet your API key at:")
    print("   Azure Portal → Your OpenAI resource → Keys and Endpoint → KEY 1")
    exit(1)

if not AZURE_OPENAI_ENDPOINT:
    print("\n[ERROR] AZURE_OPENAI_ENDPOINT is not configured")
    print("\nPlease edit the .env file and add your endpoint:")
    print("   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/")
    print("\nGet your endpoint at:")
    print("   Azure Portal → Your OpenAI resource → Keys and Endpoint → Endpoint")
    exit(1)


# Test Azure OpenAI connection
print("\n2. Testing Azure OpenAI connection...")

try:
    from openai import AsyncAzureOpenAI

    client = AsyncAzureOpenAI(
        api_key=AZURE_OPENAI_API_KEY,
        api_version=AZURE_OPENAI_API_VERSION,
        azure_endpoint=AZURE_OPENAI_ENDPOINT
    )

    async def test_connection():
        """Test connection with a simple prompt."""
        try:
            response = await client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "Say 'Hello' in one word."}
                ],
                max_tokens=10,
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            return None, str(e)

    result = asyncio.run(test_connection())

    if isinstance(result, tuple):
        print(f"   [ERROR] Connection error: {result[1]}")
        print("\nPossible causes:")
        print("   - Invalid API key")
        print("   - Incorrect endpoint")
        print("   - Incorrect deployment name")
        print("   - Quota exceeded")
        print("\nVerify your configuration in Azure Portal")
    else:
        print(f"   [OK] Connection successful!")
        print(f"   [OK] Model response: {result}")

except ImportError as e:
    print(f"   [ERROR] Import error: {e}")
    print("\nInstall dependencies:")
    print("   pip install -r requirements.txt")
except Exception as e:
    print(f"   [ERROR] Unexpected error: {e}")

print("\n" + "="*70)
print("[VERIFICATION COMPLETE]")
print("="*70 + "\n")

if result and not isinstance(result, tuple):
    print("✅ Your Azure OpenAI configuration is working correctly!")
    print("\nYou can now run the main workflow:")
    print("   python run_azure_workflow.py")
else:
    print("❌ Please fix the configuration errors above before continuing")
