---
name: secret-vault
description: Access Google Secret Manager to securely retrieve, list, create, update, and delete secrets. Use this when you need to fetch API keys, database credentials, or other sensitive configuration values stored in Google Cloud Secret Manager. Requires gcloud authentication and Secret Manager permissions.
---

# Google Secret Manager Skill

Securely access Google Secret Manager for AI agents.

## Quick Setup

```bash
# Local: Configure Application Default Credentials
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID

# Cloud (GKE/Cloud Run): Uses workload identity automatically
```

## Naming Convention

Pattern: `{service}-{component}-{secret-type}` (hyphen-separated)

Google Secret Manager requires names to match `[a-zA-Z_0-9]+` (letters, numbers, underscores, hyphens only - no slashes).

Examples:

- `agents-api-client-openai-key`
- `agents-database-connection-string`
- `shared-godaddy-dns-api-key`
- `shared-gcp-service-account-key`

## Commands

### `/secret-vault auth-status`

Check authentication setup and current GCP project.

```bash
bash scripts/check-auth.sh
```

### `/secret-vault get <name>`

Retrieve secret value. Never log the value, only the name.

```bash
gcloud secrets versions access latest --secret="<name>"
```

Example:

```bash
/secret-vault get agents-api-client-openai-key
```

### `/secret-vault list [prefix]`

List secrets, optionally filtered by prefix.

```bash
# All secrets
gcloud secrets list --format="table(name,createTime,updateTime)"

# With prefix filter (using grep)
gcloud secrets list --format="table(name,createTime,updateTime)" | grep "<prefix>"
```

Examples:

```bash
/secret-vault list
/secret-vault list agents-
/secret-vault list nexus-hub
/secret-vault list shared-godaddy
```

### `/secret-vault set <name> <value>`

Create or update a secret. Always confirm with user before executing.

```bash
# Validate naming: must match ^[a-zA-Z_0-9-]+$ (no slashes allowed)

# Check if exists, then create or update
if gcloud secrets describe "<name>" &>/dev/null; then
    echo -n "<value>" | gcloud secrets versions add "<name>" --data-file=-
else
    echo -n "<value>" | gcloud secrets create "<name>" --data-file=-
fi
```

Example:

```bash
/secret-vault set agents-api-client-openai-key "sk-..."
/secret-vault set shared-godaddy-dns-api-key "your-api-key"
```

### `/secret-vault delete <name>`

Permanently delete a secret (irreversible). Require strong user confirmation.

```bash
gcloud secrets delete "<name>" --quiet
```

## Required Permissions

- `roles/secretmanager.secretAccessor` (read)
- `roles/secretmanager.secretVersionAdder` (update)
- `roles/secretmanager.admin` (create/delete)

## Details

See [examples/common-patterns.md](examples/common-patterns.md) for usage patterns and best practices.
