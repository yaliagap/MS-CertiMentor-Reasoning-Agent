# Azure OpenAI Setup for MS-CertiMentor

This guide will help you configure MS-CertiMentor with Azure OpenAI and Azure Key Vault.

## 📋 Prerequisites

- Active Azure subscription
- Azure OpenAI resource created
- Python 3.9+ installed
- Azure CLI installed (optional, for production)

---

## 🔧 Development Setup

### Step 1: Get Azure OpenAI Credentials

1. **Go to Azure Portal**: https://portal.azure.com
2. **Find your Azure OpenAI resource**
3. **Get the necessary information:**

   **Keys and Endpoint:**
   - Navigate to: `Your resource > Keys and Endpoint`
   - Copy:
     - `KEY 1` → This is your `AZURE_OPENAI_API_KEY`
     - `Endpoint` → This is your `AZURE_OPENAI_ENDPOINT`

   **Model Deployments:**
   - Navigate to: `Your resource > Model deployments`
   - Copy the deployment name (e.g., `gpt-4o`, `gpt-35-turbo`)
   - This is your `AZURE_OPENAI_DEPLOYMENT_NAME`

### Step 2: Configure .env File

Edit the `.env` file in the project root:

```bash
# Azure OpenAI Configuration (Development)
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Environment
ENVIRONMENT=development

# Application Settings
MAX_ASSESSMENT_ITERATIONS=3
PASSING_SCORE_THRESHOLD=0.7
DEFAULT_DAILY_STUDY_HOURS=2
DEFAULT_QUESTION_COUNT=10
```

### Step 3: Run the Project

```bash
# Install dependencies
pip install -r requirements.txt

# Test connection
python test_azure_connection.py

# Run complete workflow
python run_azure_workflow.py
```

---

## 🚀 Production Setup with Azure Key Vault

### Why Azure Key Vault?

In production, you should **NEVER** store API keys in `.env` files or in code. Azure Key Vault provides:
- ✅ Secure secret storage
- ✅ Role-based access control (RBAC)
- ✅ Secret access auditing
- ✅ Automatic key rotation

### Step 1: Create Azure Key Vault

```bash
# Login to Azure
az login

# Set variables
RESOURCE_GROUP="rg-certimentor-prod"
KEYVAULT_NAME="kv-certimentor"
LOCATION="eastus"

# Create resource group (if it doesn't exist)
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create Key Vault
az keyvault create \
  --name $KEYVAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --enable-rbac-authorization true
```

### Step 2: Store API Key in Key Vault

```bash
# Save the Azure OpenAI API key
az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name "azure-openai-key" \
  --value "YOUR_AZURE_OPENAI_API_KEY"
```

### Step 3: Configure Managed Identity

#### Option A: Azure App Service / Azure Functions

```bash
# Enable Managed Identity in your App Service
az webapp identity assign \
  --name your-app-service \
  --resource-group $RESOURCE_GROUP

# Get the Principal ID
PRINCIPAL_ID=$(az webapp identity show \
  --name your-app-service \
  --resource-group $RESOURCE_GROUP \
  --query principalId -o tsv)

# Grant permissions to the Managed Identity
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $PRINCIPAL_ID \
  --scope /subscriptions/{subscription-id}/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME
```

#### Option B: Local Development with Azure CLI

```bash
# Your current Azure CLI user will have access
USER_ID=$(az ad signed-in-user show --query id -o tsv)

az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $USER_ID \
  --scope /subscriptions/{subscription-id}/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME
```

### Step 4: Configure .env for Production

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o
AZURE_OPENAI_API_VERSION=2025-01-01-preview

# Azure Key Vault Configuration
AZURE_KEY_VAULT_NAME=kv-certimentor
AZURE_KEY_VAULT_SECRET_NAME=azure-openai-key

# Environment
ENVIRONMENT=production

# Azure Configuration
AZURE_SUBSCRIPTION_ID=your-subscription-id
AZURE_RESOURCE_GROUP=rg-certimentor-prod
```

**IMPORTANT:** Do not include `AZURE_OPENAI_API_KEY` in production. It will be retrieved from Key Vault.

### Step 5: Authentication in Production

The code uses `DefaultAzureCredential` which will attempt authentication in this order:
1. **Environment Variables** (for local development)
2. **Managed Identity** (for Azure App Service, Functions, VMs)
3. **Azure CLI** (for local development)
4. **Visual Studio Code** (if you're logged in)

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# This works automatically in both development and production
credential = DefaultAzureCredential()
vault_url = f"https://{KEYVAULT_NAME}.vault.azure.net/"
client = SecretClient(vault_url=vault_url, credential=credential)
secret = client.get_secret("azure-openai-key")
```

