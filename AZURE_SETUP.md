# Configuración de Azure OpenAI para MS-CertiMentor

Esta guía te ayudará a configurar MS-CertiMentor con Azure OpenAI y Azure Key Vault.

## 📋 Requisitos Previos

- Suscripción activa de Azure
- Recurso de Azure OpenAI creado
- Python 3.9+ instalado
- Azure CLI instalado (opcional, para producción)

---

## 🔧 Configuración de Desarrollo

### Paso 1: Obtener credenciales de Azure OpenAI

1. **Ir a Azure Portal**: https://portal.azure.com
2. **Buscar tu recurso de Azure OpenAI**
3. **Obtener la información necesaria:**

   **Keys and Endpoint:**
   - Navega a: `Tu recurso > Keys and Endpoint`
   - Copia:
     - `KEY 1` → Esta es tu `AZURE_OPENAI_API_KEY`
     - `Endpoint` → Este es tu `AZURE_OPENAI_ENDPOINT`

   **Model Deployments:**
   - Navega a: `Tu recurso > Model deployments`
   - Copia el nombre del deployment (ej: `gpt-4`, `gpt-35-turbo`)
   - Este es tu `AZURE_OPENAI_DEPLOYMENT_NAME`

### Paso 2: Configurar archivo .env

Edita el archivo `.env` en la raíz del proyecto:

```bash
# Azure OpenAI Configuration (Development)
AZURE_OPENAI_API_KEY=tu-api-key-aqui
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure AI Project Configuration (opcional para desarrollo)
AZURE_AI_PROJECT_CONNECTION_STRING=
AZURE_SUBSCRIPTION_ID=tu-subscription-id
AZURE_RESOURCE_GROUP=tu-resource-group
AZURE_AI_PROJECT_NAME=MS-CertiMentor

# Environment
ENVIRONMENT=development

# Application Settings
MAX_ASSESSMENT_ITERATIONS=3
PASSING_SCORE_THRESHOLD=0.7
DEFAULT_DAILY_STUDY_HOURS=2
DEFAULT_QUESTION_COUNT=10
```

### Paso 3: Ejecutar el proyecto

```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar proyecto real con Azure OpenAI
python run_real_project.py
```

---

## 🚀 Configuración de Producción con Azure Key Vault

### ¿Por qué Azure Key Vault?

En producción, **NO debes** almacenar API keys en archivos `.env` ni en código. Azure Key Vault proporciona:
- ✅ Almacenamiento seguro de secretos
- ✅ Control de acceso basado en roles (RBAC)
- ✅ Auditoría de acceso a secretos
- ✅ Rotación automática de claves

### Paso 1: Crear Azure Key Vault

```bash
# Login a Azure
az login

# Configurar variables
RESOURCE_GROUP="rg-certimentor-prod"
KEYVAULT_NAME="kv-certimentor"
LOCATION="eastus"

# Crear resource group (si no existe)
az group create --name $RESOURCE_GROUP --location $LOCATION

# Crear Key Vault
az keyvault create \
  --name $KEYVAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --enable-rbac-authorization true
```

### Paso 2: Almacenar API Key en Key Vault

```bash
# Guardar la API key de Azure OpenAI
az keyvault secret set \
  --vault-name $KEYVAULT_NAME \
  --name "azure-open-ai-key" \
  --value "TU_API_KEY_DE_AZURE_OPENAI"
```

### Paso 3: Configurar Managed Identity

#### Opción A: Azure App Service / Azure Functions

```bash
# Habilitar Managed Identity en tu App Service
az webapp identity assign \
  --name tu-app-service \
  --resource-group $RESOURCE_GROUP

# Obtener el Principal ID
PRINCIPAL_ID=$(az webapp identity show \
  --name tu-app-service \
  --resource-group $RESOURCE_GROUP \
  --query principalId -o tsv)

# Dar permisos a la Managed Identity
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $PRINCIPAL_ID \
  --scope /subscriptions/{subscription-id}/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME
```

#### Opción B: Desarrollo local con Azure CLI

```bash
# Tu usuario actual de Azure CLI tendrá acceso
USER_ID=$(az ad signed-in-user show --query id -o tsv)

az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $USER_ID \
  --scope /subscriptions/{subscription-id}/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$KEYVAULT_NAME
```

### Paso 4: Configurar .env para Producción

```bash
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://tu-recurso.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Azure Key Vault Configuration
AZURE_KEY_VAULT_NAME=kv-certimentor
AZURE_KEY_VAULT_SECRET_NAME=azure-open-ai-key

# Environment
ENVIRONMENT=production

# Azure AI Project Configuration
AZURE_SUBSCRIPTION_ID=tu-subscription-id
AZURE_RESOURCE_GROUP=rg-certimentor-prod
```

