# Common Patterns for Secret Vault

This document provides practical examples and best practices for using the `/secret-vault` skill in your AI agent workflows.

## Table of Contents

- [Basic Operations](#basic-operations)
- [Agent Integration Patterns](#agent-integration-patterns)
- [Secret Organization](#secret-organization)
- [Security Best Practices](#security-best-practices)
- [Troubleshooting](#troubleshooting)

## Basic Operations

### Initial Setup and Verification

```bash
# Check if authentication is configured
/secret-vault auth-status

# If not configured, run the setup script
cd /Users/jinjingzhou/joezhoujinjing/skills/secret-vault
./scripts/setup-local.sh
```

### Creating Secrets

```bash
# Create an API key for an agent
/secret-vault set agents/chatbot/openai-api-key "sk-proj-..."

# Create database credentials
/secret-vault set agents/database/connection-string "postgresql://user:pass@host:5432/db"

# Create shared service account credentials
/secret-vault set shared/gcp/service-account-key "{ ... JSON key ... }"

# Create email credentials
/secret-vault set agents/email/smtp-password "your-smtp-password"
```

### Reading Secrets

```bash
# Read a specific secret
/secret-vault get agents/chatbot/openai-api-key

# Read and use in a command (example)
API_KEY=$(/secret-vault get agents/chatbot/openai-api-key)
```

### Listing Secrets

```bash
# List all secrets
/secret-vault list

# List secrets for all agents
/secret-vault list agents/

# List secrets for a specific agent component
/secret-vault list agents/chatbot/

# List shared secrets
/secret-vault list shared/
```

### Updating Secrets

```bash
# Rotate an API key (creates a new version)
/secret-vault set agents/chatbot/openai-api-key "sk-proj-NEW-KEY..."

# Note: Old versions are preserved in Secret Manager
# You can access previous versions if needed
```

### Deleting Secrets

```bash
# Delete an old/unused secret (requires confirmation)
/secret-vault delete agents/old-service/deprecated-key

# CAUTION: This is irreversible and deletes all versions
```

## Agent Integration Patterns

### Pattern 1: API Client Initialization

When an agent needs to call an external API:

```markdown
1. Agent starts and needs OpenAI API access
2. Use /secret-vault get agents/chatbot/openai-api-key
3. Initialize the API client with the retrieved key
4. Make API calls
```

Example agent workflow:

```bash
# Step 1: Retrieve the API key
API_KEY=$(/secret-vault get agents/api-client/openai-key)

# Step 2: Use it in your application
curl https://api.openai.com/v1/chat/completions \
  -H "Authorization: Bearer $API_KEY" \
  -d '{"model": "gpt-4", "messages": [...]}'
```

### Pattern 2: Database Connection

For agents that need database access:

```bash
# Store the connection string
/secret-vault set agents/database/postgres-url "postgresql://user:pass@localhost:5432/mydb"

# Retrieve and use
DB_URL=$(/secret-vault get agents/database/postgres-url)
psql "$DB_URL" -c "SELECT * FROM users"
```

### Pattern 3: Multi-Service Agent

An agent that needs multiple secrets:

```bash
# Store different service credentials
/secret-vault set agents/multi-service/github-token "ghp_..."
/secret-vault set agents/multi-service/slack-webhook "https://hooks.slack.com/..."
/secret-vault set agents/multi-service/aws-access-key "AKIA..."

# Agent retrieves all needed secrets at startup
GITHUB_TOKEN=$(/secret-vault get agents/multi-service/github-token)
SLACK_WEBHOOK=$(/secret-vault get agents/multi-service/slack-webhook)
AWS_KEY=$(/secret-vault get agents/multi-service/aws-access-key)
```

### Pattern 4: Dynamic Secret Provisioning

Create secrets on-demand for new agent instances:

```bash
# Agent requests creation of new credentials
/secret-vault set agents/instance-123/session-token "temp-token-xyz"

# Use the credentials
TOKEN=$(/secret-vault get agents/instance-123/session-token)

# Clean up when agent is done
/secret-vault delete agents/instance-123/session-token
```

### Pattern 5: Shared Secrets Across Agents

For secrets used by multiple agents:

```bash
# Store in shared namespace
/secret-vault set shared/services/email-smtp-password "password123"
/secret-vault set shared/services/monitoring-api-key "mon-key-456"

# Multiple agents can access
/secret-vault get shared/services/email-smtp-password
```

## Secret Organization

### Recommended Structure

```
agents/                          # Agent-specific secrets
  ├── chatbot/
  │   ├── openai-api-key
  │   ├── anthropic-api-key
  │   └── session-encryption-key
  ├── database/
  │   ├── postgres-url
  │   ├── redis-password
  │   └── backup-credentials
  ├── api-client/
  │   ├── github-token
  │   ├── gitlab-token
  │   └── jira-api-key
  └── email/
      ├── smtp-password
      └── sendgrid-api-key

shared/                          # Shared across multiple agents
  ├── gcp/
  │   ├── service-account-key
  │   └── storage-credentials
  ├── services/
  │   ├── monitoring-api-key
  │   └── logging-endpoint
  └── infrastructure/
      ├── kubernetes-config
      └── vault-token

test/                            # Test/development secrets
  └── example/
      └── test-api-key
```

### Naming Guidelines

**DO:**

- ✅ Use lowercase with hyphens: `api-key`, `service-account`
- ✅ Be descriptive: `openai-api-key` not `key1`
- ✅ Follow the pattern: `{service}/{component}/{secret-type}`
- ✅ Group related secrets: `agents/chatbot/*`

**DON'T:**

- ❌ Use spaces or special characters: `my secret key`
- ❌ Use generic names: `secret1`, `password`
- ❌ Mix naming styles: `camelCase`, `snake_case`
- ❌ Include sensitive info in names: `password-abc123`

## Security Best Practices

### 1. Never Log Secret Values

**BAD:**

```bash
SECRET=$(/secret-vault get agents/api-key)
echo "Retrieved secret: $SECRET"  # NEVER DO THIS
```

**GOOD:**

```bash
SECRET=$(/secret-vault get agents/api-key)
echo "✓ Successfully retrieved secret: agents/api-key"
```

### 2. Use Least Privilege Access

Only grant the minimum required permissions:

```bash
# Read-only access for most agents
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:agent@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"

# Full access only for admin agents
gcloud projects add-iam-policy-binding PROJECT_ID \
  --member="serviceAccount:admin@project.iam.gserviceaccount.com" \
  --role="roles/secretmanager.admin"
```

### 3. Rotate Secrets Regularly

```bash
# Example: Monthly API key rotation
# Old key still works during transition
/secret-vault set agents/api-client/github-token "new-token-xyz"

# Update agents to use new version
# Test thoroughly

# Old versions remain accessible if needed
```

### 4. Use Descriptive Names (Not Values)

**BAD:**

```bash
/secret-vault set agents/prod-db "password123"  # Leaks environment
```

**GOOD:**

```bash
# Keep environment in project structure, not secret names
/secret-vault set agents/database/password "password123"
```

### 5. Validate Before Deletion

Always verify before deleting:

```bash
# Check what would be deleted
/secret-vault get agents/old-service/key

# Confirm it's not in use
/secret-vault list agents/old-service/

# Then delete with caution
/secret-vault delete agents/old-service/key
```

### 6. Audit Secret Access

Monitor who accesses secrets:

```bash
# View audit logs in Cloud Console or via gcloud
gcloud logging read "resource.type=secretmanager_secret" \
  --limit=50 \
  --format=json
```

### 7. Separate Environments

If you add multiple environments later:

```bash
# Use different GCP projects per environment
# OR prefix secret names:
/secret-vault set prod/agents/api-key "..."
/secret-vault set staging/agents/api-key "..."
/secret-vault set dev/agents/api-key "..."
```

## Troubleshooting

### Error: gcloud not found

```bash
# Install Google Cloud SDK
# macOS: brew install google-cloud-sdk
# Or visit: https://cloud.google.com/sdk/docs/install
```

### Error: Application Default Credentials not configured

```bash
# Configure ADC
gcloud auth application-default login

# Or set service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
```

### Error: Permission denied

```bash
# Check your IAM permissions
gcloud projects get-iam-policy PROJECT_ID \
  --flatten="bindings[].members" \
  --filter="bindings.members:user:YOUR_EMAIL"

# You need one of:
# - roles/secretmanager.secretAccessor (read)
# - roles/secretmanager.admin (full access)
```

### Error: Secret not found

```bash
# Verify the secret name
/secret-vault list

# Check for typos in the name
/secret-vault list agents/

# Create it if it doesn't exist
/secret-vault set agents/component/secret-name "value"
```

### Error: API not enabled

```bash
# Enable Secret Manager API
gcloud services enable secretmanager.googleapis.com --project=PROJECT_ID
```

### Secret Manager quota exceeded

```bash
# Check quotas in Cloud Console
# Secrets Manager -> Quotas
# Contact Google Cloud support to increase limits
```

## Advanced Patterns

### Secret Templating

Create multiple similar secrets:

```bash
# For multiple agent instances
for i in {1..5}; do
  /secret-vault set agents/instance-$i/session-token "token-$i-$(date +%s)"
done
```

### Conditional Secret Access

Only access secrets when needed:

```bash
# Check if secret exists before trying to use it
if /secret-vault list agents/optional-service/ | grep -q api-key; then
  API_KEY=$(/secret-vault get agents/optional-service/api-key)
  # Use API key
else
  echo "Optional service not configured, skipping..."
fi
```

### Secret Backup Pattern

While Secret Manager handles versioning automatically, you might want to export for disaster recovery:

```bash
# List all secrets for backup reference (NOT THE VALUES!)
/secret-vault list > secrets-inventory-$(date +%Y%m%d).txt

# Never export actual secret values to files
# Use Secret Manager's built-in versioning instead
```

## Summary

The `/secret-vault` skill provides secure, scalable secret management for your AI agents. Key takeaways:

- **Organize** secrets using the `{service}/{component}/{secret-type}` pattern
- **Secure** secrets by never logging values and using least privilege access
- **Rotate** secrets regularly and leverage automatic versioning
- **Monitor** secret access through Cloud Logging audit trails
- **Validate** operations, especially before deletions
- **Document** your secret organization for team collaboration

For more details, see [SKILL.md](../SKILL.md).
