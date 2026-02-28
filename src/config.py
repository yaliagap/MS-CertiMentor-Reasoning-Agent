"""
Configuration management for MS-CertiMentor system.
Loads settings from environment variables and Azure Key Vault.
"""
import os
from dotenv import load_dotenv
from typing import Optional
from azure.core.credentials import AccessToken, TokenCredential
from datetime import datetime, timedelta

# Load environment variables
load_dotenv()


class StaticTokenCredential(TokenCredential):
    """
    TokenCredential implementation that uses a static API key as token.
    This allows using Azure AI Foundry with a fixed token instead of AzureCliCredential.
    """

    def __init__(self, token: str):
        """
        Initialize with a static token.

        Args:
            token: The API key or token to use
        """
        self._token = token

    def get_token(self, *scopes, **kwargs) -> AccessToken:
        """
        Get the access token.

        Returns:
            AccessToken with the static token
        """
        # Token expires in 1 hour (this is just for compatibility)
        expires_on = int((datetime.now() + timedelta(hours=1)).timestamp())
        return AccessToken(self._token, expires_on)


class Config:
    """Central configuration class for the application."""

    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    # Azure AI Foundry Settings (New approach)
    AZURE_AI_PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "")
    AZURE_AI_MODEL_DEPLOYMENT_NAME = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME", "gpt-4o")
    AZURE_AI_PROJECT_TOKEN = os.getenv("AZURE_AI_PROJECT_TOKEN", "")

    # Azure AI Project Settings (Legacy)
    AZURE_AI_PROJECT_CONNECTION_STRING = os.getenv("AZURE_AI_PROJECT_CONNECTION_STRING", "")
    AZURE_SUBSCRIPTION_ID = os.getenv("AZURE_SUBSCRIPTION_ID", "")
    AZURE_RESOURCE_GROUP = os.getenv("AZURE_RESOURCE_GROUP", "")
    AZURE_AI_PROJECT_NAME = os.getenv("AZURE_AI_PROJECT_NAME", "")

    # Azure Key Vault Settings (Production)
    AZURE_KEY_VAULT_NAME = os.getenv("AZURE_KEY_VAULT_NAME", "")
    AZURE_KEY_VAULT_SECRET_NAME = os.getenv("AZURE_KEY_VAULT_SECRET_NAME", "azure-open-ai-key")

    # Microsoft Learn MCP Settings
    MCP_ENDPOINT = os.getenv("MCP_ENDPOINT", "https://learn.microsoft.com/api/mcp")

    # Application Settings
    MAX_ASSESSMENT_ITERATIONS = int(os.getenv("MAX_ASSESSMENT_ITERATIONS", "3"))
    PASSING_SCORE_THRESHOLD = float(os.getenv("PASSING_SCORE_THRESHOLD", "0.7"))
    DEFAULT_DAILY_STUDY_HOURS = int(os.getenv("DEFAULT_DAILY_STUDY_HOURS", "2"))
    DEFAULT_QUESTION_COUNT = int(os.getenv("DEFAULT_QUESTION_COUNT", "10"))

    # Simulation Settings (for console output)
    SIMULATE_NOTIFICATIONS = True

    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production environment."""
        return cls.ENVIRONMENT.lower() == "production"

    @classmethod
    def get_token_credential(cls) -> TokenCredential:
        """
        Get TokenCredential based on environment.
        Development: Use StaticTokenCredential with token from .env
        Production: Use token from Azure Key Vault

        Returns:
            TokenCredential instance
        """
        token = cls.get_project_token()
        return StaticTokenCredential(token)

    @classmethod
    def get_project_token(cls) -> str:
        """
        Get project token based on environment.
        Development: Load from .env
        Production: Load from Azure Key Vault

        Returns:
            API token/key
        """
        if cls.is_production():
            return cls._get_token_from_keyvault()
        else:
            if not cls.AZURE_AI_PROJECT_TOKEN:
                raise ValueError(
                    "AZURE_AI_PROJECT_TOKEN not found in .env file. "
                    "Please add your Azure AI token to .env"
                )
            return cls.AZURE_AI_PROJECT_TOKEN

    @classmethod
    def _get_token_from_keyvault(cls) -> str:
        """Get token from Azure Key Vault (production only)."""
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient

            if not cls.AZURE_KEY_VAULT_NAME:
                raise ValueError("AZURE_KEY_VAULT_NAME not configured for production")

            # Create Key Vault client
            credential = DefaultAzureCredential()
            vault_url = f"https://{cls.AZURE_KEY_VAULT_NAME}.vault.azure.net/"
            client = SecretClient(vault_url=vault_url, credential=credential)

            # Get secret
            secret = client.get_secret(cls.AZURE_KEY_VAULT_SECRET_NAME)
            return secret.value

        except ImportError:
            raise ImportError(
                "Azure SDK packages required for production. Install with: "
                "pip install azure-identity azure-keyvault-secrets"
            )
        except Exception as e:
            raise RuntimeError(f"Failed to retrieve token from Key Vault: {e}")

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        # Check environment
        if cls.is_production():
            # Production: Validate Key Vault configuration
            if not cls.AZURE_KEY_VAULT_NAME:
                raise ValueError(
                    "Production environment requires AZURE_KEY_VAULT_NAME to be set"
                )
            print(f"[CONFIG] Running in PRODUCTION mode with Azure Key Vault")
        else:
            # Development: Validate Azure AI Foundry configuration
            if not cls.AZURE_AI_PROJECT_ENDPOINT:
                raise ValueError(
                    "Development environment requires AZURE_AI_PROJECT_ENDPOINT in .env file\n"
                    "Format: https://<your-project>.services.ai.azure.com/api/projects/<project-id>"
                )
            if not cls.AZURE_AI_PROJECT_TOKEN:
                raise ValueError(
                    "Development environment requires AZURE_AI_PROJECT_TOKEN in .env file"
                )
            print(f"[CONFIG] Running in DEVELOPMENT mode with Azure AI Foundry")
            print(f"[CONFIG] Endpoint: {cls.AZURE_AI_PROJECT_ENDPOINT}")
            print(f"[CONFIG] Model: {cls.AZURE_AI_MODEL_DEPLOYMENT_NAME}")

        return True


# Validate configuration on import
try:
    Config.validate()
except ValueError as e:
    print(f"\n[WARNING] Configuration validation failed: {e}")
    print("[INFO] Some features may not work without proper configuration\n")