**IMPORTANTE:** No incluyas `AZURE_OPENAI_API_KEY` en producción. Se obtendrá de Key Vault.

### Paso 5: Autenticación en Producción

El código usa `DefaultAzureCredential` que intentará autenticarse en este orden:
1. **Environment Variables** (para desarrollo local)
2. **Managed Identity** (para Azure App Service, Functions, VMs)
3. **Azure CLI** (para desarrollo local)
4. **Visual Studio Code** (si estás logueado)

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Esto funciona automáticamente en desarrollo y producción
credential = DefaultAzureCredential()
vault_url = f"https://{KEYVAULT_NAME}.vault.azure.net/"
client = SecretClient(vault_url=vault_url, credential=credential)
secret = client.get_secret("azure-open-ai-key")
```

---

## 🔐 Mejores Prácticas de Seguridad

### ✅ Hacer (DO)

- ✅ Usar Azure Key Vault para secretos en producción
- ✅ Usar Managed Identity cuando sea posible
- ✅ Rotar API keys regularmente
- ✅ Agregar `.env` al `.gitignore`
- ✅ Usar RBAC para control de acceso granular
- ✅ Habilitar auditoría en Key Vault
- ✅ Usar diferentes Key Vaults para dev/staging/prod

### ❌ No Hacer (DON'T)

- ❌ Nunca commitear archivos `.env` con secretos
- ❌ No compartir API keys por email/Slack
- ❌ No hardcodear secrets en el código
- ❌ No usar la misma API key en todos los ambientes
- ❌ No deshabilitar la auditoría de Key Vault

---

## 🧪 Verificar Configuración

### Desarrollo

```bash
python -c "from src.config import Config; print(f'Environment: {Config.ENVIRONMENT}'); print(f'Endpoint: {Config.AZURE_OPENAI_ENDPOINT}'); print('✓ Configuration OK')"
```

### Producción (con Key Vault)

```bash
# Asegúrate de estar logueado en Azure CLI
az login

# Verificar acceso a Key Vault
az keyvault secret show \
  --vault-name kv-certimentor \
  --name azure-open-ai-key \
  --query value -o tsv

# Ejecutar proyecto
python run_real_project.py
```

---

## 📊 Estructura de Configuración

```
Desarrollo:
  .env (local) → Config.AZURE_OPENAI_API_KEY → AsyncAzureOpenAI

Producción:
  .env (sin API key) → Config.get_api_key() → Azure Key Vault → AsyncAzureOpenAI
```

---

## 🛠️ Troubleshooting

### Error: "DefaultAzureCredential failed to retrieve a token"

**Solución:**
```bash
# Loguéate en Azure CLI
az login

# Verifica que tengas permisos
az keyvault secret show --vault-name kv-certimentor --name azure-open-ai-key
```

### Error: "AZURE_OPENAI_API_KEY is required"

**Solución:**
- Verifica que tu archivo `.env` exista y tenga la API key
- Asegúrate de que estás en el directorio correcto del proyecto
- Revisa que no haya espacios extras en el archivo `.env`

### Error: "The specified resource does not exist"

**Solución:**
- Verifica que tu `AZURE_OPENAI_ENDPOINT` sea correcto
- Asegúrate de que tu `AZURE_OPENAI_DEPLOYMENT_NAME` exista en tu recurso
- Revisa que tu API key sea válida

### Error: "Quota exceeded"

**Solución:**
- Verifica tu límite de tokens en Azure Portal
- Considera usar un modelo más económico (gpt-35-turbo)
- Solicita aumento de cuota si es necesario

---

## 📚 Recursos Adicionales

- [Azure OpenAI Service Documentation](https://learn.microsoft.com/azure/ai-services/openai/)
- [Azure Key Vault Documentation](https://learn.microsoft.com/azure/key-vault/)
- [Azure Identity SDK](https://learn.microsoft.com/python/api/overview/azure/identity-readme)
- [Best Practices for Azure OpenAI](https://learn.microsoft.com/azure/ai-services/openai/how-to/deployment-best-practices)

---

## 🎯 Quick Start

**Desarrollo (5 minutos):**
1. Obtén tu API key de Azure Portal
2. Edita `.env` con tus credenciales
3. `pip install -r requirements.txt`
4. `python run_real_project.py`

**Producción (30 minutos):**
1. Crea Azure Key Vault
2. Almacena API key en Key Vault
3. Configura Managed Identity
4. Establece `ENVIRONMENT=production`
5. Deploy tu aplicación

---

**¿Preguntas?** Revisa la documentación o abre un issue en GitHub.