---

## 🔐 Security Best Practices

### ✅ DO

- ✅ Use Azure Key Vault for secrets in production
- ✅ Use Managed Identity whenever possible
- ✅ Rotate API keys regularly
- ✅ Add `.env` to `.gitignore`
- ✅ Use RBAC for granular access control
- ✅ Enable auditing in Key Vault
- ✅ Use different Key Vaults for dev/staging/prod

### ❌ DON'T

- ❌ Never commit `.env` files with secrets
- ❌ Don't share API keys via email/Slack
- ❌ Don't hardcode secrets in code
- ❌ Don't use the same API key in all environments
- ❌ Don't disable Key Vault auditing

---

## 🧪 Verify Configuration

### Development

```bash
# Test Azure connection
python test_azure_connection.py
```

Expected output:
```
[VERIFICATION] Azure OpenAI Configuration
======================================================================

1. Checking environment variables...
   ✓ ENVIRONMENT: development
   ✓ AZURE_OPENAI_ENDPOINT: https://your-resource.openai.azure.com/
   ✓ AZURE_OPENAI_DEPLOYMENT_NAME: gpt-4o
   ✓ AZURE_OPENAI_API_VERSION: 2025-01-01-preview
   ✓ AZURE_OPENAI_API_KEY: xxxxxxxx...

2. Testing Azure OpenAI connection...
   [OK] Connection successful!
   [OK] Model response: Hello

[VERIFICATION COMPLETE]
======================================================================
```

### Production (with Key Vault)

```bash
# Make sure you're logged in to Azure CLI
az login

# Verify access to Key Vault
az keyvault secret show \
  --vault-name kv-certimentor \
  --name azure-openai-key \
  --query value -o tsv

# Run the project
python run_azure_workflow.py
```

---

## 📊 Configuration Structure

```
Development:
  .env (local) → Config.AZURE_OPENAI_API_KEY → AsyncAzureOpenAI

Production:
  .env (no API key) → Config.get_api_key() → Azure Key Vault → AsyncAzureOpenAI
```

---

## 🛠️ Troubleshooting

### Error: "DefaultAzureCredential failed to retrieve a token"

**Solution:**
```bash
# Login to Azure CLI
az login

# Verify you have permissions
az keyvault secret show --vault-name kv-certimentor --name azure-openai-key
```

### Error: "AZURE_OPENAI_API_KEY is required"

**Solution:**
- Verify your `.env` file exists and contains the API key
- Make sure you're in the correct project directory
- Check for extra spaces in the `.env` file

### Error: "The specified resource does not exist"

**Solution:**
- Verify your `AZURE_OPENAI_ENDPOINT` is correct
- Make sure your `AZURE_OPENAI_DEPLOYMENT_NAME` exists in your resource
- Check that your API key is valid

### Error: "Quota exceeded"

**Solution:**
- Check your token limit in Azure Portal
- Consider using a more economical model (gpt-35-turbo)
- Request quota increase if necessary

### Error: "Cannot connect to host"

**Solution:**
- Verify your network connection
- Check firewall settings
- Ensure the Azure OpenAI resource is active

---

## 📚 Additional Resources

- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure Key Vault Documentation](https://learn.microsoft.com/azure/key-vault/)
- [Azure Identity SDK](https://learn.microsoft.com/python/api/overview/azure/identity-readme)
- [Best Practices for Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/how-to/deployment-best-practices)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)

---

## 🎯 Quick Start

**Development (5 minutes):**
1. Get your API key from Azure Portal
2. Edit `.env` with your credentials
3. `pip install -r requirements.txt`
4. `python test_azure_connection.py`
5. `python run_azure_workflow.py`

**Production (30 minutes):**
1. Create Azure Key Vault
2. Store API key in Key Vault
3. Configure Managed Identity
4. Set `ENVIRONMENT=production`
5. Deploy your application

---

## 💡 Tips for AgentsLeague Submission

- ✅ Use `.env.example` as template (included in repository)
- ✅ Never commit your actual `.env` with secrets
- ✅ Test with `test_azure_connection.py` before running full workflow
- ✅ Ensure your Azure OpenAI deployment has sufficient quota
- ✅ Use GPT-4o for best results (model used in development)

---

**Questions?** Check the documentation or open an issue on GitHub.
